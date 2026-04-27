#!/usr/bin/env python3
"""
Live Integration Test for License Expiry Middleware (LicenseGuard)
SAAS-018: Verifies that expired licenses are blocked with 403 LICENSE_EXPIRED.

Runs INSIDE the backend container where all dependencies (jose, bcrypt, etc.) are available.
Usage: docker exec g777_backend python /app/scripts/live_license_guard_test.py
"""

import json
import sys
import time
import logging
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from jose import jwt

logger = logging.getLogger("license-guard-test")

# ─── Configuration ───────────────────────────────────────────────────────────
SECRET_KEY = "g777_super_secret_key_2026"
ALGORITHM = "HS256"
BASE_URL = "http://127.0.0.1:8081"
HANDSHAKE_TOKEN = None  # Read from session file at runtime

# Test license key (matches existing DB record)
EXISTING_LICENSE_KEY = "544EC-45EE5-1EEAC-0B4DF"

# ─── Helpers ─────────────────────────────────────────────────────────────────

def read_handshake_token():
    """Read the handshake token from the session file."""
    try:
        with open("/app/.antigravity/secure_session.json", "r") as f:
            data = json.load(f)
            return data.get("token", "")
    except Exception as e:
        logger.warning("Could not read session file: %s", e)
        return ""


def create_test_jwt(role: str, username: str, sub: str = "test_user", instance_name: str = "test_instance") -> str:
    """Create a JWT token with the given claims."""
    expire = datetime.utcnow() + timedelta(hours=1)
    payload = {
        "sub": sub,
        "instance_name": instance_name,
        "role": role,
        "username": username,
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": "test-integration-jti",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def make_request(path: str, token: str = None, method: str = "GET") -> dict:
    """Make an HTTP request and return status code + response body."""
    url = f"{BASE_URL}{path}"
    headers = {}
    
    if HANDSHAKE_TOKEN:
        headers["X-G777-Auth-Token"] = HANDSHAKE_TOKEN
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    req = urllib.request.Request(url, headers=headers, method=method)
    
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            elapsed = time.time() - start
            body = json.loads(resp.read().decode())
            return {"status": resp.status, "body": body, "time": elapsed}
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        try:
            body = json.loads(e.read().decode())
        except Exception:
            body = {"raw": str(e)}
        return {"status": e.code, "body": body, "time": elapsed}
    except Exception as e:
        elapsed = time.time() - start
        return {"status": 0, "body": {"error": str(e)}, "time": elapsed}


def run_sql(sql: str) -> dict:
    """Execute SQL via the backend's database_manager."""
    import subprocess
    result = subprocess.run(
        ["psql", "-U", "g777_admin", "-d", "g777_crm", "-c", sql, "-t", "-A"],
        capture_output=True, text=True, timeout=10,
        env={"PGPASSWORD": "G777SecureDB2026", "PATH": "/usr/bin:/bin"}
    )
    return {"stdout": result.stdout.strip(), "stderr": result.stderr.strip(), "returncode": result.returncode}


# ─── Test Runner ─────────────────────────────────────────────────────────────

def main():
    global HANDSHAKE_TOKEN
    
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    logger.info("=" * 70)
    logger.info("LicenseGuard Live Integration Test")
    logger.info("=" * 70)
    
    results = []
    
    # Read handshake token
    HANDSHAKE_TOKEN = read_handshake_token()
    if not HANDSHAKE_TOKEN:
        logger.error("FATAL: Could not read handshake token from session file")
        sys.exit(1)
    logger.info("Handshake token: %s...", HANDSHAKE_TOKEN[:8])
    
    # ─── TEST 1: Health Check ────────────────────────────────────────────
    logger.info("TEST 1: Health Check")
    r = make_request("/health")
    passed = r["status"] == 200
    results.append(("Health Check", passed, r))
    logger.info("  Status: %s | Time: %.2fs | %s", r['status'], r['time'], 'PASS' if passed else 'FAIL')
    if not passed:
        logger.info("  Body: %s", r['body'])
    
    # ─── TEST 2: Guest token on exempt path ──────────────────────────────
    logger.info("TEST 2: Guest token endpoint (exempt path)")
    r = make_request("/auth/license/guest")
    passed = r["status"] == 200
    results.append(("Guest Token Endpoint", passed, r))
    logger.info("  Status: %s | Time: %.2fs | %s", r['status'], r['time'], 'PASS' if passed else 'FAIL')
    if passed and "access_token" in r.get("body", {}):
        logger.info("  Got guest JWT (first 20 chars): %s...", r['body']['access_token'][:20])
    
    # ─── TEST 3: Client JWT with ACTIVE license → should PASS ────────────
    logger.info("TEST 3: Client JWT with ACTIVE license → should allow access")
    client_jwt = create_test_jwt(role="client", username=EXISTING_LICENSE_KEY)
    r = make_request("/api/user/quota", token=client_jwt)
    is_not_license_expired = r["status"] != 403 or r.get("body", {}).get("detail") != "LICENSE_EXPIRED"
    passed = is_not_license_expired
    results.append(("Active License - Access Allowed", passed, r))
    logger.info("  Status: %s | Time: %.2fs | %s", r['status'], r['time'], 'PASS' if passed else 'FAIL')
    if r["status"] == 403 and r.get("body", {}).get("detail") == "LICENSE_EXPIRED":
        logger.error("  UNEXPECTED: LicenseGuard blocked an ACTIVE license!")
        logger.info("  Body: %s", r['body'])
    elif r["status"] in (200, 401, 404, 422):
        logger.info("  LicenseGuard did NOT block (status %s is from route-level, not license check)", r['status'])
    else:
        logger.info("  Body: %s", r['body'])
    
    # ─── TEST 4: Expire the license in DB ────────────────────────────────
    logger.info("TEST 4: Expiring license in database (set expires_at to past)")
    import subprocess
    expire_result = subprocess.run(
        [
            "docker", "exec", "g777_postgres", "psql",
            "-U", "g777_admin", "-d", "g777_crm", "-c",
            f"UPDATE licenses SET expires_at = '2020-01-01 00:00:00+00' WHERE license_key = '{EXISTING_LICENSE_KEY}';"
        ],
        capture_output=True, text=True, timeout=10
    )
    expire_ok = "UPDATE 1" in expire_result.stdout
    results.append(("Expire License in DB", expire_ok, {"stdout": expire_result.stdout, "stderr": expire_result.stderr}))
    logger.info("  Result: %s | %s", expire_result.stdout.strip(), 'PASS' if expire_ok else 'FAIL')
    if expire_result.stderr:
        logger.info("  Stderr: %s", expire_result.stderr.strip())
    
    # ─── TEST 5: Client JWT with EXPIRED license → should get 403 ────────
    logger.info("TEST 5: Client JWT with EXPIRED license → should get 403 LICENSE_EXPIRED")
    client_jwt_expired = create_test_jwt(role="client", username=EXISTING_LICENSE_KEY)
    r = make_request("/api/user/quota", token=client_jwt_expired)
    is_403_license_expired = (
        r["status"] == 403 
        and r.get("body", {}).get("detail") == "LICENSE_EXPIRED"
    )
    passed = is_403_license_expired
    results.append(("Expired License - 403 LICENSE_EXPIRED", passed, r))
    logger.info("  Status: %s | Time: %.2fs | %s", r['status'], r['time'], 'PASS' if passed else 'FAIL')
    if passed:
        logger.info("  LicenseGuard correctly blocked expired license!")
        logger.info("  Detail: %s", r['body'].get('detail'))
        logger.info("  Reason: %s", r['body'].get('reason'))
        logger.info("  Days expired: %s", r['body'].get('days_expired'))
        logger.info("  Message: %s", r['body'].get('message'))
    else:
        logger.error("  Expected 403 LICENSE_EXPIRED, got status %s", r['status'])
        logger.info("  Body: %s", r['body'])
    
    # ─── TEST 6: Deactivated license → should get 403 ────────────────────
    logger.info("TEST 6: Deactivated license → should get 403 LICENSE_DEACTIVATED")
    deactivate_result = subprocess.run(
        [
            "docker", "exec", "g777_postgres", "psql",
            "-U", "g777_admin", "-d", "g777_crm", "-c",
            f"UPDATE licenses SET is_active = false, expires_at = '2027-01-01 00:00:00+00' WHERE license_key = '{EXISTING_LICENSE_KEY}';"
        ],
        capture_output=True, text=True, timeout=10
    )
    logger.info("  Deactivated license: %s", deactivate_result.stdout.strip())
    
    client_jwt_deactivated = create_test_jwt(role="client", username=EXISTING_LICENSE_KEY)
    r = make_request("/api/user/quota", token=client_jwt_deactivated)
    is_403_deactivated = (
        r["status"] == 403 
        and r.get("body", {}).get("detail") == "LICENSE_EXPIRED"
        and r.get("body", {}).get("reason") == "license_deactivated"
    )
    passed = is_403_deactivated
    results.append(("Deactivated License - 403 LICENSE_DEACTIVATED", passed, r))
    logger.info("  Status: %s | Time: %.2fs | %s", r['status'], r['time'], 'PASS' if passed else 'FAIL')
    if r["status"] == 403:
        logger.info("  Detail: %s", r['body'].get('detail'))
        logger.info("  Reason: %s", r['body'].get('reason'))
    else:
        logger.info("  Body: %s", r['body'])
    
    # ─── TEST 7: Admin role bypasses license check ───────────────────────
    logger.info("TEST 7: Admin role bypasses license check (even with expired license)")
    admin_jwt = create_test_jwt(role="admin", username=EXISTING_LICENSE_KEY)
    r = make_request("/api/user/quota", token=admin_jwt)
    is_not_403_license = r["status"] != 403 or r.get("body", {}).get("detail") != "LICENSE_EXPIRED"
    passed = is_not_403_license
    results.append(("Admin Role Bypass", passed, r))
    logger.info("  Status: %s | Time: %.2fs | %s", r['status'], r['time'], 'PASS' if passed else 'FAIL')
    if passed:
        logger.info("  Admin bypassed license check (got %s, not 403 LICENSE_EXPIRED)", r['status'])
    else:
        logger.error("  Admin was blocked by LicenseGuard!")
    
    # ─── RESTORE: Reactivate the license ─────────────────────────────────
    logger.info("RESTORE: Reactivating license in database")
    restore_result = subprocess.run(
        [
            "docker", "exec", "g777_postgres", "psql",
            "-U", "g777_admin", "-d", "g777_crm", "-c",
            f"UPDATE licenses SET is_active = true, expires_at = '2026-05-26 06:42:15+00' WHERE license_key = '{EXISTING_LICENSE_KEY}';"
        ],
        capture_output=True, text=True, timeout=10
    )
    logger.info("  Result: %s", restore_result.stdout.strip())
    
    # ─── Summary ─────────────────────────────────────────────────────────
    logger.info("=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    total = len(results)
    passed_count = sum(1 for _, p, _ in results if p)
    failed_count = total - passed_count
    
    for name, passed, r in results:
        status_icon = "PASS" if passed else "FAIL"
        http_status = r.get("status", "N/A")
        logger.info("  [%s] %s (HTTP %s)", status_icon, name, http_status)
    
    logger.info("")
    logger.info("  Total: %s | Passed: %s | Failed: %s", total, passed_count, failed_count)
    
    if failed_count == 0:
        logger.info("ALL TESTS PASSED! LicenseGuard is working correctly.")
        sys.exit(0)
    else:
        logger.warning("Some tests failed. Review the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
