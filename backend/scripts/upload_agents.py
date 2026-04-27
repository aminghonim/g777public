"""Upload all agency agents to Pinecone for semantic routing."""
import os
import sys
import logging
import yaml
import time

logger = logging.getLogger(__name__)

# Pinecone SDK
try:
    from pinecone import Pinecone
except ImportError:
    logger.error("Pinecone SDK not installed. Run: pip install pinecone")
    sys.exit(1)


SKILLS_DIR = os.path.expanduser("~/.gemini/antigravity/skills")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
INDEX_NAME = "g777-memory"
NAMESPACE = "agents"


def parse_skill_file(skill_path: str) -> dict:
    """Parse a SKILL.md file and extract frontmatter + content summary."""
    skill_file = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_file):
        return {}

    with open(skill_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse YAML frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1])
            except yaml.YAMLError:
                meta = {}
            body = parts[2].strip()
        else:
            meta = {}
            body = content
    else:
        meta = {}
        body = content

    name = meta.get("name", os.path.basename(skill_path))
    description = meta.get("description", "")

    # Take first 800 chars of body for embedding context
    body_summary = body[:800]

    return {
        "id": name,
        "name": name,
        "description": description,
        "skill_path": os.path.basename(skill_path),
        "text": f"{name}: {description}. {body_summary}",
    }


def main() -> None:
    """Upload all agents to Pinecone."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )

    if not PINECONE_API_KEY:
        logger.error("PINECONE_API_KEY not set")
        sys.exit(1)

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)

    # Collect all agency skills
    skills = []
    for entry in sorted(os.listdir(SKILLS_DIR)):
        if not entry.startswith("agency-"):
            continue
        skill_path = os.path.join(SKILLS_DIR, entry)
        if not os.path.isdir(skill_path):
            continue
        parsed = parse_skill_file(skill_path)
        if parsed:
            skills.append(parsed)

    logger.info("Found %d agency skills to upload", len(skills))

    # Upload in batches of 10
    batch_size = 10
    for i in range(0, len(skills), batch_size):
        batch = skills[i : i + batch_size]
        records = []
        for skill in batch:
            records.append(
                {
                    "_id": skill["id"],
                    "text": skill["text"],
                    "name": skill["name"],
                    "description": skill["description"],
                    "skill_path": skill["skill_path"],
                }
            )
        try:
            index.upsert_records(NAMESPACE, records)
            logger.info(
                "Uploaded batch %d-%d (%d records)",
                i + 1,
                min(i + batch_size, len(skills)),
                len(records),
            )
        except Exception as e:
            logger.error("Failed to upload batch %d: %s", i, e)
            # Fallback: try one by one
            for record in records:
                try:
                    index.upsert_records(NAMESPACE, [record])
                    logger.info("  Uploaded: %s", record["_id"])
                except Exception as e2:
                    logger.error("  Failed: %s - %s", record["_id"], e2)

        time.sleep(0.5)

    logger.info("Done! Uploaded %d agents to %s/%s", len(skills), INDEX_NAME, NAMESPACE)


if __name__ == "__main__":
    main()
