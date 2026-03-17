import subprocess
import logging
import shlex
import re
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SandboxExecutor:
    """
    Executes shell commands in a controlled environment with validation.
    """

    DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",  # recursive delete root (Linux/GitBash)
        r"del\s+/s\s+/q\s+c:\\",  # recursive delete C: (Windows)
        r"format\s+[a-z]:",  # format drive
        r":(){:|:&};:",  # fork bomb
        r"mkfs",  # make filesystem
        r"dd\s+if=",  # direct disk write
    ]

    def __init__(self, allowed_commands: Optional[list] = None):
        self.allowed_commands = allowed_commands

    def validate_command(self, command: str) -> bool:
        """
        Checks if the command contains any dangerous patterns.
        """
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                logger.error(f"Blocked dangerous command: {command}")
                return False
        return True

    def execute(
        self, command: str, timeout: int = 30, cwd: str = None
    ) -> Tuple[int, str, str]:
        """
        Executes a shell command if it passes validation.
        Returns: (return_code, stdout, stderr)
        """
        if not self.validate_command(command):
            return -1, "", "Command blocked by security policy."

        try:
            logger.info(f"Executing Sandbox Command: {command}")

            # Using shell=True for Windows compatibility with complex commands,
            # but validation is critical here.
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return -2, "", "Command execution timed out."
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return -3, "", str(e)


if __name__ == "__main__":
    # Test execution
    executor = SandboxExecutor()

    # Safe command
    code, out, err = executor.execute("echo 'Hello form CNS Sandbox'")
    print(f"Safe Command Output: {out.strip()}")

    # Dangerous command
    code, out, err = executor.execute("rm -rf /")
    print(f"Dangerous Command Result: {err}")
