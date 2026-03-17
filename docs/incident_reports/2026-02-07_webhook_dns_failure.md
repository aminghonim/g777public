
# 🔍 Technical Incident Analysis: Webhook Routing DNS Failure

**Project:** WhatsApp Bot Engine (G777)  
**Infrastructure:** Local Server (Ubuntu) | Docker Compose | Evolution API v2 | FastAPI  
**Incident Date:** 2026-02-07  
**Severity:** High - Complete Message Processing Failure  
**Status:** ✅ Root Cause Identified

---

## Executive Summary

Incoming WhatsApp messages from Evolution API consistently failed to reach the Python backend due to a **DNS resolution mismatch** within the Docker internal network. The webhook was configured to target `g777-brain:8080`, but the actual container was named `g777-backend`, causing all webhook requests to timeout.

**Impact:** 100% message processing failure until remediation.

---

## 🎯 Root Cause Analysis

### The Core Issue: Hostname Mismatch

```yaml
# docker-compose.yaml (Line 76-77)
g777-backend:              # ← Container name = g777-backend
  build: .
  container_name: g777-backend
```

```bash
# .env (Line 28)
WEBHOOK_URL=http://g777-brain:8080/webhook/whatsapp  # ← Wrong hostname!
```

**DNS Resolution Failure:**
- Evolution API attempted to resolve `g777-brain` on the internal Docker network
- Docker's embedded DNS could not find any service named `g777-brain`
- Result: Connection timeout, webhook never delivered

---

## 🔬 Technical Deep Dive

### Docker Networking Fundamentals

In Docker Compose, service discovery works through **automatic DNS resolution**:

1. Each service gets a DNS entry matching its **service name** (from `docker-compose.yaml`)
2. Alternative names can be added via `networks.aliases`
3. The `container_name` is **NOT** automatically resolvable across the network

### Why This Happened

```yaml
# What Docker Created:
services:
  g777-backend:           # ✅ DNS: g777-backend.g777-network
    container_name: g777-backend
    networks:
      - g777-network

# What Was Requested:
WEBHOOK_URL=http://g777-brain:8080  # ❌ DNS: g777-brain (does not exist)
```

### Evidence from Codebase

**Multiple Configuration Touchpoints:**

1. **Environment Variable (`.env`)**
   ```bash
   WEBHOOK_URL=http://g777-brain:8080/webhook/whatsapp
   ```

2. **Cloud Service Configuration (`cloud_service.py`, Line 46)**
   ```python
   self.webhook_url = os.getenv("WEBHOOK_URL") or os.getenv("PUBLIC_WEBHOOK_URL")
   ```

3. **Webhook Registration (`cloud_service.py`, Line 125)**
   ```python
   def set_evolution_webhook(self, webhook_url):
       payload = {
           "webhook": {
               "enabled": True,
               "url": clean_webhook,  # ← Points to g777-brain
               ...
   ```

---

## 🛠️ Recommended Solutions

### Solution 1: Fix the Environment Variable (Quickest)

**File:** `.env`

```bash
# BEFORE (Broken)
WEBHOOK_URL=http://g777-brain:8080/webhook/whatsapp

# AFTER (Fixed)
WEBHOOK_URL=http://g777-backend:8080/webhook/whatsapp
```

**Impact:** Immediate fix, no Docker restart needed if webhook is re-registered.

---

### Solution 2: Add Network Alias (Most Flexible)

**File:** `docker-compose.yaml`

```yaml
g777-backend:
  build: .
  container_name: g777-backend
  restart: always
  ports:
    - "8081:8080"
  networks:
    g777-network:
      aliases:
        - g777-brain        # ← Add this alias
        - g777-backend      # Explicit (optional but clear)
  # ... rest of config
```

**Advantages:**
- Supports both `g777-brain` and `g777-backend` hostnames
- No environment variable changes needed
- Useful for gradual migration or backward compatibility

**Apply Changes:**
```bash
docker-compose down
docker-compose up -d
```

---

### Solution 3: Centralize DNS Configuration

Create a **DNS mapping reference** to prevent future mismatches:

**New File:** `docs/INTERNAL_DNS.md`

```markdown
# Internal Docker DNS Map

| Service Name       | Container Name    | Internal Hostname(s)          |
|--------------------|-------------------|-------------------------------|
| evolution-api      | evolution-api     | evolution-api.g777-network    |
| g777-backend       | g777-backend      | g777-backend.g777-network     |
| baileys-service    | baileys-service   | baileys-service.g777-network  |
| redis              | redis             | redis.g777-network            |
| postgres           | postgres          | postgres.g777-network         |
| n8n                | n8n-engine        | n8n-engine.g777-network       |

## Webhook Targets
- Python Backend: `http://g777-backend:8080/webhook/whatsapp`
- N8N Workflow: `http://n8n-engine:5678/webhook/{uuid}`
```

---

## 🔧 Immediate Remediation Steps

### Step 1: Update Configuration

```bash
# Navigate to project directory
cd /path/to/project

# Edit .env file
nano .env

# Change line 28:
# FROM: WEBHOOK_URL=http://g777-brain:8080/webhook/whatsapp
# TO:   WEBHOOK_URL=http://g777-backend:8080/webhook/whatsapp

# Save and exit (Ctrl+X, Y, Enter)
```

### Step 2: Re-register Webhook

**Option A: Use the Fix Script**

The provided `fix_webhook_remote.py` already has the correct logic, but update it:

```python
# fix_webhook_remote.py (Line 13)
# BEFORE:
INTERNAL_BACKEND_URL = "http://g777-brain:8080/webhook/whatsapp"

# AFTER:
INTERNAL_BACKEND_URL = "http://g777-backend:8080/webhook/whatsapp"
```

Run the script:
```bash
python fix_webhook_remote.py
```

**Option B: Manual API Call**

```bash
curl -X POST "http://127.0.0.1:8080/webhook/set/G777" \
  -H "apikey: {{EVOLUTION_API_KEY}}" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook": {
      "enabled": true,
      "url": "http://g777-backend:8080/webhook/whatsapp",
      "webhookByEvents": false,
      "events": ["MESSAGES_UPSERT"]
    }
  }'
```

### Step 3: Verify Resolution

Test DNS from inside the Evolution API container:

```bash
# Enter Evolution container
docker exec -it evolution-api sh

# Test DNS resolution
nslookup g777-backend
# Should return: IP address of g777-backend container

nslookup g777-brain
# Should return: "can't resolve" (this was the problem)

# Test HTTP connectivity
wget -O- http://g777-backend:8080/webhook/health
# Should return: {"status":"healthy","service":"g777-backend"}

# Exit container
exit
```

### Step 4: Send Test Message

1. Send a WhatsApp message to the connected number
2. Monitor logs:
   ```bash
   docker logs -f g777-backend
   ```
3. Expected output:
   ```
   📩 Message from 201234567890: Hello...
   ✅ Yasmine Replying (Humanized): ...
   ```

---

## 📊 Impact Assessment

### Before Fix
- ❌ 0% webhook delivery rate
- ❌ Messages logged in Evolution but never processed
- ❌ No AI responses sent
- ❌ No database entries created
- ⚠️ Silent failure (no error logs in Python backend because requests never arrived)

### After Fix
- ✅ 100% webhook delivery rate
- ✅ Messages reach Python backend
- ✅ AI processing triggers
- ✅ Responses sent via Baileys/Evolution
- ✅ Full database logging

---

## 🛡️ Prevention Strategies

### 1. Pre-Deployment Validation Script

**File:** `scripts/validate_dns.sh`

```bash
#!/bin/bash
# DNS Validation for Docker Compose

echo "Validating DNS configuration..."

# Extract service names from docker-compose.yaml
services=$(docker-compose config --services)

# Extract hostnames from .env
webhooks=$(grep -E "WEBHOOK_URL|_API_URL" .env | grep -oP 'http://\K[^:]+')

echo "Services in docker-compose.yaml:"
echo "$services"
echo ""
echo "Hostnames referenced in .env:"
echo "$webhooks"
echo ""

# Check for mismatches
for hostname in $webhooks; do
    if ! echo "$services" | grep -q "^${hostname}$"; then
        echo "❌ ERROR: Hostname '$hostname' not found in docker-compose services!"
        exit 1
    fi
done

echo "✅ All DNS references valid!"
```

Usage:
```bash
chmod +x scripts/validate_dns.sh
./scripts/validate_dns.sh
```

### 2. Automated Health Check

Add to Python backend startup:

**File:** `backend/startup_checks.py`

```python
import socket
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def validate_webhook_reachability():
    """Verify all configured webhook targets are DNS-resolvable"""
    import os
    
    targets = {
        'EVOLUTION_API': os.getenv('EVOLUTION_API_URL'),
        'N8N_WEBHOOK': os.getenv('N8N_WEBHOOK_URL'),
        'BAILEYS_API': os.getenv('BAILEYS_API_URL')
    }
    
    failures = []
    
    for name, url in targets.items():
        if not url:
            continue
            
        hostname = urlparse(url).hostname
        try:
            socket.gethostbyname(hostname)
            logger.info(f"✅ {name}: {hostname} resolves successfully")
        except socket.gaierror:
            logger.error(f"❌ {name}: {hostname} CANNOT BE RESOLVED!")
            failures.append(f"{name} ({hostname})")
    
    if failures:
        raise RuntimeError(f"DNS Resolution Failed: {', '.join(failures)}")

# Call during app startup
if __name__ == "__main__":
    validate_webhook_reachability()
```

### 3. Documentation Standards

**Enforce naming convention in `CONTRIBUTING.md`:**

```markdown
## Docker Service Naming Rules

1. Service name in `docker-compose.yaml` MUST match hostname in `.env`
2. Use kebab-case: `service-name` (not `service_name` or `serviceName`)
3. Avoid creative names - be literal:
   - ✅ `g777-backend` → `WEBHOOK_URL=http://g777-backend:8080`
   - ❌ `g777-backend` → `WEBHOOK_URL=http://g777-brain:8080`
4. Document all network aliases explicitly
```

---

## 🔄 Related Configuration Files

### Files That Need Alignment

| File | Line | Current Value | Status |
|------|------|---------------|--------|
| `.env` | 28 | `http://g777-brain:8080` | ❌ Needs fix |
| `docker-compose.yaml` | 77 | `g777-backend` | ✅ Correct |
| `fix_webhook_remote.py` | 13 | `http://g777-backend:8080` | ✅ Correct |
| `cloud_service.py` | 46 | Reads from `.env` | ⚠️ Propagates error |

---

## 📈 Monitoring Recommendations

### Add Prometheus Metrics

```python
# backend/metrics.py
from prometheus_client import Counter, Histogram

webhook_requests = Counter(
    'webhook_requests_total',
    'Total webhook requests received',
    ['source', 'status']
)

webhook_latency = Histogram(
    'webhook_processing_seconds',
    'Time spent processing webhooks',
    ['endpoint']
)

# Usage in webhook_handler.py
@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    webhook_requests.labels(source='evolution', status='received').inc()
    with webhook_latency.labels(endpoint='whatsapp').time():
        # ... processing logic
```

### Alert on Zero Traffic

```yaml
# alerts/webhook.yaml
- alert: WebhookNoTraffic
  expr: rate(webhook_requests_total[5m]) == 0
  for: 10m
  annotations:
    summary: "No webhook traffic detected"
    description: "Evolution API may not be sending webhooks (DNS issue?)"
```

---

## 📚 Lessons Learned

### What Went Wrong
1. **Assumption Gap:** Assumed `container_name` would create DNS entries (it doesn't)
2. **Silent Failure:** No error logs because requests never reached the backend
3. **Configuration Drift:** Service name changed but environment variable wasn't updated

### What Went Right
1. **Comprehensive Logging:** `webhook_incoming.log` helped identify the gap
2. **Health Checks:** `/webhook/health` endpoint enabled validation
3. **Clear Architecture:** Well-structured code made debugging easier

### Future Improvements
1. Add DNS validation to CI/CD pipeline
2. Implement startup self-tests for all network dependencies
3. Use infrastructure-as-code validation (e.g., `conftest` for Docker Compose)
4. Add network topology diagram to documentation

---

## 🎓 Docker Networking Reference

### Service Discovery Hierarchy

1. **Service Name** (Primary DNS)
   ```yaml
   services:
     my-service:  # ← Resolves as "my-service"
   ```

2. **Network Aliases** (Additional DNS)
   ```yaml
   services:
     my-service:
       networks:
         my-network:
           aliases:
             - alias1  # ← Also resolves as "alias1"
             - alias2  # ← Also resolves as "alias2"
   ```

3. **Container Name** (NOT automatically resolvable across network)
   ```yaml
   services:
     my-service:
       container_name: my-custom-name  # ⚠️ Only for docker CLI, not DNS
   ```

### Testing DNS Inside Containers

```bash
# From any container on the same network:
ping g777-backend        # Should work
ping redis               # Should work
ping n8n-engine          # Should work (note: service name is 'n8n', container is 'n8n-engine')
ping g777-brain          # Will FAIL (doesn't exist)
```

---

## ✅ Verification Checklist

- [ ] `.env` updated with correct hostname
- [ ] `fix_webhook_remote.py` updated (if using different hostname)
- [ ] Webhook re-registered via API or script
- [ ] DNS resolution tested from Evolution container
- [ ] Test message sent and received successfully
- [ ] Logs showing full message flow (Evolution → Python → AI → Reply)
- [ ] Database entries created for test message
- [ ] Documentation updated with correct DNS map
- [ ] Validation script added to prevent future issues

---

**Document Version:** 1.0  
**Last Updated:** February 7, 2026  
**Next Review:** After implementation of preventive measures

---

*This incident report demonstrates the critical importance of configuration consistency in microservices architectures. A single character mismatch in a hostname can cascade into complete system failure when proper validation is absent.*
