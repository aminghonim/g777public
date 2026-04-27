"""
G777 Database Manager - Supabase PostgreSQL Integration
========================================================
Modular, secure database connector with upsert operations
and flexible metadata support.
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values, Json
from psycopg2 import pool
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Handles all database operations for G777 CRM"""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL not found in environment variables!")

        # Check for Mock/Testing Mode
        is_mock_or_sqlite = self.database_url.startswith(
            "sqlite"
        ) or self.database_url.startswith("mock")

        if is_mock_or_sqlite:
            if os.getenv("ENV") == "PROD":
                logger.critical(
                    "CRITICAL: Attempted to use SQLITE or MOCK DB in PRODUCTION environment!"
                )
                raise ValueError(
                    "SQLITE and MOCK databases are FORBIDDEN in Production. Set a valid DATABASE_URL."
                )

            logger.info(
                "Running in DATABASE MOCK/SQLITE MODE (No actual PostgreSQL connection)"
            )
            self.pool = None
            self.is_sqlite = True
            return

        self.is_sqlite = False

        # Connection Pool for efficiency (Thread-Safe for asyncio.to_thread)
        try:
            self.pool = pool.ThreadedConnectionPool(
                minconn=1, maxconn=20, dsn=self.database_url
            )
            logger.info("Threaded Database pool created successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def get_connection(self):
        """Get a connection from the pool"""
        if self.pool is None:
            return None
        return self.pool.getconn()

    def release_connection(self, conn):
        """Return connection to pool"""
        if self.pool is None:
            return
        self.pool.putconn(conn)

    def upsert_customer(
        self,
        phone: str,
        user_id: str,
        name: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        SAAS-008: Isolated Customer Upsert.
        Strictly requires user_id for tenant separation.
        """
        if self.pool is None:
            return "mock-customer-id"
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 1. Scope search strictly to user_id
                cursor.execute(
                    "SELECT id, metadata FROM customers WHERE phone = %s AND user_id = %s",
                    (phone, user_id),
                )
                existing = cursor.fetchone()

                if existing:
                    customer_id = existing["id"]
                    update_data = {"last_interaction": datetime.now()}
                    if name:
                        update_data["name"] = name
                    if metadata:
                        current_meta = existing.get("metadata", {}) or {}
                        merged_meta = {**current_meta, **metadata}
                        update_data["metadata"] = Json(merged_meta)

                    set_clause = ", ".join([f"{k} = %s" for k in update_data.keys()])
                    values = list(update_data.values()) + [phone, user_id]
                    cursor.execute(
                        f"UPDATE customers SET {set_clause} WHERE phone = %s AND user_id = %s",
                        values,
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO customers (phone, name, metadata, user_id)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                        """,
                        (phone, name, Json(metadata or {}), user_id),
                    )
                    result = cursor.fetchone()
                    customer_id = result["id"]

                conn.commit()
                return str(customer_id)

        except Exception as e:
            conn.rollback()
            logger.error(f"Error in upsert_customer: {e}")
            raise
        finally:
            self.release_connection(conn)

    def save_interaction(
        self, customer_id: str, user_id: str, role: str, message: str
    ) -> str:
        """
        SAAS-008: Saving isolated interaction.
        """
        if self.pool is None:
            return "mock-interaction-id"
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO interactions (customer_id, role, message, user_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        customer_id,
                        role,
                        message if isinstance(message, str) else json.dumps(message),
                        user_id,
                    ),
                )
                result = cursor.fetchone()
                conn.commit()
                return str(result["id"])
        except Exception as e:
            conn.rollback()
            logger.error(f"Error in save_interaction: {e}")
            raise
        finally:
            self.release_connection(conn)

    def sync_groups_to_db(self, instance_name: str, groups: List[Dict]) -> int:
        """
        SAAS-008: High-Performance Batch Group Sync.
        Uses single bulk query to upsert WhatsApp groups.
        """
        if self.pool is None or not groups:
            return 0

        # Transform into tuples for execute_values
        data_list = [
            (g["id"], instance_name, g["name"], g.get("member_count", 0))
            for g in groups
        ]

        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO groups (id, instance_name, name, member_count)
                    VALUES %s
                    ON CONFLICT (id, instance_name) 
                    DO UPDATE SET 
                        name = EXCLUDED.name,
                        member_count = EXCLUDED.member_count,
                        updated_at = NOW();
                """
                execute_values(cursor, query, data_list)
                conn.commit()
                return len(data_list)
        except Exception as e:
            conn.rollback()
            logger.error(f"Error in bulk sync_groups_to_db: {e}")
            raise
        finally:
            self.release_connection(conn)

    def save_analytics(
        self,
        customer_id: str,
        user_id: str,
        intent: str,
        confidence: float,
        extracted_data: Optional[Dict] = None,
    ) -> str:
        """
        SAAS-008: Saving isolated analytics.
        """
        if self.pool is None:
            return "mock-analytics-id"
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO analytics (customer_id, detected_intent, confidence_score, extracted_data, user_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        customer_id,
                        intent,
                        confidence,
                        Json(extracted_data or {}),
                        user_id,
                    ),
                )
                result = cursor.fetchone()
                conn.commit()
                return str(result["id"])
        except Exception as e:
            conn.rollback()
            logger.error(f"Error in save_analytics: {e}")
            raise
        finally:
            self.release_connection(conn)

    def get_customer_by_phone(self, phone: str, user_id: str) -> Optional[Dict]:
        """
        SAAS-008: Strictly scoped customer retrieval.
        """
        if self.pool is None:
            return None
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM customers WHERE phone = %s AND user_id = %s",
                    (phone, user_id),
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        finally:
            self.release_connection(conn)

    def get_customer_interactions(
        self, customer_id: str, user_id: str, limit: int = 50
    ) -> List[Dict]:
        """
        SAAS-008: Get conversation history strictly scoped to user_id.
        """
        if self.pool is None:
            return []
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT i.role, i.message, i.timestamp
                    FROM interactions i
                    JOIN customers c ON c.id = i.customer_id
                    WHERE i.customer_id = %s AND c.user_id = %s
                    ORDER BY i.timestamp DESC
                    LIMIT %s
                    """,
                    (customer_id, user_id, limit),
                )
                return [dict(row) for row in cursor.fetchall()]
        finally:
            self.release_connection(conn)

    def get_customers_by_user(self, user_id: str, limit: int = 100) -> List[Dict]:
        """SaaS-first: Get all customers scoped to a specific user_id."""
        if self.pool is None:
            return []
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, phone, name, last_interaction, metadata
                    FROM customers
                    WHERE user_id = %s
                    ORDER BY last_interaction DESC
                    LIMIT %s
                    """,
                    (user_id, limit),
                )
                return [dict(row) for row in cursor.fetchall()]
        finally:
            self.release_connection(conn)

    def get_user_quota_info(self, user_id: str) -> Dict[str, Any]:
        """
        SAAS-013: High-Performance Quota Retrieval.
        Returns combined tier limits and current daily usage.
        """
        if self.pool is None:
            return {
                "daily_limit": 1000,
                "message_count": 0,
                "max_instances": 1,
                "instance_count": 0,
            }

        conn = self.get_connection()
        try:
            # Validate UUID syntax to avoid PostgreSQL errors (InvalidTextRepresentation)
            import uuid

            try:
                # If it's a dev string like 'dev_master_007', we treat it as a guest or return default
                # to prevent breaking the SQL query which expects a UUID format.
                query_id = str(uuid.UUID(user_id)) if user_id else None
            except (ValueError, TypeError, AttributeError):
                # Fallback for dev strings or invalid formats
                query_id = "00000000-0000-0000-0000-000000000000"

            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT 
                        COALESCE(t.daily_limit, 1000) as daily_limit,
                        COALESCE(u.message_count, 0) as message_count,
                        COALESCE(t.max_instances, 1) as max_instances,
                        COALESCE(u.instance_count, 0) as instance_count
                    FROM users usr
                    LEFT JOIN tiers t ON t.id = usr.tier_id
                    LEFT JOIN usage_quotas u ON u.user_id = usr.id AND u.usage_date = CURRENT_DATE
                    WHERE usr.id = %s
                    """,
                    (query_id,),
                )
                result = cursor.fetchone()
                return (
                    dict(result)
                    if result
                    else {
                        "daily_limit": 1000,
                        "message_count": 0,
                        "max_instances": 1,
                        "instance_count": 0,
                    }
                )
        finally:
            self.release_connection(conn)

    def increment_daily_usage(self, user_id: str, field: str = "message_count") -> None:
        """
        SAAS-013: Atomic Quota Increment.
        Ensures thread-safe counter updates using Postgres ON CONFLICT.
        """
        if self.pool is None or field not in ["message_count", "instance_count"]:
            return

        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO usage_quotas (user_id, usage_date, {field})
                    VALUES (%s, CURRENT_DATE, 1)
                    ON CONFLICT (user_id, usage_date) 
                    DO UPDATE SET {field} = usage_quotas.{field} + 1;
                    """,
                    (user_id,),
                )
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error incrementing quota: {e}")
        finally:
            self.release_connection(conn)

    def decrement_instance_usage(self, user_id: str) -> None:
        """SAAS-013: Atomic decrement for active instances."""
        if self.pool is None:
            return
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE usage_quotas 
                    SET instance_count = GREATEST(0, instance_count - 1)
                    WHERE user_id = %s AND usage_date = CURRENT_DATE
                    """,
                    (user_id,),
                )
                conn.commit()
        finally:
            self.release_connection(conn)

    def get_interactions_by_user(self, user_id: str, limit: int = 200) -> List[Dict]:
        """SaaS-first: Get all interactions scoped to a specific user_id."""
        if self.pool is None:
            return []
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT i.id, i.role, i.message, i.timestamp, c.phone, c.name
                    FROM interactions i
                    JOIN customers c ON c.id = i.customer_id
                    WHERE c.user_id = %s
                    ORDER BY i.timestamp DESC
                    LIMIT %s
                    """,
                    (user_id, limit),
                )
                return [dict(row) for row in cursor.fetchall()]
        finally:
            self.release_connection(conn)

    def get_dashboard_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        SAAS-018: Aggregated Dashboard Analytics.
        Returns total metrics and 7-day activity strictly scoped to user_id.
        """
        if self.pool is None:
            return {}

        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 1. Total Messages Sent (Lifetime)
                # Note: We cast user_id to text to match index-friendly comparison
                cursor.execute(
                    "SELECT COUNT(*) as total FROM messages WHERE user_id::text = %s",
                    (user_id,),
                )
                total_msgs = cursor.fetchone()["total"]

                # 2. Current Usage & Limits
                cursor.execute(
                    """
                    SELECT 
                        COALESCE(q.message_count, 0) as used_today,
                        COALESCE(q.instance_count, 0) as active_instances,
                        t.daily_limit,
                        t.max_instances
                    FROM users u
                    JOIN tiers t ON u.tier_id = t.id
                    LEFT JOIN usage_quotas q ON q.user_id = u.id AND q.usage_date = CURRENT_DATE
                    WHERE u.id::text = %s
                    """,
                    (user_id,),
                )
                usage_data = cursor.fetchone() or {
                    "used_today": 0,
                    "active_instances": 0,
                    "daily_limit": 100,
                    "max_instances": 1,
                }

                # 3. 7-Day Trailing Activity
                cursor.execute(
                    """
                    SELECT usage_date::text, message_count 
                    FROM usage_quotas 
                    WHERE user_id::text = %s 
                      AND usage_date > CURRENT_DATE - INTERVAL '7 days'
                    ORDER BY usage_date ASC
                    """,
                    (user_id,),
                )
                history = cursor.fetchall()

                return {
                    "total_messages_sent": total_msgs,
                    "daily_usage": usage_data["used_today"],
                    "daily_limit": usage_data["daily_limit"],
                    "daily_remaining": max(
                        0, usage_data["daily_limit"] - usage_data["used_today"]
                    ),
                    "active_instances": usage_data["active_instances"],
                    "max_instances": usage_data["max_instances"],
                    "activity_7d": history,
                }
        finally:
            self.release_connection(conn)

    def close(self):
        """Close all connections"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database pool closed")

    # ----------------------------
    # User management helpers
    # ----------------------------
    def check_migrations(self):
        """Run all necessary DB migrations for SaaS features."""
        if self.pool is None:
            return
        self._ensure_users_table()
        self._ensure_tiers_and_quotas_tables()
        self._ensure_licenses_and_devices_tables()
        self._ensure_groups_table()
        self._ensure_crm_tables()
        self._ensure_multitenancy_columns()

    def _ensure_users_table(self):
        """Create `users` table if it does not exist (multitenancy support)."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # ensure pgcrypto extension for gen_random_uuid
                cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

                # Users Table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        email TEXT,
                        instance_name TEXT,
                        role TEXT DEFAULT 'client',
                        tier_id INTEGER,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                    """
                )

                # SAAS Migration: Ensure columns exist if table was created by older versions
                cursor.execute(
                    """
                    DO $$ 
                    BEGIN 
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='tier_id') THEN
                            ALTER TABLE users ADD COLUMN tier_id INTEGER;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='email') THEN
                            ALTER TABLE users ADD COLUMN email TEXT;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='instance_name') THEN
                            ALTER TABLE users ADD COLUMN instance_name TEXT;
                        END IF;
                    END $$;
                    """
                )
                conn.commit()
        finally:
            self.release_connection(conn)

    def _ensure_tiers_and_quotas_tables(self):
        """SAAS-013: Schema Migration for Tiers and Quotas."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. Tiers Table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tiers (
                        id SERIAL PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL,
                        daily_limit INTEGER DEFAULT 100,
                        max_instances INTEGER DEFAULT 1
                    );
                    """
                )

                # 2. Populate Default Tiers
                cursor.execute(
                    """
                    INSERT INTO tiers (name, daily_limit, max_instances)
                    VALUES ('Starter', 1000, 1), ('Pro', 5000, 5)
                    ON CONFLICT (name) DO UPDATE SET 
                        daily_limit = EXCLUDED.daily_limit,
                        max_instances = EXCLUDED.max_instances;
                    """
                )

                # 3. Usage Quotas Table (Atomic Tracker)
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS usage_quotas (
                        user_id UUID NOT NULL,
                        usage_date DATE DEFAULT CURRENT_DATE,
                        message_count INTEGER DEFAULT 0,
                        instance_count INTEGER DEFAULT 0,
                        PRIMARY KEY (user_id, usage_date)
                    );
                    """
                )
                conn.commit()
        finally:
            self.release_connection(conn)

    def _ensure_licenses_and_devices_tables(self):
        """SAAS-016: License Key Management & HWID Binding"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. Licenses Table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS licenses (
                        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                        license_key TEXT UNIQUE NOT NULL,
                        tier_id INTEGER REFERENCES tiers(id),
                        max_devices INTEGER DEFAULT 1,
                        expires_at TIMESTAMP WITH TIME ZONE,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                    """
                )

                # 2. Devices Table for HWID Binding
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS devices (
                        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                        license_id UUID REFERENCES licenses(id) ON DELETE CASCADE,
                        hwid TEXT NOT NULL,
                        registered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        UNIQUE(license_id, hwid)
                    );
                    """
                )
                conn.commit()
        finally:
            self.release_connection(conn)

    def _ensure_multitenancy_columns(self):
        """Add user_id column to core tables if missing."""
        conn = self.get_connection()
        tables = ["customers", "interactions", "messages", "campaigns"]
        try:
            with conn.cursor() as cursor:
                for table in tables:
                    # Check if table exists
                    cursor.execute(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)",
                        (table,),
                    )
                    if not cursor.fetchone()[0]:
                        continue

                    # Add user_id column if not exists
                    cursor.execute(
                        f"""
                        DO $$
                        BEGIN
                            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                           WHERE table_name='{table}' AND column_name='user_id') THEN
                                ALTER TABLE {table} ADD COLUMN user_id TEXT;
                                CREATE INDEX IF NOT EXISTS idx_{table}_user_id ON {table}(user_id);
                            END IF;
                        END
                        $$;
                        """
                    )
                conn.commit()
        except Exception as e:
            logger.warning(f"Migration failed: {e}")
        finally:
            self.release_connection(conn)

    def _ensure_groups_table(self):
        """Create `groups` table if it does not exist."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS groups (
                        id TEXT NOT NULL,
                        instance_name TEXT NOT NULL,
                        name TEXT,
                        member_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        PRIMARY KEY (id, instance_name)
                    );
                    CREATE INDEX IF NOT EXISTS idx_groups_instance_name ON groups(instance_name);
                    """
                )
                conn.commit()
        finally:
            self.release_connection(conn)

    def _ensure_crm_tables(self):
        """SAAS-008: Create customers, interactions, and analytics tables if they do not exist."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS customers (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        phone TEXT NOT NULL,
                        name TEXT,
                        metadata JSONB DEFAULT '{}',
                        user_id TEXT NOT NULL,
                        last_interaction TIMESTAMPTZ,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW(),
                        UNIQUE(phone, user_id)
                    );
                    CREATE INDEX IF NOT EXISTS idx_customers_user_id ON customers(user_id);
                    CREATE INDEX IF NOT EXISTS idx_customers_phone_user ON customers(phone, user_id);

                    CREATE TABLE IF NOT EXISTS interactions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
                        role TEXT NOT NULL,
                        message TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                    CREATE INDEX IF NOT EXISTS idx_interactions_customer_id ON interactions(customer_id);
                    CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interactions(user_id);

                    CREATE TABLE IF NOT EXISTS analytics (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
                        detected_intent TEXT,
                        confidence_score FLOAT,
                        extracted_data JSONB DEFAULT '{}',
                        user_id TEXT NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                    CREATE INDEX IF NOT EXISTS idx_analytics_customer_id ON analytics(customer_id);
                    CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id);
                    """
                )
                conn.commit()
        except Exception as e:
            logger.warning(f"CRM tables migration failed: {e}")
        finally:
            self.release_connection(conn)

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        if self.pool is None:
            return None
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Check both username and email
                cursor.execute(
                    "SELECT * FROM users WHERE username = %s OR email = %s",
                    (username, username),
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        finally:
            self.release_connection(conn)

    def activate_or_validate_license(self, license_key: str, hwid: str) -> dict:
        """
        SAAS-016: Validates license_key and binds hwid.
        Returns the mapped synthetic user details on success or raises Exception.
        """
        if self.pool is None:
            raise Exception("Database not connected")

        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 1. Fetch Active License
                cursor.execute(
                    "SELECT * FROM licenses WHERE license_key = %s AND is_active = TRUE",
                    (license_key,),
                )
                license_data = cursor.fetchone()

                if not license_data:
                    raise Exception("Invalid or inactive license key.")

                if license_data["expires_at"] and license_data[
                    "expires_at"
                ] < datetime.now(timezone.utc):
                    raise Exception("License key has expired.")

                license_id = license_data["id"]
                max_devices = license_data["max_devices"]

                # 2. Query Existing Device Bindings
                cursor.execute(
                    "SELECT * FROM devices WHERE license_id = %s", (license_id,)
                )
                bound_devices = cursor.fetchall()

                is_bound = any(d["hwid"] == hwid for d in bound_devices)

                if is_bound:
                    # Update Last Active Heartbeat
                    cursor.execute(
                        "UPDATE devices SET last_active = NOW() WHERE license_id = %s AND hwid = %s",
                        (license_id, hwid),
                    )
                else:
                    # Not bound yet, check if slot is available
                    if len(bound_devices) >= max_devices:
                        raise Exception(
                            f"License limit reached ({max_devices} devices max)."
                        )

                    # Bind HWID
                    cursor.execute(
                        "INSERT INTO devices (license_id, hwid) VALUES (%s, %s)",
                        (license_id, hwid),
                    )

                # 3. Transparently Get or Create a Synthetic 'User' tied to this License
                cursor.execute(
                    "SELECT * FROM users WHERE username = %s", (license_key,)
                )
                user = cursor.fetchone()

                if not user:
                    # Create Synthetic User
                    tier_id = license_data["tier_id"]
                    cursor.execute(
                        """
                        INSERT INTO users (username, password_hash, instance_name, role, tier_id)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING *
                        """,
                        (
                            license_key,
                            "license_bound",  # Mock Hash
                            f"Inst_{license_key[:8]}",  # Instance Name Isolation
                            "client",
                            tier_id,
                        ),
                    )
                    user = cursor.fetchone()

                conn.commit()
                return dict(user)

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.release_connection(conn)

    def check_license_status(self, username: str) -> dict:
        """
        SAAS-018: Check if the license associated with this user is still valid.
        Used by LicenseGuard middleware to enforce subscription expiry.

        Args:
            username: The username from JWT (equals license_key for synthetic users).

        Returns:
            dict with keys:
                - is_valid (bool): Whether the license is still active and not expired.
                - reason (str): Why the license is invalid, or "active" if valid.
                - expires_at (str|None): ISO format expiry date.
                - days_remaining (int|None): Days until expiry (None if no expiry).
        """
        if self.pool is None:
            return {
                "is_valid": True,
                "reason": "no_database",
                "expires_at": None,
                "days_remaining": None,
            }

        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT expires_at, is_active FROM licenses WHERE license_key = %s",
                    (username,),
                )
                license_data = cursor.fetchone()

                if not license_data:
                    # No license bound to this user — could be a direct DB user
                    return {
                        "is_valid": True,
                        "reason": "no_license_bound",
                        "expires_at": None,
                        "days_remaining": None,
                    }

                if not license_data["is_active"]:
                    return {
                        "is_valid": False,
                        "reason": "license_deactivated",
                        "expires_at": (
                            license_data["expires_at"].isoformat()
                            if license_data["expires_at"]
                            else None
                        ),
                        "days_remaining": 0,
                    }

                if license_data["expires_at"] and license_data[
                    "expires_at"
                ] < datetime.now(timezone.utc):
                    days_expired = (
                        datetime.now(timezone.utc) - license_data["expires_at"]
                    ).days
                    return {
                        "is_valid": False,
                        "reason": "license_expired",
                        "expires_at": license_data["expires_at"].isoformat(),
                        "days_expired": days_expired,
                        "days_remaining": 0,
                    }

                days_remaining = None
                if license_data["expires_at"]:
                    days_remaining = (
                        license_data["expires_at"] - datetime.now(timezone.utc)
                    ).days

                return {
                    "is_valid": True,
                    "reason": "active",
                    "expires_at": (
                        license_data["expires_at"].isoformat()
                        if license_data["expires_at"]
                        else None
                    ),
                    "days_remaining": days_remaining,
                }
        finally:
            self.release_connection(conn)


# Singleton instance
try:
    db_manager = DatabaseManager()
except Exception as e:
    logger.warning(f"Could not initialize DatabaseManager: {e}")
    db_manager = None
