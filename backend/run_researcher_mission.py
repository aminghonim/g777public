import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

sys.path.append(os.getcwd())

from backend.agents.orchestrator import Orchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResearcherMission")


async def run_mission():
    load_dotenv()
    logger.info("\n--- Starting Researcher Mission: ADK Self-Healing ---\n")

    try:
        # Initialize Orchestrator which contains the Researcher
        orchestrator = Orchestrator()

        topic = "Google ADK Self-Healing Agents"
        subtopics = ["retry_policy", "state persistence", "error recovery"]

        # Execute Researcher Mission
        report = await orchestrator.researcher.execute_mission(topic, subtopics)

        logger.info("\n--- Mission Report ---\n")
        logger.info(report)

        # Save Report to Artifacts
        artifact_path = os.path.join("Artifacts", "RESEARCH_ADK_SELF_HEALING.md")
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"\nReport saved to: {artifact_path}")
        logger.info("\nPASS: Researcher Mission Complete.")

    except Exception as e:
        logger.error(f"\nFAIL: Mission Error: {e}")


if __name__ == "__main__":
    asyncio.run(run_mission())
