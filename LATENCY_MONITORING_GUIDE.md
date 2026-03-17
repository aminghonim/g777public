# 🔍 LATENCY MONITORING IMPLEMENTATION GUIDE
**Critical for Rule 4: Performance Transparency**  
**Target Threshold:** 500ms per DB query  
**Implementation Time:** 1-2 hours

---

## PART 1: Add Timing Wrapper to db_service.py

### Add to top of file (after imports):

```python
import time
import logging

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
```

---

## PART 2: Apply to All Critical Functions

### Patch each function:

```python
# ✅ Customers (CRM)
@log_query_latency(500)
def get_all_customers(user_id=None, instance_name='G777', limit=1000):
    # ... existing code ...

@log_query_latency(500)
def get_customer_by_phone(phone, user_id=None, instance_name='G777'):
    # ... existing code ...

@log_query_latency(500)
def create_customer(phone, name=None, ctype='lead', user_id=None, instance_name='G777'):
    # ... existing code ...

@log_query_latency(500)
def update_customer_profile(phone, updates, user_id=None, instance_name='G777'):
    # ... existing code ...

@log_query_latency(500)
def mark_field_collected(phone, field_name, user_id=None, instance_name='G777'):
    # ... existing code ...

# ✅ Conversations & Messages
@log_query_latency(500)
def save_message(conv_id, cust_id, sender_type, content, intent=None):
    # ... existing code ...

@log_query_latency(500)
def get_conversation_history(conv_id, limit=10):
    # ... existing code ...

# ✅ Settings & Cache
@log_query_latency(500)
def get_tenant_settings():
    # ... existing code ...

@log_query_latency(500)
def get_all_offerings(cat=None, avail=True):
    # ... existing code ...
```

---

## PART 3: Advanced Monitoring Setup (Optional)

### Add performance baseline tracking:

```python
import os
from datetime import datetime, timedelta

class LatencyBaseline:
    """Track query performance over time"""
    
    def __init__(self):
        self.baselines = {
            'get_all_customers': 100,    # Expected: 100ms
            'get_customer_by_phone': 50,  # Expected: 50ms
            'create_customer': 75,        # Expected: 75ms
        }
        self.deviations = []
    
    def check(self, func_name, elapsed_ms):
        """Alert if query deviates significantly from baseline"""
        if func_name not in self.baselines:
            return
        
        baseline = self.baselines[func_name]
        deviation_pct = ((elapsed_ms - baseline) / baseline) * 100
        
        if deviation_pct > 30:  # >30% slower
            logger.warning(
                f"PERFORMANCE_REGRESSION: {func_name} "
                f"({elapsed_ms:.2f}ms vs baseline {baseline}ms, "
                f"+{deviation_pct:.1f}% slower)"
            )
            self.deviations.append({
                'function': func_name,
                'elapsed_ms': elapsed_ms,
                'baseline_ms': baseline,
                'deviation_pct': deviation_pct,
                'timestamp': datetime.now()
            })

baseline_tracker = LatencyBaseline()

def log_query_latency_advanced(threshold_ms=500):
    """Enhanced latency logging with baseline comparison"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                func_name = func.__name__
                
                # Check threshold
                if elapsed_ms > threshold_ms:
                    logger.warning(
                        f"SLOW_QUERY: {func_name} took {elapsed_ms:.2f}ms "
                        f"(threshold: {threshold_ms}ms)"
                    )
                
                # Check baseline
                baseline_tracker.check(func_name, elapsed_ms)
                
                # Debug logging
                logger.debug(f"DB_PERF [{func_name}]: {elapsed_ms:.2f}ms")
        
        return wrapper
    return decorator
```

---

## PART 4: Logging Configuration

### Update `logging.yaml` or add to main initialization:

```python
import logging
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout',
        },
        'file_debug': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'logs/db_debug.log',
        },
        'file_slow_queries': {
            'class': 'logging.FileHandler',
            'level': 'WARNING',
            'formatter': 'detailed',
            'filename': 'logs/slow_queries.log',
        },
    },
    'loggers': {
        'backend.db_service': {
            'level': 'DEBUG',
            'handlers': ['console', 'file_debug', 'file_slow_queries'],
            'propagate': False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

---

## PART 5: Sentry Integration (Production)

### Add to Supabase-connected backend initialization:

```python
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
import os

# Initialize Sentry for production monitoring
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,  # Capture all transactions
        
        # Custom transaction filter to only track slow queries
        before_send_transaction=lambda event: event 
            if event.get('measurements', {}).get('duration', 0) > 500 
            else None,
        
        integrations=[
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.WARNING,
            ),
        ],
        
        environment=os.getenv("ENVIRONMENT", "production"),
    )
```

### Log slow queries to Sentry:

```python
def _report_slow_query(func_name, elapsed_ms, threshold_ms):
    """Send slow query to Sentry + custom monitoring"""
    
    # Sentry breadcrumb (lightweight)
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("query_type", func_name)
        scope.set_context("slow_query", {
            "function": func_name,
            "elapsed_ms": elapsed_ms,
            "threshold_ms": threshold_ms,
            "severity": "high" if elapsed_ms > 1000 else "medium",
        })
        
        sentry_sdk.capture_message(
            f"Slow database query: {func_name} ({elapsed_ms:.2f}ms)",
            level="warning"
        )
```

---

## PART 6: Monitoring Dashboard Queries

### Query Supabase logs for slow queries:

```sql
-- List slowest queries in past 24h
SELECT 
    extract(hour from timestamp) as hour,
    query_name,
    avg(duration_ms) as avg_ms,
    max(duration_ms) as max_ms,
    count(*) as num_calls
FROM query_logs
WHERE timestamp > now() - interval '24 hours'
  AND duration_ms > 500
GROUP BY hour, query_name
ORDER BY max_ms DESC;

-- Monitor by function
SELECT 
    query_name,
    count(*) as total_calls,
    sum(case when duration_ms > 500 then 1 else 0 end) as slow_calls,
    (sum(case when duration_ms > 500 then 1 else 0 end)::float / count(*)) * 100 as pct_slow,
    avg(duration_ms) as avg_ms,
    max(duration_ms) as max_ms
FROM query_logs
WHERE timestamp > now() - interval '7 days'
GROUP BY query_name
ORDER BY pct_slow DESC;
```

---

## PART 7: Alert Setup (CloudWatch Example)

### Create CloudWatch alarm for slow queries:

```json
{
  "AlarmName": "db-slow-queries-500ms",
  "MetricName": "SlowQueryCount",
  "Namespace": "G777/Database",
  "Statistic": "Sum",
  "Period": 60,
  "EvaluationPeriods": 1,
  "Threshold": 5,
  "ComparisonOperator": "GreaterThanOrEqualToThreshold",
  "AlarmActions": [
    "arn:aws:sns:eu-west-1:123456789:prod-alerts"
  ],
  "TreatMissingData": "notBreaching"
}
```

---

## PART 8: Testing Latency Instrumentation

### Unit test for timing decorator:

```python
import pytest
import time
from backend.db_service import log_query_latency

def test_latency_logging(caplog):
    """Verify latency decorator logs slow queries"""
    
    @log_query_latency(threshold_ms=100)
    def slow_operation():
        time.sleep(0.15)  # 150ms > 100ms threshold
        return "done"
    
    import logging
    caplog.set_level(logging.WARNING)
    
    result = slow_operation()
    
    assert result == "done"
    assert "SLOW_QUERY" in caplog.text
    assert "150." in caplog.text or "15" in caplog.text  # milliseconds

def test_latency_baseline_tracking():
    """Verify baseline comparison works"""
    from backend.db_service import baseline_tracker
    
    # Simulate slow query (50% deviation)
    baseline_tracker.check('get_customer_by_phone', 75)  # baseline=50, deviation=+50%
    
    assert len(baseline_tracker.deviations) == 1
    assert baseline_tracker.deviations[0]['deviation_pct'] > 30
```

---

## PART 9: Daily Monitoring Checklist

### Morning Report (09:00 UTC)
```bash
#!/bin/bash
# Check overnight slow queries
psql -h aws-1-eu-west-1.pooler.supabase.com \
     -U postgres \
     -d postgres \
     -c "SELECT query_name, max(duration_ms), count(*) FROM query_logs WHERE timestamp > now() - interval '8 hours' AND duration_ms > 500 GROUP BY query_name ORDER BY max_ms DESC LIMIT 10;"
```

### Metrics to Track
- [ ] Total queries per hour
- [ ] % of queries > 500ms
- [ ] Max query latency
- [ ] Avg connection pool utilization
- [ ] Connection pool wait time

### Monthly Review
- [ ] Performance baseline regression analysis
- [ ] Identify most-called slow queries for optimization
- [ ] Index analysis on frequently queried columns
- [ ] Update query hints or materialized views

---

## PART 10: Performance Optimization Tips

### If slow queries detected:

1. **Check index usage:**
   ```sql
   EXPLAIN (ANALYZE, BUFFERS)
   SELECT * FROM customer_profiles WHERE phone = %s AND instance_name = %s;
   ```

2. **Add missing index:**
   ```sql
   CREATE INDEX IF NOT EXISTS idx_customer_profiles_phone_instance 
   ON customer_profiles(phone, instance_name);
   ```

3. **Verify connection pool settings:**
   ```python
   # Current: minconn=1, maxconn=20
   # Supabase pooler recommends: minconn=5, maxconn=30
   self.pool = pool.ThreadedConnectionPool(
       minconn=5,      # Increased
       maxconn=30,     # Increased
       dsn=self.database_url,
       timeout=10      # Add timeout
   )
   ```

4. **Use LIMIT pagination:**
   ```python
   # SLOW: Returns ALL customers
   SELECT * FROM customer_profiles
   
   # FAST: Paginated
   SELECT * FROM customer_profiles LIMIT 100 OFFSET 0
   ```

---

## SUMMARY

**What This Achieves:**
✅ Automatic detection of slow queries (>500ms)  
✅ Historical tracking of query performance  
✅ Alerts to monitoring team  
✅ Foundation for performance optimization  
✅ Compliance with Rule 4  

**Implementation Checklist:**
- [ ] Add latency decorator (Part 1)
- [ ] Apply to all functions (Part 2)
- [ ] Configure logging (Part 4)
- [ ] Set up Sentry (Part 5)
- [ ] Create CloudWatch alarms (Part 7)
- [ ] Write tests (Part 8)
- [ ] Add monitoring checklist (Part 9)

**Estimated Effort:** 1-2 hours  
**Ongoing Monitoring:** 15 min/day

