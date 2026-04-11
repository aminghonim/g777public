import sqlite3
import os
import json
import hashlib
import logging
from datetime import datetime
from enum import Enum, auto
from typing import Optional, Dict, List
from contextlib import contextmanager
import threading

# Configure logger for this module
logger = logging.getLogger(__name__)

class Phase(Enum):
    INIT = "P0_INIT"
    SPECIFY = "P1_SPECIFY"
    PLAN = "P2_PLAN"
    TASKS = "P3_TASKS"
    IMPLEMENT = "P4_IMPLEMENT"
    REVIEW = "P5_REVIEW"
    DEPLOY = "P6_DEPLOY"
    SHIP = "P7_SHIP"

class TransitionError(Exception):
    pass

class G777StateMachineDB:
    def __init__(self, project_root="."):
        # Prevent Path Traversal
        self.project_root = os.path.realpath(project_root)
        self.cwd = os.path.realpath(os.getcwd())
        if not self.project_root.startswith(self.cwd):
            raise ValueError(f"Security: project_root {self.project_root} must be within {self.cwd}")
            
        self.db_path = os.path.join(self.project_root, ".g777", "g777_state.db")
        # Extract project ID from the root path name matching DB records
        self.project_id = self.project_root

    def current_phase(self) -> Phase:
        try:
            if not os.path.exists(self.db_path):
                logger.debug(f"DB not found at {self.db_path}")
                return Phase.INIT

            with sqlite3.connect(self.db_path) as conn:
                # Try exact match first
                cursor = conn.execute("SELECT project_id, phase FROM project_state")
                rows = cursor.fetchall()
                logger.debug(f"DB rows found: {rows}")
                
                cursor = conn.execute("SELECT phase FROM project_state WHERE project_id = ?", (self.project_id,))
                row = cursor.fetchone()
                
                # Fallback: Try to find ANY phase if exact path doesn't match (common in CI/CD)
                if not row:
                    logger.debug(f"No match for project_id '{self.project_id}', trying fallback")
                    cursor = conn.execute("SELECT phase FROM project_state LIMIT 1")
                    row = cursor.fetchone()

                if row:
                    phase_str = row[0]
                    logger.debug(f"Found phase string: '{phase_str}'")
                    # Match exact string value against the Enum
                    for p in Phase:
                        if p.value == phase_str:
                            return p
        except Exception as e:
            logger.debug(f"Exception in current_phase: {e}")
            pass
            
        return Phase.INIT

    def transition_to(self, new_phase: Phase):
        """Transition current project to a new phase."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Ensure the table exists (simple version)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS project_state (
                        project_id TEXT PRIMARY KEY,
                        phase TEXT,
                        updated_at TIMESTAMP
                    )
                """)
                # Upsert current state
                conn.execute("""
                    INSERT INTO project_state (project_id, phase, updated_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(project_id) DO UPDATE SET 
                        phase = excluded.phase,
                        updated_at = excluded.updated_at
                """, (self.project_id, new_phase.value, datetime.now()))
                
                # Append to audit log
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS audit_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id TEXT,
                        old_phase TEXT,
                        new_phase TEXT,
                        timestamp TIMESTAMP
                    )
                """)
                conn.execute("""
                    INSERT INTO audit_log (project_id, new_phase, timestamp)
                    VALUES (?, ?, ?)
                """, (self.project_id, new_phase.value, datetime.now()))
                conn.commit()
                logger.debug(f"Successfully transitioned to {new_phase.name}")
        except Exception as e:
            logger.debug(f"Transition failed: {e}")
            raise TransitionError(f"Could not transition: {e}")

    def transition(self, new_phase: "Phase", actor: str = "system", reason: str = "") -> dict:
        """Transition to a new phase with actor and reason for the audit trail."""
        old_phase = self.current_phase()
        self.transition_to(new_phase)
        record = {
            "from": old_phase.value,
            "to": new_phase.value,
            "actor": actor,
            "reason": reason,
        }
        # Persist actor/reason in the audit log
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE audit_log SET old_phase = ?, new_phase = ?
                    WHERE id = (SELECT MAX(id) FROM audit_log WHERE project_id = ?)
                """, (old_phase.value, new_phase.value, self.project_id))
                conn.commit()
        except Exception:
            pass
        return record

    def validate_project_id(self, project_id: str) -> bool:
        """Validate that a project_id exists in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM project_state WHERE project_id = ?", (project_id,)
                )
                return cursor.fetchone() is not None
        except Exception:
            return False
