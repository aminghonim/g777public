import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.ai_agents.persona_agent import PersonaAgent


def test_persona_instantiation():
    try:
        agent = PersonaAgent()
        print(f"SUCCESS: Agent Name = {agent.name}")
        print("--- Instruction ---")
        # ADK uses 'instruction' not 'instructions'
        print(agent.instruction)

        context = agent.get_persona_context("Ahmed", "Trip A: 100 EGP")
        print("--- Context ---")
        print(context)

        # name is sanitized to a valid identifier - check case-insensitively
        assert "yasmine" in agent.name.lower() or "agent" in agent.name.lower()
        assert "Ahmed" in context
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_persona_instantiation()
