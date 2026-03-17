"""
G777 Persistent Error Logger
==============================
Writes critical errors to Supabase (critical_errors table)
so they survive Docker log rotation.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone


logger = logging.getLogger(__name__)


class PersistentErrorLogger:
    """Logs critical errors to the database for long-term retention."""

    def __init__(self) -> None:
        self._db = None

    def _get_db(self):
        """Lazy-load database manager to avoid circular imports."""
        if self._db is None:
            from backend.database_manager import db_manager
            self._db = db_manager
        return self._db

    def critical(
        self,
        service: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Persist a critical error to the database.

        Args:
            service: Origin service name (e.g. 'baileys', 'backend', 'nginx').
            message: Human-readable error description.
            context: Optional dict with extra debugging context.
        """
        self._log_to_db("CRITICAL", service, message, context)

    def error(
        self,
        service: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Persist an error-level event to the database."""
        self._log_to_db("ERROR", service, message, context)

    def _log_to_db(
        self,
        severity: str,
        service: str,
        message: str,
        context: Optional[Dict[str, Any]],
    ) -> None:
        """Internal: write to critical_errors table."""
        db = self._get_db()
        if db is None or db.pool is None:
            logger.warning(
                "PersistentErrorLogger: DB unavailable, falling back to stderr"
            )
            logger.error(f"[{severity}] [{service}] {message} | ctx={context}")
            return

        conn = db.get_connection()
        try:
            from psycopg2.extras import Json

            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO critical_errors
                        (service, severity, message, context, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        service,
                        severity,
                        message[:500],
                        Json(context or {}),
                        datetime.now(timezone.utc),
                    ),
                )
                conn.commit()
        except Exception as exc:
            conn.rollback()
            logger.error(f"PersistentErrorLogger write failed: {exc}")
        finally:
            db.release_connection(conn)


# Singleton
error_logger = PersistentErrorLogger()
