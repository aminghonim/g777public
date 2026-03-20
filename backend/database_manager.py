import logging
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from datetime import datetime

# Setup logging with CNS format
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Single Source of Truth for database integrity and isolation.
    """
    def __init__(self, dsn: Optional[str] = None):
        if not dsn:
            # Fallback to env or mock for testing
            dsn = os.getenv("DATABASE_URL", "dbname=g777_test user=postgres password=root host=localhost")
        self.dsn = dsn
        self.conn = None
        logger.info("DatabaseManager initialized with context isolation protocols.")

    def _ensure_connection(self):
        """Self-healing connection logic."""
        if not self.conn or self.conn.closed:
            try:
                self.conn = psycopg2.connect(self.dsn)
                logger.info("Database connection established.")
            except psycopg2.Error as e:
                logger.error(f"Failed to connect to PG: {e}")
                raise

    def get_customers(self, instance_name: str) -> List[Dict[str, Any]]:
        """Instance-isolated customer fetch."""
        self._ensure_connection()
        query = "SELECT * FROM customers WHERE instance_name = %s"
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (instance_name,))
                return cur.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Query error in get_customers: {e}")
            return []

    def log_action(self, user_id: int, action_type: str, details: str):
        """Audit logging compliance."""
        self._ensure_connection()
        query = "INSERT INTO audit_logs (user_id, action_type, details, created_at) VALUES (%s, %s, %s, %s)"
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (user_id, action_type, details, datetime.now()))
                self.conn.commit()
                logger.info(f"Audit Log: {action_type} for User {user_id}")
        except psycopg2.Error as e:
            logger.error(f"Failed to write audit log: {e}")
            self.conn.rollback()

if __name__ == "__main__":
    db = DatabaseManager()
    db._ensure_connection()
    logger.info("Test finished.")
