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
    print("\n--- Starting Researcher Mission: ADK Self-Healing ---\n")

    try:
        # Initialize Orchestrator which contains the Researcher
        orchestrator = Orchestrator()

        topic = "Google ADK Self-Healing Agents"
        subtopics = ["retry_policy", "state persistence", "error recovery"]

        # Execute Researcher Mission
        report = await orchestrator.researcher.execute_mission(topic, subtopics)

        print("\n--- Mission Report ---\n")
        print(report)

        # Save Report to Artifacts
        artifact_path = os.path.join("Artifacts", "RESEARCH_ADK_SELF_HEALING.md")
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\nReport saved to: {artifact_path}")
        print("\nPASS: Researcher Mission Complete.")

    except Exception as e:
        print(f"\nFAIL: Mission Error: {e}")


if __name__ == "__main__":
    asyncio.run(run_mission())
