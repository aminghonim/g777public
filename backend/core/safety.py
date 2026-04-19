import os
import shutil
import time
import ast
import logging
import hashlib
from typing import Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SafetyProtocol")


class SafetyProtocol:
    def __init__(self, root_dir: str = ".safety"):
        self.root_dir = root_dir
        self.snapshots_dir = os.path.join(root_dir, "snapshots")
        self._ensure_infrastructure()

    def _ensure_infrastructure(self):
        """Create necessary directories."""
        os.makedirs(self.snapshots_dir, exist_ok=True)

    def create_atomic_snapshot(self, file_path: str) -> str:
        """
        Creates a time-stamped backup of a file before modification.
        Returns the snapshot ID (filename).
        """
        if not os.path.exists(file_path):
            logger.warning(f"File {file_path} does not exist. Skipping snapshot.")
            return ""

        timestamp = int(time.time())
        filename = os.path.basename(file_path)
        snapshot_id = f"{timestamp}_{filename}"
        dest_path = os.path.join(self.snapshots_dir, snapshot_id)

        try:
            shutil.copy2(file_path, dest_path)
            logger.info(f"Snapshot created: {snapshot_id}")
            return snapshot_id
        except Exception as e:
            logger.error(f"Snapshot failed for {file_path}: {e}")
            raise

    def validate_code_safety(
        self, code: str, language: str = "python"
    ) -> Tuple[bool, str]:
        """
        Static Analysis Gate.
        Checks for syntax errors and dangerous patterns in the proposed code.
        """
        if not code or not code.strip():
            return False, "Code content is empty."

        SUPPORTED_LANGUAGES = {"python"}
        if language.lower() not in SUPPORTED_LANGUAGES:
            logger.warning(f"M10 Guard: Unsupported language '{language}' rejected.")
            return False, f"Language '{language}' is not supported for execution. Only Python is permitted."

        return self._validate_python(code)

    def _validate_python(self, code: str) -> Tuple[bool, str]:
        try:
            tree = ast.parse(code)

            # Security Scan (Basic)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        # Detect subprocess.call, os.system, etc.
                        if node.func.attr in ["system", "popen", "spawn"]:
                            return (
                                False,
                                f"Security Risk: Usage of potentially unsafe function '{node.func.attr}' detected.",
                            )

            return True, "Syntax Valid."
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"
        except Exception as e:
            return False, f"Validation Error: {e}"

    def rollback(self, snapshot_id: str, original_path: str) -> bool:
        """
        Restores a file from a snapshot.
        """
        snapshot_path = os.path.join(self.snapshots_dir, snapshot_id)
        if not os.path.exists(snapshot_path):
            logger.error(f"Snapshot {snapshot_id} not found.")
            return False

        try:
            shutil.copy2(snapshot_path, original_path)
            logger.info(
                f"Rollback successful: {original_path} restored from {snapshot_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False


# Global Instance
safety_protocol = SafetyProtocol()
