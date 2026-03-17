"""
Memory Router - Internal API for n8n to read/write customer memory via g777_backend.

This router acts as the single gateway between n8n workflows and the Supabase
`customer_memory` table, eliminating the need for n8n to hold Supabase credentials
or establish direct external TLS connections (which fail under Docker networking).
"""

import logging
from typing import Optional

import psycopg2
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.database_manager import DatabaseManager

logger = logging.getLogger(__name__)
router = APIRouter()


class MemoryEntry(BaseModel):
    """Schema for a single memory record written by n8n workflows."""

    phone: str
    intent: str
    fact: str


def _get_connection():
    """Return a live psycopg2 connection from the singleton DatabaseManager."""
    db = DatabaseManager()
    conn = db.get_connection()
    if conn is None:
        raise HTTPException(status_code=503, detail="Database connection unavailable")
    return conn


def _ensure_memory_table(conn) -> None:
    """Idempotently create the customer_memory table if it does not exist.

    Runs on first request so the table is guaranteed to exist before any
    read/write operation, regardless of migration order.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS customer_memory (
                id SERIAL PRIMARY KEY,
                phone TEXT NOT NULL,
                intent TEXT,
                fact TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
        conn.commit()


@router.get("/", tags=["Memory"])
def get_memory(
    phone: str = Query(..., description="Customer phone number (E.164 without +)"),
    limit: int = Query(10, ge=1, le=100, description="Maximum records to return"),
):
    """Retrieve the most recent memory entries for a customer.

    Called by the n8n `Get Memory (Addon)1` node instead of hitting Supabase
    directly, keeping all DB credentials inside the backend container only.
    """
    conn = _get_connection()
    try:
        _ensure_memory_table(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT phone, intent, fact, created_at
                FROM customer_memory
                WHERE phone = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (phone, limit),
            )
            rows = cur.fetchall()
            return [
                {"phone": r[0], "intent": r[1], "fact": r[2], "created_at": str(r[3])}
                for r in rows
            ]
    except psycopg2.Error as exc:
        logger.error("DB error fetching memory for %s: %s", phone, exc)
        raise HTTPException(status_code=500, detail="Database error") from exc


@router.post("/", status_code=201, tags=["Memory"])
def save_memory(entry: MemoryEntry):
    """Persist a new memory entry for a customer.

    Called by the n8n `Save Memory (Addon)1` node instead of hitting Supabase
    directly, routing the write through the backend so credentials stay secure.
    """
    conn = _get_connection()
    try:
        _ensure_memory_table(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO customer_memory (phone, intent, fact)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (entry.phone, entry.intent, entry.fact),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            logger.info("Saved memory id=%s for phone=%s", new_id, entry.phone)
            return {"id": new_id, "status": "saved"}
    except psycopg2.Error as exc:
        logger.error("DB error saving memory for %s: %s", entry.phone, exc)
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database error") from exc
