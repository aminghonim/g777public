"""
G777 System Command Executor - Async Subprocess Wrapper.

Provides a unified interface for executing shell commands with:
    1. RTK integration (transparent hook detection)
    2. Smart Output Filtering (post-filter compliance layer)
    3. Full audit trail per tenant
    4. Sensitive data redaction
    5. Timeout and error handling

Architecture:
    Agent -> SystemCommandExecutor.execute()
         -> [RTK Hook auto-rewrites if installed]
         -> subprocess execution
         -> SmartOutputFilter (post-filter)
         -> compressed, auditable output
"""

import asyncio
import logging
import os
import shutil
from typing import Dict, Optional

from backend.core.output_filter import (
    CommandOutputWrapper,
    check_rtk_installed,
)

logger = logging.getLogger("g777.system_commands")


class SystemCommandExecutor:
    """
    Async-safe system command executor with RTK + G777 filtering.

    Designed for use within FastAPI endpoints and agent orchestrators.
    Each instance is bound to a specific tenant (instance_name) for
    compliance and audit isolation.

    Args:
        instance_name: Tenant identifier for audit trail.
        timeout_seconds: Maximum execution time per command.
        enable_rtk: Whether to check for RTK availability.
        enable_filter: Whether to apply G777 post-filter.
    """

    def __init__(
        self,
        instance_name: str,
        timeout_seconds: int = 30,
        enable_rtk: bool = True,
        enable_filter: bool = True,
    ) -> None:
        self.instance_name = instance_name
        self.timeout_seconds = timeout_seconds
        self.enable_rtk = enable_rtk
        self.enable_filter = enable_filter
        self._output_wrapper = CommandOutputWrapper(instance_name)
        self._rtk_available: Optional[bool] = None
        self._rtk_version: Optional[str] = None

    async def execute(self, command: str) -> Dict:
        """
        Execute a shell command with full filtering pipeline.

        Pipeline:
            1. Pre-check: validate command is not empty
            2. Execute: asyncio subprocess (non-blocking)
            3. RTK: if hook is installed, output arrives pre-compressed
            4. G777 Filter: post-filter for compliance + audit trail
            5. Return: compressed output + metadata

        Args:
            command: Shell command string to execute.

        Returns:
            Dict with keys:
                - status: "success" | "error" | "timeout"
                - output: Filtered command output
                - metadata: Audit trail and compression stats
                - unfiltered: Full raw output (only on critical errors)
                - error: Error message (only on failure)
        """
        if not command or not command.strip():
            return {
                "status": "error",
                "error": "Empty command",
                "output": "",
            }

        # Check RTK status (cached after first check)
        if self._rtk_available is None and self.enable_rtk:
            self._rtk_available, self._rtk_version = check_rtk_installed()
            if self._rtk_available:
                logger.info(
                    "RTK detected and active",
                    extra={
                        "instance_name": self.instance_name,
                        "rtk_version": self._rtk_version,
                    },
                )

        try:
            # Build environment with RTK telemetry disabled
            env = os.environ.copy()
            env["RTK_TELEMETRY_DISABLED"] = "1"

            # -----------------------------------------------------------------
            # RTK Integration - Transparent Rewriting
            # -----------------------------------------------------------------
            effective_command = command
            if self.enable_rtk and self._rtk_available:
                # Only prefix if not already prefixed with 'rtk'
                if not command.strip().startswith("rtk "):
                    effective_command = f"rtk {command}"
                    logger.debug(
                        "Command transparently rewritten with RTK",
                        extra={
                            "instance_name": self.instance_name,
                            "original": command,
                            "effective": effective_command,
                        },
                    )

            # Use asyncio subprocess (non-blocking)
            process = await asyncio.create_subprocess_shell(
                effective_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout_seconds,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                logger.warning(
                    "Command timed out",
                    extra={
                        "instance_name": self.instance_name,
                        "command": command,
                        "timeout": self.timeout_seconds,
                    },
                )
                return {
                    "status": "timeout",
                    "error": (
                        f"Command timed out after "
                        f"{self.timeout_seconds}s"
                    ),
                    "command": command,
                    "output": "",
                }

            # Combine stdout + stderr
            raw_output = ""
            if stdout:
                raw_output += stdout.decode("utf-8", errors="replace")
            if stderr:
                raw_output += stderr.decode("utf-8", errors="replace")

            # Apply G777 post-filter if enabled
            if self.enable_filter and raw_output:
                result = self._output_wrapper.process(
                    command=command,
                    raw_output=raw_output,
                    include_metadata=True,
                )

                response: Dict = {
                    "status": "success",
                    "output": result["filtered_output"],
                    "return_code": process.returncode,
                    "metadata": {
                        "instance_name": self.instance_name,
                        "rtk_active": bool(self._rtk_available),
                        "rtk_version": self._rtk_version,
                        **(result.get("metadata", {})),
                    },
                }

                # Preserve unfiltered copy if critical
                if "unfiltered" in result:
                    response["unfiltered"] = result["unfiltered"]

                return response

            # No filter: return raw output
            return {
                "status": "success",
                "output": raw_output.strip(),
                "return_code": process.returncode,
                "metadata": {
                    "instance_name": self.instance_name,
                    "rtk_active": bool(self._rtk_available),
                    "filter_applied": False,
                },
            }

        except FileNotFoundError as exc:
            logger.error(
                "Command not found",
                extra={
                    "instance_name": self.instance_name,
                    "command": command,
                    "error": str(exc),
                },
            )
            return {
                "status": "error",
                "error": f"Command not found: {exc}",
                "command": command,
                "output": "",
            }
        except OSError as exc:
            logger.error(
                "OS error during command execution",
                extra={
                    "instance_name": self.instance_name,
                    "command": command,
                    "error": str(exc),
                },
            )
            return {
                "status": "error",
                "error": f"OS error: {exc}",
                "command": command,
                "output": "",
            }

    async def execute_with_rtk(self, command: str) -> Dict:
        """
        Execute a command explicitly through RTK (bypass hook).

        Useful when the RTK hook is not installed but you want
        RTK-compressed output for a specific command.

        Args:
            command: Shell command to prefix with 'rtk'.

        Returns:
            Same Dict format as execute().
        """
        rtk_path = shutil.which("rtk")
        if rtk_path:
            rtk_command = f"rtk {command}"
            return await self.execute(rtk_command)

        # Fallback: execute without RTK
        logger.info(
            "RTK not found, executing command directly",
            extra={
                "instance_name": self.instance_name,
                "command": command,
            },
        )
        return await self.execute(command)

    def get_rtk_status(self) -> Dict:
        """
        Return current RTK integration status.

        Returns:
            Dict with rtk_installed, rtk_version, filter_enabled.
        """
        if self._rtk_available is None:
            self._rtk_available, self._rtk_version = check_rtk_installed()

        return {
            "rtk_installed": bool(self._rtk_available),
            "rtk_version": self._rtk_version,
            "filter_enabled": self.enable_filter,
            "instance_name": self.instance_name,
        }
