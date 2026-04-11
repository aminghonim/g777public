"""
Sandbox Executor - Secure Command Execution with RTK + SmartFilter.

Validates shell commands against dangerous patterns before execution,
then routes through SystemCommandExecutor for token optimization
and audit compliance.

Architecture:
    Request -> SandboxExecutor.validate_command() -> [security check]
            -> SystemCommandExecutor.execute() -> [RTK + Filter]
            -> (return_code, filtered_stdout, stderr)
"""

import logging
import re
from typing import Optional, Tuple

from backend.core.output_filter import CommandOutputWrapper

logger = logging.getLogger("g777.sandbox")


class SandboxExecutor:
    """
    Executes shell commands in a controlled environment with validation.

    Combines security validation (dangerous pattern blocking) with
    output optimization (RTK + SmartOutputFilter).

    Args:
        allowed_commands: Optional whitelist of allowed command prefixes.
        instance_name: Tenant identifier for audit trail isolation.
    """

    DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",           # recursive delete root (Linux/GitBash)
        r"del\s+/s\s+/q\s+c:\\",   # recursive delete C: (Windows)
        r"format\s+[a-z]:",        # format drive
        r":(){:|:&};:",            # fork bomb
        r"mkfs",                   # make filesystem
        r"dd\s+if=",              # direct disk write
    ]

    def __init__(
        self,
        allowed_commands: Optional[list] = None,
        instance_name: str = "sandbox_default",
    ) -> None:
        self.allowed_commands = allowed_commands
        self.instance_name = instance_name
        self._output_wrapper = CommandOutputWrapper(instance_name)

    def validate_command(self, command: str) -> bool:
        """
        Check if the command contains any dangerous patterns.

        Returns True if the command is safe, False if blocked.
        """
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                logger.error(
                    "Blocked dangerous command",
                    extra={
                        "instance_name": self.instance_name,
                        "command": command,
                        "matched_pattern": pattern,
                    },
                )
                return False
        return True

    def execute(
        self,
        command: str,
        timeout: int = 30,
        cwd: Optional[str] = None,
        apply_filter: bool = True,
    ) -> Tuple[int, str, str]:
        """
        Execute a shell command if it passes validation.

        Uses synchronous subprocess for backward compatibility with
        callers that don't support async. For async callers, use
        SystemCommandExecutor directly.

        Args:
            command: Shell command to execute.
            timeout: Maximum execution time in seconds.
            cwd: Working directory for command execution.
            apply_filter: Whether to apply SmartOutputFilter.

        Returns:
            Tuple of (return_code, stdout, stderr).
            return_code: 0=success, -1=blocked, -2=timeout, -3=error
        """
        if not self.validate_command(command):
            return -1, "", "Command blocked by security policy."

        try:
            import subprocess

            logger.info(
                "Executing sandbox command",
                extra={
                    "instance_name": self.instance_name,
                    "command": command,
                    "cwd": cwd,
                },
            )

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )

            stdout = result.stdout
            stderr = result.stderr

            # Apply SmartOutputFilter to stdout for token optimization
            if apply_filter and stdout:
                filter_result = self._output_wrapper.process(
                    command=command,
                    raw_output=stdout,
                    include_metadata=True,
                )
                stdout = filter_result["filtered_output"]

            return result.returncode, stdout, stderr

        except subprocess.TimeoutExpired:
            logger.error(
                "Command timed out",
                extra={
                    "instance_name": self.instance_name,
                    "command": command,
                    "timeout": timeout,
                },
            )
            return -2, "", "Command execution timed out."
        except FileNotFoundError as exc:
            logger.error(
                "Command not found",
                extra={
                    "instance_name": self.instance_name,
                    "command": command,
                    "error": str(exc),
                },
            )
            return -3, "", str(exc)
        except OSError as exc:
            logger.error(
                "OS error during execution",
                extra={
                    "instance_name": self.instance_name,
                    "command": command,
                    "error": str(exc),
                },
            )
            return -3, "", str(exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor = SandboxExecutor(instance_name="sandbox_test")

    # Safe command
    code, out, err = executor.execute("echo 'Hello from CNS Sandbox'")
    logger.info(
        "Safe command result",
        extra={"return_code": code, "output": out.strip()},
    )

    # Dangerous command
    code, out, err = executor.execute("rm -rf /")
    logger.info(
        "Dangerous command result",
        extra={"return_code": code, "error": err},
    )
