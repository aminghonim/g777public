# 🛡️ QUICK FIX GUIDE: Rule 11 Tenant Isolation Patches
**Est. Implementation Time:** 2-3 hours  
**Complexity:** Medium (requires testing)  
**Risk Level:** Low (safety upgrade)

---

## PATCH #1: Fix `get_customer_by_phone()`

### File: `backend/db_service.py` (Lines 192-196)

**Original (UNSAFE):**
```python
def get_customer_by_phone(phone):
    with get_db_cursor() as cur:
        if not cur: return None
        cur.execute("SELECT * FROM customer_profiles WHERE phone = %s", (phone,))
        res = cur.fetchone()
        return dict(res) if res else None
```

**Fixed (SAFE):**
```python
def get_customer_by_phone(phone, user_id=None, instance_name='G777'):
    """
    Retrieve customer profile with full tenant isolation.
    
    Args:
        phone: Customer phone number
        user_id: Optional - required for multi-saas mode
        instance_name: Tenant instance name
    
    Returns:
        Customer dict or None
    
    Rule 11: Enforces instance_name filter (+ user_id if provided)
    """
    with get_db_cursor() as cur:
        if not cur:
            return None
        
        if user_id:
            # Multi-SaaS mode: double isolation
            cur.execute(
                "SELECT * FROM customer_profiles WHERE phone = %s AND user_id = %s AND instance_name = %s",
                (phone, user_id, instance_name)
            )
        else:
            # Single-tenant mode: instance filter only
            cur.execute(
                "SELECT * FROM customer_profiles WHERE phone = %s AND instance_name = %s",
                (phone, instance_name)
            )
        
        res = cur.fetchone()
        return dict(res) if res else None
```

---

## PATCH #2: Fix `get_all_customers()`

### File: `backend/db_service.py` (Lines 188-191)

**Original (UNSAFE):**
```python
def get_all_customers():
    """Retrieve all customers for CRM dashboard"""
    with get_db_cursor() as cur:
        if not cur: return []
        cur.execute("SELECT * FROM customer_profiles ORDER BY last_conversation_at DESC NULLS LAST, created_at DESC")
        return [dict(r) for r in cur.fetchall()]
```

**Fixed (SAFE):**
```python
def get_all_customers(user_id=None, instance_name='G777', limit=1000):
    """
    Retrieve all customers with tenant isolation and pagination.
    
    Args:
        user_id: Optional - required for multi-saas mode
        instance_name: Tenant instance name
        limit: Page size to prevent huge result sets
    
    Returns:
        List of customer dicts
    
    Rule 11: Enforces instance_name filter (+ user_id if provided)
    """
    with get_db_cursor() as cur:
        if not cur:
            return []
        
        if user_id:
            # Multi-SaaS mode
            cur.execute("""
                SELECT * FROM customer_profiles 
                WHERE user_id = %s AND instance_name = %s
                ORDER BY last_conversation_at DESC NULLS LAST, created_at DESC
                LIMIT %s
            """, (user_id, instance_name, limit))
        else:
            # Single-tenant mode
            cur.execute("""
                SELECT * FROM customer_profiles 
                WHERE instance_name = %s
                ORDER BY last_conversation_at DESC NULLS LAST, created_at DESC
                LIMIT %s
            """, (instance_name, limit))
        
        return [dict(r) for r in cur.fetchall()]
```

---

## PATCH #3: Fix `create_customer()`

### File: `backend/db_service.py` (Lines 198-206)

**Original (UNSAFE):**
```python
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
```

**Fixed (SAFE):**
```python
def create_customer(phone, name=None, ctype='lead', user_id=None, instance_name='G777'):
    """
    Create or return existing customer with tenant isolation.
    
    Args:
        phone: Customer phone
        name: Customer name
        ctype: Customer type (lead/customer)
        user_id: Optional - required for multi-saas
        instance_name: Tenant instance
    
    Returns:
        Customer ID string
    
    Rule 11: Includes instance_name in uniqueness constraint
    """
    with get_db_cursor() as cur:
        if not cur:
            return None
        
        # Check if customer exists (scoped to tenant)
        if user_id:
            cur.execute(
                "SELECT id FROM customer_profiles WHERE phone = %s AND user_id = %s AND instance_name = %s",
                (phone, user_id, instance_name)
            )
        else:
            cur.execute(
                "SELECT id FROM customer_profiles WHERE phone = %s AND instance_name = %s",
                (phone, instance_name)
            )
        
        existing = cur.fetchone()
        if existing:
            return str(existing['id'])
        
        # Insert new customer with tenant context
        cur.execute("""
            INSERT INTO customer_profiles (phone, name, customer_type, user_id, instance_name)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (phone, name, ctype, user_id, instance_name))
        
        res = cur.fetchone()
        return str(res['id']) if res else None
```

---

## PATCH #4: Fix `update_customer_profile()`

### File: `backend/db_service.py` (Lines 208-217)

**Original (UNSAFE):**
```python
def update_customer_profile(phone, updates):
    if not updates: return False
    set_c = [f"{k} = %s" for k in updates if k not in ['id', 'phone', 'created_at']]
    vals = [json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in updates.items() if k not in ['id', 'phone', 'created_at']]
    vals.append(phone)
    with get_db_cursor() as cursor:
        if not cursor: return False
        cursor.execute(f"UPDATE customer_profiles SET {', '.join(set_c)}, updated_at = NOW() WHERE phone = %s", vals)
    return True
```

**Fixed (SAFE):**
```python
def update_customer_profile(phone, updates, user_id=None, instance_name='G777'):
    """
    Update customer profile with tenant isolation.
    
    Args:
        phone: Customer phone
        updates: Dict of fields to update
        user_id: Optional - required for multi-saas
        instance_name: Tenant instance
    
    Returns:
        Boolean indicating success
    
    Rule 11: Scoped update to tenant
    """
    if not updates:
        return False
    
    # Filter safe columns
    safe_columns = ['name', 'customer_type', 'email', 'notes', 'metadata', 'tags']
    set_c = [f"{k} = %s" for k in updates if k in safe_columns]
    vals = [json.dumps(v) if isinstance(v, (dict, list)) else v 
            for k, v in updates.items() if k in safe_columns]
    
    if not set_c:
        return False
    
    # Add tenant filters
    vals.append(phone)
    vals.append(instance_name)
    
    with get_db_cursor() as cursor:
        if not cursor:
            return False
        
        if user_id:
            vals.append(user_id)
            cursor.execute(
                f"UPDATE customer_profiles SET {', '.join(set_c)}, updated_at = NOW() WHERE phone = %s AND instance_name = %s AND user_id = %s",
                vals
            )
        else:
            cursor.execute(
                f"UPDATE customer_profiles SET {', '.join(set_c)}, updated_at = NOW() WHERE phone = %s AND instance_name = %s",
                vals
            )
    
    return True
```

---

## PATCH #5: Fix `mark_field_collected()`

### File: `backend/db_service.py` (Lines 219-236)

**Original (UNSAFE):**
```python
def mark_field_collected(phone, field_name):
    """Removes a field from the missing_fields list in customer profile"""
    with get_db_cursor() as cur:
        if not cur: return False
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
```

**Fixed (SAFE):**
```python
def mark_field_collected(phone, field_name, user_id=None, instance_name='G777'):
    """
    Remove field from missing_fields list with tenant isolation.
    
    Args:
        phone: Customer phone
        field_name: Field name to mark as collected
        user_id: Optional - required for multi-saas
        instance_name: Tenant instance
    
    Returns:
        Boolean indicating success
    
    Rule 11: Scoped update to tenant
    """
    with get_db_cursor() as cur:
        if not cur:
            return False
        
        # Query with tenant filters
        if user_id:
            cur.execute(
                "SELECT missing_fields FROM customer_profiles WHERE phone = %s AND user_id = %s AND instance_name = %s",
                (phone, user_id, instance_name)
            )
        else:
            cur.execute(
                "SELECT missing_fields FROM customer_profiles WHERE phone = %s AND instance_name = %s",
                (phone, instance_name)
            )
        
        row = cur.fetchone()
        if not row or not row['missing_fields']:
            return True
        
        missing = row['missing_fields']
        if field_name in missing:
            missing.remove(field_name)
            
            # Update with tenant filters
            if user_id:
                cur.execute(
                    "UPDATE customer_profiles SET missing_fields = %s, updated_at = NOW() WHERE phone = %s AND user_id = %s AND instance_name = %s",
                    (json.dumps(missing), phone, user_id, instance_name)
                )
            else:
                cur.execute(
                    "UPDATE customer_profiles SET missing_fields = %s, updated_at = NOW() WHERE phone = %s AND instance_name = %s",
                    (json.dumps(missing), phone, instance_name)
                )
        
        return True
```

---

## PATCH #6: Fix `is_excluded()`

### File: `backend/db_service.py` (Lines 274-293)

**Original (UNSAFE):**
```python
def is_excluded(phone):
    """Check if the phone number should be ignored by the bot"""
    settings = get_tenant_settings()
    excluded = settings.get('excluded_contacts', [])
    if phone in excluded: return True
    
    with get_db_cursor() as cur:
        if not cur: return False
        cur.execute("SELECT exclude_from_bot FROM contacts WHERE phone = %s", (phone,))
        res = cur.fetchone()
        if res and res['exclude_from_bot']: return True
        
        cur.execute("SELECT is_blocked, bot_paused_until FROM customer_profiles WHERE phone = %s", (phone,))
        res = cur.fetchone()
        if res:
            if res['is_blocked']: return True
            if res['bot_paused_until'] and res['bot_paused_until'] > datetime.now(res['bot_paused_until'].tzinfo):
                return True
        
    return False
```

**Fixed (SAFE):**
```python
def is_excluded(phone, user_id=None, instance_name='G777'):
    """
    Check if phone should be ignored by bot with tenant isolation.
    
    Args:
        phone: Customer phone
        user_id: Optional - required for multi-saas
        instance_name: Tenant instance
    
    Returns:
        Boolean indicating if excluded
    
    Rule 11: Scoped check to tenant
    """
    # Check tenant settings
    settings = get_tenant_settings()
    excluded = settings.get('excluded_contacts', [])
    if phone in excluded:
        return True
    
    with get_db_cursor() as cur:
        if not cur:
            return False
        
        # Check contacts table with tenant filter
        if user_id:
            cur.execute(
                "SELECT exclude_from_bot FROM contacts WHERE phone = %s AND user_id = %s AND instance_name = %s",
                (phone, user_id, instance_name)
            )
        else:
            cur.execute(
                "SELECT exclude_from_bot FROM contacts WHERE phone = %s AND instance_name = %s",
                (phone, instance_name)
            )
        
        res = cur.fetchone()
        if res and res['exclude_from_bot']:
            return True
        
        # Check customer_profiles with tenant filter
        if user_id:
            cur.execute(
                "SELECT is_blocked, bot_paused_until FROM customer_profiles WHERE phone = %s AND user_id = %s AND instance_name = %s",
                (phone, user_id, instance_name)
            )
        else:
            cur.execute(
                "SELECT is_blocked, bot_paused_until FROM customer_profiles WHERE phone = %s AND instance_name = %s",
                (phone, instance_name)
            )
        
        res = cur.fetchone()
        if res:
            if res['is_blocked']:
                return True
            
            if res['bot_paused_until'] and res['bot_paused_until'] > datetime.now(res['bot_paused_until'].tzinfo):
                return True
    
    return False
```

---

## PATCH #7: Fix `pause_bot_for_customer()`

### File: `backend/db_service.py` (Lines 295-310)

**Original (UNSAFE):**
```python
def pause_bot_for_customer(phone, hours=4):
    """Pauses the bot for a specific customer for N hours"""
    try:
        paused_until = datetime.now() + timedelta(hours=hours)
        with get_db_cursor() as cur:
            if not cur: return False
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
```

**Fixed (SAFE):**
```python
def pause_bot_for_customer(phone, hours=4, user_id=None, instance_name='G777'):
    """
    Pause bot for specific customer with tenant isolation.
    
    Args:
        phone: Customer phone
        hours: Hours to pause (default: 4)
        user_id: Optional - required for multi-saas
        instance_name: Tenant instance
    
    Returns:
        Boolean indicating success
    
    Rule 11: Scoped pause to tenant/user
    """
    try:
        paused_until = datetime.now() + timedelta(hours=hours)
        
        with get_db_cursor() as cur:
            if not cur:
                return False
            
            # Ensure customer exists (with tenant context)
            create_customer(phone, ctype='lead', user_id=user_id, instance_name=instance_name)
            
            # Update with tenant filters
            if user_id:
                cur.execute("""
                    UPDATE customer_profiles 
                    SET bot_paused_until = %s, updated_at = NOW() 
                    WHERE phone = %s AND user_id = %s AND instance_name = %s
                """, (paused_until, phone, user_id, instance_name))
            else:
                cur.execute("""
                    UPDATE customer_profiles 
                    SET bot_paused_until = %s, updated_at = NOW() 
                    WHERE phone = %s AND instance_name = %s
                """, (paused_until, phone, instance_name))
        
        return True
    
    except Exception as e:
        logging.error(f"Error pausing bot for {phone} ({instance_name}): {e}")
        return False
```

---

## DEPLOYMENT CHECKLIST

### Pre-Deployment (Code Review)
- [ ] All 7 patches reviewed and approved
- [ ] No SQL injection vectors introduced
- [ ] Backward compatibility verified (optional params default to G777)
- [ ] Tests updated to pass user_id/instance_name

### Deployment
- [ ] Run pytest suite: `pytest tests/test_db_service.py -v`
- [ ] Monitor logs for deprecation warnings
- [ ] Verify Supabase latency is normal
- [ ] Check for any 500ms+ slow queries

### Post-Deployment (24-72 hours)
- [ ] Verify no data integrity issues
- [ ] Monitor error logs for call signature mismatches
- [ ] Update downstream callers incrementally
- [ ] Plan db_service.py deprecation timeline

---

## TESTING EXAMPLES

### Unit Test: Tenant Isolation
```python
import pytest
from backend.db_service import get_customer_by_phone, create_customer

def test_customer_isolation():
    """Verify customers cannot be accessed across tenant boundaries"""
    
    # Create customer as user_a
    id_a = create_customer(
        phone="555-0001",
        name="Alice",
        user_id="user_a",
        instance_name="G777"
    )
    
    # Query as user_b - should not find it
    customer_b = get_customer_by_phone(
        phone="555-0001",
        user_id="user_b",
        instance_name="G777"
    )
    
    assert customer_b is None, "Tenant isolation violated: user_b found user_a's customer"
    
    # Query as user_a - should find it
    customer_a = get_customer_by_phone(
        phone="555-0001",
        user_id="user_a",
        instance_name="G777"
    )
    
    assert customer_a is not None
    assert customer_a['id'] == id_a
```

### Integration Test: Supabase Latency
```python
import time
import pytest
from backend.db_service import get_all_customers

@pytest.mark.integration
def test_query_latency_under_500ms():
    """Verify queries don't exceed 500ms threshold"""
    
    start_time = time.perf_counter()
    customers = get_all_customers(user_id="user_a", limit=100)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    
    print(f"Query took {elapsed_ms:.2f}ms ({len(customers)} records)")
    assert elapsed_ms < 500, f"Query exceeded 500ms threshold: {elapsed_ms:.2f}ms"
```

---

## ROLLBACK PLAN

If issues arise post-deployment:

```bash
# Step 1: Identify the breaking patch
git log --oneline backend/db_service.py | head -10

# Step 2: Revert specific patches
git revert <commit-hash>

# Step 3: Verify
pytest tests/ -v --tb=short

# Step 4: Notify team
# Post incident update to #incidents channel
```

---

**Total Implementation Time:** 2-3 hours  
**Risk Level:** Low (backward compatible, same data)  
**Testing Effort:** 1-2 hours (new tests required)  
**Post-Deployment Monitoring:** 72 hours recommended

