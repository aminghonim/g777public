"""
G777 Smart CRM - Database Service
Uses Supabase PostgreSQL with Connection Pooling & Caching.
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from dotenv import load_dotenv
import time
import logging

load_dotenv()

logger = logging.getLogger(__name__)

def log_query_latency(threshold_ms=500):
    """
    Decorator to log database query latency.
    Triggers warning for queries exceeding threshold.

    Args:
        threshold_ms: Alert threshold in milliseconds (default: 500ms)

    Example:
        @log_query_latency(500)
        def get_customer_by_phone(phone):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                # Log summary
                func_name = func.__name__

                if elapsed_ms > threshold_ms:
                    # SLOW QUERY WARNING
                    logger.warning(
                        f"SLOW_QUERY [ALERT]: {func_name} took {elapsed_ms:.2f}ms "
                        f"(threshold: {threshold_ms}ms) | args={args[:2]} kwargs={list(kwargs.keys())}"
                    )

                    # Send to monitoring service (if configured)
                    _report_slow_query(func_name, elapsed_ms, threshold_ms)
                else:
                    # Normal log
                    logger.debug(
                        f"DB_QUERY: {func_name} took {elapsed_ms:.2f}ms"
                    )

        return wrapper
    return decorator


def _report_slow_query(func_name, elapsed_ms, threshold_ms):
    """
    Send slow query alert to monitoring system.

    TODO: Integrate with:
    - Sentry error tracking
    - DataDog APM
    - Cloudwatch metrics
    - Custom Slack webhook
    """
    pass

# DB Configuration
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("NEON_DATABASE_URL")
_connection_pool: Optional[pool.ThreadedConnectionPool] = None

class SettingsCache:
    def __init__(self, ttl_seconds: int = 60):
        self.ttl = timedelta(seconds=ttl_seconds)
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key):
        if key in self._cache:
            if datetime.now() - self._timestamps[key] < self.ttl:
                return self._cache[key]
            else:
                del self._cache[key]
        return None
    
    def set(self, key, value):
        self._cache[key] = value
        self._timestamps[key] = datetime.now()
    
    def invalidate(self, key=None):
        if key: self._cache.pop(key, None)
        else: self._cache.clear()

settings_cache = SettingsCache(30)

def get_connection_pool():
    global _connection_pool
    if _connection_pool is None:
        if not DATABASE_URL: return None
        try:
            _connection_pool = pool.ThreadedConnectionPool(1, 10, dsn=DATABASE_URL)
        except Exception: return None
    return _connection_pool

@contextmanager
def get_db_cursor():
    pool = get_connection_pool()
    if not pool:
        yield None
        return
    conn = pool.getconn()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
        conn.commit()
        cursor.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)

# --- Tenant Settings ---
@log_query_latency(500)
def get_tenant_settings():
    cached = settings_cache.get("tenant_settings")
    if cached: return cached
    with get_db_cursor() as cursor:
        if not cursor: return {}
        # Changed: Removed is_active filter as per new schema unless added back
        cursor.execute("SELECT * FROM tenant_settings ORDER BY created_at DESC LIMIT 1")
        res = cursor.fetchone()
        if res:
            res = dict(res)
            settings_cache.set("tenant_settings", res)
            return res
        return {}

@log_query_latency(500)
def update_tenant_settings(updates):
    if not updates: return False
    set_c = [f"{k} = %s" for k in updates if k not in ['id', 'created_at']]
    vals = [json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in updates.items() if k not in ['id', 'created_at']]
    with get_db_cursor() as cursor:
        if not cursor: return False
        cursor.execute(f"UPDATE tenant_settings SET {', '.join(set_c)}, updated_at = NOW()", vals)
    settings_cache.invalidate("tenant_settings")
    return True

# --- Prompts ---
@log_query_latency(500)
def get_system_prompt(name):
    key = f"prompt_{name}"
    cached = settings_cache.get(key)
    if cached: return cached
    with get_db_cursor() as cursor:
        if not cursor: return None
        cursor.execute("SELECT prompt_text FROM system_prompts WHERE prompt_name = %s AND is_active = true", (name,))
        res = cursor.fetchone()
        if res:
            settings_cache.set(key, res['prompt_text'])
            return res['prompt_text']
        return None

# --- Offerings ---
def get_all_offerings(cat=None, avail=True):
    key = f"off_{cat}_{avail}"
    cached = settings_cache.get(key)
    if cached: return cached
    with get_db_cursor() as cur:
        if not cur: return []
        q, p = "SELECT * FROM business_offerings WHERE 1=1", []
        if avail: q += " AND is_available = true"
        if cat: 
            q += " AND category = %s"
            p.append(cat)
        q += " ORDER BY name"
        cur.execute(q, p)
        res = [dict(r) for r in cur.fetchall()]
        settings_cache.set(key, res)
        return res

def format_offerings_for_prompt():
    offs = get_all_offerings()
    if not offs: return "لا توجد منتجات حالياً"
    lines = []
    for o in offs:
        p = f"{o['price']} {o.get('currency','EGP')}"
        lines.append(f"- {o['name']} ({p}): {o.get('description','')}")
    return "\n".join(lines)

def create_offering(data):
    """Create a new business offering"""
    with get_db_cursor() as cur:
        if not cur: return None
        cur.execute("""
            INSERT INTO business_offerings (name, category, price, description, is_available)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.get('name'),
            data.get('category', 'General'),
            data.get('price', 0.0),
            data.get('description', ''),
            data.get('is_available', True)
        ))
        result = cur.fetchone()
        settings_cache.invalidate()  # Clear cache
        return str(result['id']) if result else None

def update_offering(offering_id, data):
    """Update an existing offering"""
    if not data: return False
    set_clauses = []
    values = []
    
    for key in ['name', 'category', 'price', 'description', 'is_available']:
        if key in data:
            set_clauses.append(f"{key} = %s")
            values.append(data[key])
    
    if not set_clauses: return False
    
    values.append(offering_id)
    
    with get_db_cursor() as cur:
        if not cur: return False
        cur.execute(f"""
            UPDATE business_offerings 
            SET {', '.join(set_clauses)}, updated_at = NOW()
            WHERE id = %s
        """, values)
        settings_cache.invalidate()  # Clear cache
        return True

# --- Customers (CRM) ---
def get_all_customers():
    """Retrieve all customers for CRM dashboard"""
    with get_db_cursor() as cur:
        if not cur: return []
        cur.execute("SELECT * FROM customer_profiles ORDER BY last_conversation_at DESC NULLS LAST, created_at DESC")
        return [dict(r) for r in cur.fetchall()]

def get_customer_by_phone(phone):
    with get_db_cursor() as cur:
        if not cur: return None
        cur.execute("SELECT * FROM customer_profiles WHERE phone = %s", (phone,))
        res = cur.fetchone()
        return dict(res) if res else None

def create_customer(phone, name=None, ctype='lead'):
    with get_db_cursor() as cur:
        if not cur: return None
        cur.execute("""
            INSERT INTO customer_profiles (phone, name, customer_type)
            VALUES (%s, %s, %s) ON CONFLICT (phone) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """, (phone, name, ctype))
        res = cur.fetchone()
        return str(res['id']) if res else None

def update_customer_profile(phone, updates):
    if not updates: return False
    set_c = [f"{k} = %s" for k in updates if k not in ['id', 'phone', 'created_at']]
    vals = [json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in updates.items() if k not in ['id', 'phone', 'created_at']]
    vals.append(phone)
    with get_db_cursor() as cursor:
        if not cursor: return False
        cursor.execute(f"UPDATE customer_profiles SET {', '.join(set_c)}, updated_at = NOW() WHERE phone = %s", vals)
    return True

# Aliases for compatibility with different parts of the system
update_customer = update_customer_profile

def mark_field_collected(phone, field_name):
    """Removes a field from the missing_fields list in customer profile"""
    with get_db_cursor() as cur:
        if not cur: return False
        # Get current missing fields
        cur.execute("SELECT missing_fields FROM customer_profiles WHERE phone = %s", (phone,))
        row = cur.fetchone()
        if not row or not row['missing_fields']: return True
        
        missing = row['missing_fields']
        if field_name in missing:
            missing.remove(field_name)
            cur.execute(
                "UPDATE customer_profiles SET missing_fields = %s, updated_at = NOW() WHERE phone = %s",
                (json.dumps(missing), phone)
            )
        return True

# --- Conversations & Messages ---
@log_query_latency(500)
def save_message(conv_id, cust_id, sender_type, content, intent=None):
    """Saves a message using the new Row-per-message schema"""
    with get_db_cursor() as cur:
        if not cur: return
        cur.execute("""
            INSERT INTO messages (conversation_id, customer_id, sender_type, content, intent)
            VALUES (%s, %s, %s, %s, %s)
        """, (conv_id, cust_id, sender_type, content, intent))
        
        # Update last interaction timestamp
        if cust_id:
            cur.execute("UPDATE customer_profiles SET last_conversation_at = NOW() WHERE id = %s", (cust_id,))

def create_conversation(cust_id, phone=None):
    with get_db_cursor() as cur:
        if not cur: return None
        cur.execute("INSERT INTO conversations (customer_id, phone) VALUES (%s, %s) RETURNING id", (cust_id, phone))
        return str(cur.fetchone()['id'])

@log_query_latency(500)
def get_conversation_history(conv_id, limit=10):
    """Retrieve chat history for AI context or extractor"""
    with get_db_cursor() as cur:
        if not cur: return ""
        cur.execute("""
            SELECT sender_type, content FROM messages 
            WHERE conversation_id = %s 
            ORDER BY created_at ASC LIMIT %s
        """, (conv_id, limit))
        rows = cur.fetchall()
        return "\n".join([f"{'العميل' if r['sender_type']=='user' else 'ياسمين'}: {r['content']}" for r in rows])

def is_excluded(phone):
    """Check if the phone number should be ignored by the bot"""
    settings = get_tenant_settings()
    excluded = settings.get('excluded_contacts', [])
    if phone in excluded: return True
    
    with get_db_cursor() as cur:
        if not cur: return False
        cur.execute("SELECT is_blocked, bot_paused_until, exclude_from_bot FROM customer_profiles WHERE phone = %s", (phone,))
        res = cur.fetchone()
        if res:
            if res.get('is_blocked') or res.get('exclude_from_bot'): 
                return True
            # Smart Pause Check
            if res.get('bot_paused_until') and res.get('bot_paused_until') > datetime.now(res['bot_paused_until'].tzinfo):
                return True
        
    return False

def pause_bot_for_customer(phone, hours=4):
    """Pauses the bot for a specific customer for N hours"""
    try:
        paused_until = datetime.now() + timedelta(hours=hours)
        with get_db_cursor() as cur:
            if not cur: return False
            # Upsert customer to ensure profile exists
            create_customer(phone, ctype='lead')
            cur.execute("""
                UPDATE customer_profiles 
                SET bot_paused_until = %s, updated_at = NOW() 
                WHERE phone = %s
            """, (paused_until, phone))
        return True
    except Exception as e:
        print(f"Error pausing bot: {e}")
        return False

def get_training_samples(limit=5):
    """Retrieve high-quality (humanized) training examples for AI in-context learning"""
    with get_db_cursor() as cur:
        if not cur: return ""
        # We need a table check here because it's created dynamically by brain_trainer.py
        try:
            cur.execute("SELECT question, humanized_response FROM bot_training_samples ORDER BY created_at DESC LIMIT %s", (limit,))
            rows = cur.fetchall()
            if not rows: return ""
            
            examples = []
            for r in rows:
                examples.append(f"Q: {r['question']}\nA: {r['humanized_response']}")
            
            return "\n\nمثال للردود البشرية المطلوبة:\n" + "\n---\n".join(examples)
        except:
            return ""

if __name__ == "__main__": # pragma: no cover
    if get_connection_pool(): print(" DB Connected")
    else: print(" DB Failed")

