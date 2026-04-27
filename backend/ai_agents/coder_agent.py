from google import adk
import logging
import ast

logger = logging.getLogger("ADKCoder")


class CoderAgent(adk.Agent):
    """
    ADK-compliant Coder Agent.
    Specializes in code generation, refactoring, and syntax validation.
    """

    def __init__(self):
        super().__init__(
            name="Architect-Builder",
            instructions="""
            ROLE: System Architect & Full-Stack Developer.
            TASK: Implement features, fix bugs, and optimize codebases.
            
            GUIDELINES:
            1. Prioritize Modular Architecture and Zero-Regression.
            2. Always validate Python syntax before proposing changes.
            3. Use 'replace_file_content' and 'write_to_file' via the Orchestrator's tools.
            4. Follow PEP 8 and project-specific coding standards (no emojis in code).
            """,
        )

    def validate_syntax(self, code: str) -> bool:
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
