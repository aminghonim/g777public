\"\"\"
G777 Database Manager - Supabase PostgreSQL Integration
========================================================
Modular, secure database connector with upsert operations
and flexible metadata support.
\"\"\"

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2 import pool

from core.config import settings

# Standardize Logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    \"\"\"Handles all database operations for G777 CRM\"\"\"

    def __init__(self) -> None:
        # Configuration from core settings
        import os
        self.database_url: Optional[str] = getattr(settings, "database_url", os.getenv("DATABASE_URL"))
        
        if not self.database_url or self.database_url.startswith("sqlite") or self.database_url.startswith("mock") or "host" in self.database_url:
            logger.info("Running in DATABASE MOCK/TEST MODE (SQLite In-Memory)")
            self.is_mock = True
            self.pool = None
            self._init_mock_db()
            return
            
        self.is_mock = False
        # Connection Pool for efficiency (Thread-Safe for asyncio.to_thread)
        try:
            self.pool = pool.ThreadedConnectionPool(
                minconn=1, maxconn=20, dsn=self.database_url
            )
            logger.info("Threaded Database pool created successfully")
        except psycopg2.Error as e:
            logger.error(f"Database connection failed: {e}. Falling back to MOCK mode.")
            self.is_mock = True
            self.pool = None
            self._init_mock_db()

    def _init_mock_db(self) -> None:
        \"\"\"Initialize in-memory SQLite for testing/mocking\"\"\"
        import sqlite3
        self.mock_conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.mock_conn.row_factory = sqlite3.Row
        cursor = self.mock_conn.cursor()
        
        # Create minimal schema for testing
        cursor.execute("CREATE TABLE customers (id TEXT PRIMARY KEY, phone TEXT, name TEXT, user_id TEXT, last_interaction TIMESTAMP, metadata TEXT)")
        cursor.execute("CREATE TABLE interactions (id TEXT PRIMARY KEY, customer_id TEXT, role TEXT, message TEXT, user_id TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("CREATE TABLE system_prompts (id TEXT PRIMARY KEY, prompt_name TEXT, prompt_text TEXT, is_active BOOLEAN, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        
        # Seed a test prompt
        cursor.execute(
            \"INSERT INTO system_prompts (id, prompt_name, prompt_text, is_active) VALUES (?, ?, ?, ?)\",
            (str(uuid.uuid4()), \"entity_extractor\", \"Extract entities from: {conversation}\", True)
        )
        self.mock_conn.commit()
        logger.info(\"Mock SQLite DB initialized with test schema.\")

    def get_connection(self):
        \"\"\"Get a connection from the pool or return mock connection\"\"\"
        if self.is_mock:
            return self.mock_conn
        if self.pool is None:
            return None
        try:
            return self.pool.getconn()
        except psycopg2.Error as e:
            logger.error(f\"Failed to get connection from pool: {e}\")
            return None

    def release_connection(self, conn) -> None:
        \"\"\"Return connection to pool (NOP for mock)\"\"\"
        if self.is_mock or self.pool is None or conn is None:
            return
        self.pool.putconn(conn)

    def upsert_customer(
        self,
        phone: str,
        user_id: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        \"\"\"
        SAAS-008: Isolated Customer Upsert.
        Strictly requires user_id for tenant separation.
        \"\"\"
        if self.is_mock:
            cursor = self.mock_conn.cursor()
            cursor.execute(
                \"SELECT id, metadata FROM customers WHERE phone = ? AND user_id = ?\",
                (phone, user_id),
            )
            existing = cursor.fetchone()

            if existing:
                customer_id = existing[\"id\"]
                current_meta = json.loads(existing[\"metadata\"]) if existing[\"metadata\"] else {}
                merged_meta = {**current_meta, **(metadata or {})}
                cursor.execute(
                    \"UPDATE customers SET name = COALESCE(?, name), metadata = ?, last_interaction = ? WHERE id = ?\",
                    (name, json.dumps(merged_meta), datetime.now(timezone.utc).isoformat(), customer_id),
                )
            else:
                customer_id = str(uuid.uuid4())
                cursor.execute(
                    \"INSERT INTO customers (id, phone, name, metadata, user_id, last_interaction) VALUES (?, ?, ?, ?, ?, ?)\",
                    (customer_id, phone, name, json.dumps(metadata or {}), user_id, datetime.now(timezone.utc).isoformat()),
                )
            self.mock_conn.commit()
            return customer_id

        if self.pool is None:
            return \"mock-customer-id\"
        
        conn = self.get_connection()
        if not conn:
            return \"error-no-conn\"
            
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 1. Scope search strictly to user_id
                cursor.execute(
                    \"SELECT id, metadata FROM customers WHERE phone = %s AND user_id = %s\",
                    (phone, user_id),
                )
                existing = cursor.fetchone()

                if existing:
                    customer_id = existing[\"id\"]
                    update_data: Dict[str, Any] = {\"last_interaction\": datetime.now(timezone.utc)}
                    if name:
                        update_data[\"name\"] = name
                    if metadata:
                        current_meta = existing.get(\"metadata\", {}) or {}
                        merged_meta = {**current_meta, **metadata}
                        update_data[\"metadata\"] = Json(merged_meta)

                    set_clause = \", \".join([f\"{k} = %s\" for k in update_data.keys()])
                    values = list(update_data.values()) + [phone, user_id]
                    cursor.execute(
                        f\"UPDATE customers SET {set_clause} WHERE phone = %s AND user_id = %s\",
                        values,
                    )
                else:
                    cursor.execute(
                        \"\"\"
                        INSERT INTO customers (phone, name, metadata, user_id)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                        \"\"\",
                        (phone, name, Json(metadata or {})),
                    )
                    result = cursor.fetchone()
                    customer_id = result[\"id\"] if result else \"unknown\"

                conn.commit()
                return str(customer_id)

        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f\"Error in upsert_customer: {e}\")
            raise
        finally:
            self.release_connection(conn)

    def save_interaction(
        self, customer_id: str, user_id: str, role: str, message: str
    ) -> str:
        \"\"\"
        SAAS-008: Saving isolated interaction.
        \"\"\"
        if self.is_mock:
            cursor = self.mock_conn.cursor()
            interaction_id = str(uuid.uuid4())
            cursor.execute(
                \"INSERT INTO interactions (id, customer_id, role, message, user_id) VALUES (?, ?, ?, ?, ?)\",
                (interaction_id, customer_id, role, message, user_id),
            )
            self.mock_conn.commit()
            return interaction_id

        if self.pool is None:
            return \"mock-interaction-id\"
            
        conn = self.get_connection()
        if not conn:
            return \"error-no-conn\"
            
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    \"\"\"
                    INSERT INTO interactions (customer_id, role, message, user_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    \"\"\",
                    (
                        customer_id,
                        role,
                        message if isinstance(message, str) else json.dumps(message),
                        user_id,
                    ),
                )
                result = cursor.fetchone()
                conn.commit()
                return str(result[\"id\"]) if result else \"unknown\"
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f\"Error in save_interaction: {e}\")
            raise
        finally:
            self.release_connection(conn)

    def save_analytics(
        self,
        customer_id: str,
        user_id: str,
        intent: str,
        confidence: float,
        extracted_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        \"\"\"
        SAAS-008: Saving isolated analytics.
        \"\"\"
        if self.pool is None:
            return \"mock-analytics-id\"
            
        conn = self.get_connection()
        if not conn:
            return \"error-no-conn\"
            
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    \"\"\"
                    INSERT INTO analytics (customer_id, detected_intent, confidence_score, extracted_data, user_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    \"\"\",
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
                return str(result[\"id\"]) if result else \"unknown\"
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f\"Error in save_analytics: {e}\")
            raise
        finally:
            self.release_connection(conn)

    def get_customer_by_phone(self, phone: str, user_id: str) -> Optional[Dict[str, Any]]:
        \"\"\"
        SAAS-008: Strictly scoped customer retrieval.
        \"\"\"
        if self.is_mock:
            cursor = self.mock_conn.cursor()
            cursor.execute(\"SELECT * FROM customers WHERE phone = ? AND user_id = ?\", (phone, user_id))
            row = cursor.fetchone()
            if row:
                res = dict(row)
                res['metadata'] = json.loads(res['metadata']) if res.get('metadata') else {}
                return res
            return None

        if self.pool is None:
            return None
            
        conn = self.get_connection()
        if not conn:
            return None
            
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    \"SELECT * FROM customers WHERE phone = %s AND user_id = %s\",
                    (phone, user_id),
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        finally:
            self.release_connection(conn)

    def get_customer_interactions(
        self, customer_id: str, user_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        \"\"\"
        SAAS-008: Get conversation history strictly scoped to user_id.
        \"\"\"
        if self.is_mock:
            cursor = self.mock_conn.cursor()
            cursor.execute(
                \"SELECT role, message, timestamp FROM interactions WHERE customer_id = ? AND user_id = ? ORDER BY timestamp DESC LIMIT ?\",
                (customer_id, user_id, limit),
            )
            return [dict(row) for row in cursor.fetchall()]

        if self.pool is None:
            return []
            
        conn = self.get_connection()
        if not conn:
            return []
            
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    \"\"\"
                    SELECT i.role, i.message, i.timestamp
                    FROM interactions i
                    JOIN customers c ON c.id = i.customer_id
                    WHERE i.customer_id = %s AND c.user_id = %s
                    ORDER BY i.timestamp DESC
                    LIMIT %s
                    \"\"\",
                    (customer_id, user_id, limit),
                )
                return [dict(row) for row in cursor.fetchall()]
        finally:
            self.release_connection(conn)

    def get_customers_by_user(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        \"\"\"SaaS-first: Get all customers scoped to a specific user_id.\"\"\"
        if self.pool is None:
            return []
            
        conn = self.get_connection()
        if not conn:
            return []
            
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    \"\"\"
                    SELECT id, phone, name, last_interaction, metadata
                    FROM customers
                    WHERE user_id = %s
                    ORDER BY last_interaction DESC
                    LIMIT %s
                    \"\"\",
                    (user_id, limit),
                )
                return [dict(row) for row in cursor.fetchall()]
        finally:
            self.release_connection(conn)

    def get_user_quota_info(self, user_id: str) -> Dict[str, Any]:
        \"\"\"
        SAAS-013: High-Performance Quota Retrieval.
        Returns combined tier limits and current daily usage.
        \"\"\"
        if self.pool is None:
            return {
                \"daily_limit\": 1000,
                \"message_count\": 0,
                \"max_instances\": 1,
                \"instance_count\": 0,
            }

        conn = self.get_connection()
        if not conn:
            return {}
            
        try:
            try:
                # Validate UUID if needed
                query_id = str(uuid.UUID(user_id)) if user_id and \"-\" in user_id else user_id
            except (ValueError, TypeError):
                query_id = user_id or \"00000000-0000-0000-0000-000000000000\"

            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    \"\"\"
                    SELECT 
                        COALESCE(t.daily_limit, 1000) as daily_limit,
                        COALESCE(u.message_count, 0) as message_count,
                        COALESCE(t.max_instances, 1) as max_instances,
                        COALESCE(u.instance_count, 0) as instance_count
                    FROM users usr
                    LEFT JOIN tiers t ON t.id = usr.tier_id
                    LEFT JOIN usage_quotas u ON u.user_id = usr.id AND u.usage_date = CURRENT_DATE
                    WHERE usr.id::text = %s OR usr.username = %s
                    \"\"\",
                    (query_id, user_id),
                )
                result = cursor.fetchone()
                return (
                    dict(result)
                    if result
                    else {
                        \"daily_limit\": 1000,
                        \"message_count\": 0,
                        \"max_instances\": 1,
                        \"instance_count\": 0,
                    }
                )
        finally:
            self.release_connection(conn)

    def increment_daily_usage(self, user_id: str, field: str = \"message_count\") -> None:
        \"\"\"
        SAAS-013: Atomic Quota Increment.
        Ensures thread-safe counter updates using Postgres ON CONFLICT.
        \"\"\"
        if self.pool is None or field not in [\"message_count\", \"instance_count\"]:
            return

        conn = self.get_connection()
        if not conn:
            return
            
        try:
            with conn.cursor() as cursor:
                # We need to handle mapping user_id (potentially non-UUID) to actual user record
                cursor.execute(
                    f\"\"\"
                    INSERT INTO usage_quotas (user_id, usage_date, {field})
                    SELECT id, CURRENT_DATE, 1 FROM users WHERE id::text = %s OR username = %s
                    ON CONFLICT (user_id, usage_date) 
                    DO UPDATE SET {field} = usage_quotas.{field} + 1;
                    \"\"\",
                    (user_id, user_id),
                )
                conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f\"Error incrementing quota: {e}\")
        finally:
            self.release_connection(conn)

    def decrement_instance_usage(self, user_id: str) -> None:
        \"\"\"SAAS-013: Atomic decrement for active instances.\"\"\"
        if self.pool is None:
            return
            
        conn = self.get_connection()
        if not conn:
            return
            
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    \"\"\"
                    UPDATE usage_quotas 
                    SET instance_count = GREATEST(0, instance_count - 1)
                    WHERE user_id IN (SELECT id FROM users WHERE id::text = %s OR username = %s)
                      AND usage_date = CURRENT_DATE
                    \"\"\",
                    (user_id, user_id),
                )
                conn.commit()
        finally:
            self.release_connection(conn)

    def close(self) -> None:
        \"\"\"Close all connections\"\"\"
        if self.pool:
            self.pool.closeall()
            logger.info(\"Database pool closed\")

    # ----------------------------
    # Migrations & Helpers
    # ----------------------------
    def check_migrations(self) -> None:
        \"\"\"Run all necessary DB migrations for SaaS features.\"\"\"
        if self.pool is None:
            return
        self._ensure_users_table()
        self._ensure_tiers_and_quotas_tables()
        self._ensure_licenses_and_devices_tables()
        self._ensure_multitenancy_columns()

    def _ensure_users_table(self) -> None:
        conn = self.get_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                cursor.execute(\"CREATE EXTENSION IF NOT EXISTS pgcrypto;\")
                cursor.execute(
                    \"\"\"
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
                    \"\"\"
                )
                conn.commit()
        finally:
            self.release_connection(conn)

    def _ensure_tiers_and_quotas_tables(self) -> None:
        conn = self.get_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    \"\"\"
                    CREATE TABLE IF NOT EXISTS tiers (
                        id SERIAL PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL,
                        daily_limit INTEGER DEFAULT 100,
                        max_instances INTEGER DEFAULT 1
                    );
                    \"\"\"
                )
                cursor.execute(
                    \"\"\"
                    INSERT INTO tiers (name, daily_limit, max_instances)
                    VALUES ('Starter', 1000, 1), ('Pro', 5000, 5)
                    ON CONFLICT (name) DO UPDATE SET 
                        daily_limit = EXCLUDED.daily_limit,
                        max_instances = EXCLUDED.max_instances;
                    \"\"\"
                )
                cursor.execute(
                    \"\"\"
                    CREATE TABLE IF NOT EXISTS usage_quotas (
                        user_id UUID NOT NULL,
                        usage_date DATE DEFAULT CURRENT_DATE,
                        message_count INTEGER DEFAULT 0,
                        instance_count INTEGER DEFAULT 0,
                        PRIMARY KEY (user_id, usage_date)
                    );
                    \"\"\"
                )
                conn.commit()
        finally:
            self.release_connection(conn)

    def _ensure_licenses_and_devices_tables(self) -> None:
        conn = self.get_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    \"\"\"
                    CREATE TABLE IF NOT EXISTS licenses (
                        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                        license_key TEXT UNIQUE NOT NULL,
                        tier_id INTEGER REFERENCES tiers(id),
                        max_devices INTEGER DEFAULT 1,
                        expires_at TIMESTAMP WITH TIME ZONE,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                    \"\"\"
                )
                cursor.execute(
                    \"\"\"
                    CREATE TABLE IF NOT EXISTS devices (
                        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                        license_id UUID REFERENCES licenses(id) ON DELETE CASCADE,
                        hwid TEXT NOT NULL,
                        registered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        UNIQUE(license_id, hwid)
                    );
                    \"\"\"
                )
                conn.commit()
        finally:
            self.release_connection(conn)

    def _ensure_multitenancy_columns(self) -> None:
        conn = self.get_connection()
        if not conn: return
        tables = [\"customers\", \"interactions\", \"messages\", \"campaigns\"]
        try:
            with conn.cursor() as cursor:
                for table in tables:
                    cursor.execute(
                        \"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)\",
                        (table,),
                    )
                    if not cursor.fetchone()[0]:
                        continue

                    cursor.execute(
                        f\"\"\"
                        DO $$
                        BEGIN
                            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                           WHERE table_name='{table}' AND column_name='user_id') THEN
                                 ALTER TABLE {table} ADD COLUMN user_id TEXT;
                                 CREATE INDEX IF NOT EXISTS idx_{table}_user_id ON {table}(user_id);
                            END IF;
                        END
                        $$;
                        \"\"\"
                    )
                conn.commit()
        except psycopg2.Error as e:
            logger.warning(f\"Migration failed: {e}\")
        finally:
            self.release_connection(conn)

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        if self.pool is None:
            return None
        conn = self.get_connection()
        if not conn: return None
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    \"SELECT * FROM users WHERE username = %s OR email = %s\",
                    (username, username),
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        finally:
            self.release_connection(conn)

    def get_system_prompt(self, prompt_name: str, user_id: str = \"default\") -> str:
        \"\"\"
        Retrieves a system prompt by name.
        \"\"\"
        if self.is_mock:
            cursor = self.mock_conn.cursor()
            cursor.execute(\"SELECT prompt_text FROM system_prompts WHERE prompt_name = ? AND is_active = 1\", (prompt_name,))
            row = cursor.fetchone()
            if row:
                return row[\"prompt_text\"]
            return \"Mock prompt for \" + prompt_name

        if self.pool is None:
            return \"\"
        
        conn = self.get_connection()
        if not conn:
            return \"\"
            
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    \"SELECT prompt_text FROM system_prompts WHERE prompt_name = %s AND is_active = TRUE\",
                    (prompt_name,),
                )
                result = cursor.fetchone()
                return result[\"prompt_text\"] if result else \"\"
        finally:
            self.release_connection(conn)

    def update_customer(self, customer_id: str, user_id: str, updates: Dict[str, Any]) -> bool:
        \"\"\"
        Updates specific fields of a customer record.
        \"\"\"
        if self.is_mock:
            cursor = self.mock_conn.cursor()
            
            # Handle metadata merging if present
            if \"metadata\" in updates:
                cursor.execute(\"SELECT metadata FROM customers WHERE id = ? AND user_id = ?\", (customer_id, user_id))
                row = cursor.fetchone()
                current_meta = json.loads(row[\"metadata\"]) if row and row[\"metadata\"] else {}
                new_meta = updates[\"metadata\"]
                merged_meta = {**current_meta, **new_meta}
                updates[\"metadata\"] = json.dumps(merged_meta)

            set_clause = \", \".join([f\"{k} = ?\" for k in updates.keys()])
            values = list(updates.values()) + [customer_id, user_id]
            cursor.execute(f\"UPDATE customers SET {set_clause} WHERE id = ? AND user_id = ?\", values)
            self.mock_conn.commit()
            return True

        if self.pool is None:
            return False

        conn = self.get_connection()
        if not conn: return False
        try:
            with conn.cursor() as cursor:
                # Handle metadata merging if present in updates
                if \"metadata\" in updates:
                    cursor.execute(\"SELECT metadata FROM customers WHERE id = %s AND user_id = %s\", (customer_id, user_id))
                    row = cursor.fetchone()
                    current_meta = row[0] if row and row[0] else {}
                    new_meta = updates[\"metadata\"]
                    merged_meta = {**current_meta, **new_meta}
                    updates[\"metadata\"] = Json(merged_meta)

                set_clause = \", \".join([f\"{k} = %s\" for k in updates.keys()])
                values = list(updates.values()) + [customer_id, user_id]
                cursor.execute(f\"UPDATE customers SET {set_clause} WHERE id = %s AND user_id = %s\", values)
                conn.commit()
            return True
        except Exception as e:
            logger.error(f\"Error updating customer {customer_id}: {e}\")
            if conn: conn.rollback()
            return False
        finally:
            self.release_connection(conn)


# Singleton instance
try:
    db_manager = DatabaseManager()
except Exception as e:
    logger.warning(f\"Could not initialize DatabaseManager: {e}\")
    db_manager = None