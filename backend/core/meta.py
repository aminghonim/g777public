import ast
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetaProgrammer:
    """
    Analyzes code to detect patterns and propose improvements or new tools.
    Part of the Recursive Self-Improvement pillar.
    """

    def __init__(self):
        self.improvement_log = []

    def analyze_module(self, module_path: str) -> Dict[str, Any]:
        """
        Parses a python file and extracts functions/classes to identify complexity.
        """
        try:
            with open(module_path, "r", encoding="utf-8") as file:
                code_content = file.read()

            tree = ast.parse(code_content)
            functions = [
                node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
            ]
            classes = [
                node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
            ]

            complexity_score = len(functions) + len(classes)
            logger.info(
                f"Analyzed {module_path}: {len(functions)} functions, {len(classes)} classes."
            )

            return {
                "functions": [f.name for f in functions],
                "classes": [c.name for c in classes],
                "complexity": complexity_score,
            }
        except Exception as e:
            logger.error(f"Failed to analyze module {module_path}: {e}")
            return {}

    def propose_tool(self, task_description: str, code_snippet: str) -> str:
        """
        Generates a proposal for a new tool based on a repeated task.
        """
        proposal = (
            f"# Tool Proposal for: {task_description}\n"
            f"# Based on snippet:\n{code_snippet}\n"
            f"# Suggestion: Encapsulate this logic into a reusable function in a new utility module."
        )
        self.improvement_log.append(proposal)
        logger.info(f"Proposed new tool for task: {task_description}")
        return proposal


if __name__ == "__main__":
    meta = MetaProgrammer()
    # Self-analyze this file
    meta.analyze_module(__file__)
    logger.info(meta.propose_tool("Parse Python AST", "ast.parse(code)"))
