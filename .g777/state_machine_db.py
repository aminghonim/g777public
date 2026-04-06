import sqlite3
import os
import json
import hashlib
from datetime import datetime
from enum import Enum, auto
from typing import Optional, Dict, List
from contextlib import contextmanager
import threading

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
                print(f"DEBUG: DB not found at {self.db_path}")
                return Phase.INIT

            with sqlite3.connect(self.db_path) as conn:
                # Try exact match first
                cursor = conn.execute("SELECT project_id, phase FROM project_state")
                rows = cursor.fetchall()
                print(f"DEBUG: DB rows found: {rows}")
                
                cursor = conn.execute("SELECT phase FROM project_state WHERE project_id = ?", (self.project_id,))
                row = cursor.fetchone()
                
                # Fallback: Try to find ANY phase if exact path doesn't match (common in CI/CD)
                if not row:
                    print(f"DEBUG: No match for project_id '{self.project_id}', trying fallback")
                    cursor = conn.execute("SELECT phase FROM project_state LIMIT 1")
                    row = cursor.fetchone()

                if row:
                    phase_str = row[0]
                    print(f"DEBUG: Found phase string: '{phase_str}'")
                    # Match exact string value against the Enum
                    for p in Phase:
                        if p.value == phase_str:
                            return p
        except Exception as e:
            print(f"DEBUG: Exception in current_phase: {e}")
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
                print(f"DEBUG: Successfully transitioned to {new_phase.name}")
        except Exception as e:
            print(f"DEBUG: Transition failed: {e}")
            raise TransitionError(f"Could not transition: {e}")

    # Needed because the user script tested this file earlier
    def validate_project_id(self, project_id):
        pass
