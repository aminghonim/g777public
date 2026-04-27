#!/bin/bash
# ==============================================================================
# 🛡️ LicenseGuard Live Integration Test (SAAS-018)
# Runs from HOST machine. Tests the full license expiry middleware flow.
# ==============================================================================

set -euo pipefail

BASE_URL="http://127.0.0.1:8081"
SECRET_KEY="g777_super_secret_key_2026"
ALGORITHM="HS256"
LICENSE_KEY="544EC-45EE5-1EEAC-0B4DF"
PSQL_CMD="docker exec g777_postgres psql -U g777_admin -d g777_crm -t -A"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PASS_COUNT=0
FAIL_COUNT=0
TOTAL=0

pass_test() { TOTAL=$((TOTAL+1)); PASS_COUNT=$((PASS_COUNT+1)); echo -e "  ${GREEN}✅ PASS${NC} — $1"; }
fail_test() { TOTAL=$((TOTAL+1)); FAIL_COUNT=$((FAIL_COUNT+1)); echo -e "  ${RED}❌ FAIL${NC} — $1"; echo -e "  ${RED}   Details: $2${NC}"; }

echo "========================================================================"
echo -e "${CYAN}🛡️  LicenseGuard Live Integration Test${NC}"
echo "========================================================================"
echo ""

# ─── Read handshake token ────────────────────────────────────────────────────
HANDSHAKE_TOKEN=$(cat .antigravity/secure_session.json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null || echo "")
if [ -z "$HANDSHAKE_TOKEN" ]; then
    echo -e "${RED}❌ FATAL: Could not read handshake token from session file${NC}"
    exit 1
fi
echo -e "📋 Handshake token: ${HANDSHAKE_TOKEN:0:8}..."
echo ""

# ─── Helper: Create JWT inside backend container ─────────────────────────────
create_jwt() {
    local role="$1"
    local username="$2"
    docker exec g777_backend python3 -c "
from jose import jwt
from datetime import datetime, timedelta
import uuid
payload = {
    'sub': 'test_user',
    'instance_name': 'test_instance',
    'role': '$role',
    'username': '$username',
    'exp': datetime.utcnow() + timedelta(hours=1),
    'iat': datetime.utcnow(),
    'jti': str(uuid.uuid4()),
}
print(jwt.encode(payload, '$SECRET_KEY', algorithm='$ALGORITHM'))
" 2>/dev/null
}

# ─── Helper: Make HTTP request ───────────────────────────────────────────────
http_request() {
    local path="$1"
    local token="${2:-}"
    local method="${3:-GET}"
    local start_time=$(date +%s%N)
    
    if [ -n "$token" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "X-G777-Auth-Token: $HANDSHAKE_TOKEN" \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json" \
            "${BASE_URL}${path}" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "X-G777-Auth-Token: $HANDSHAKE_TOKEN" \
            -H "Content-Type: application/json" \
            "${BASE_URL}${path}" 2>/dev/null)
    fi
    
    local end_time=$(date +%s%N)
    local elapsed=$(( (end_time - start_time) / 1000000 ))
    
    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | sed '$d')
    
    echo "${http_code}|${elapsed}|${body}"
}

# ─── TEST 1: Health Check ────────────────────────────────────────────────────
echo -e "${CYAN}📋 TEST 1: Health Check${NC}"
result=$(http_request "/health")
code=$(echo "$result" | cut -d'|' -f1)
time_ms=$(echo "$result" | cut -d'|' -f2)
if [ "$code" = "200" ]; then
    pass_test "HTTP 200 in ${time_ms}ms"
else
    fail_test "Expected 200, got $code" "$(echo "$result" | cut -d'|' -f3-)"
fi
echo ""

# ─── TEST 2: Guest token endpoint (exempt path) ─────────────────────────────
echo -e "${CYAN}📋 TEST 2: Guest token endpoint (exempt path)${NC}"
result=$(http_request "/auth/license/guest" "" "POST")
code=$(echo "$result" | cut -d'|' -f1)
time_ms=$(echo "$result" | cut -d'|' -f2)
body=$(echo "$result" | cut -d'|' -f3-)
if [ "$code" = "200" ]; then
    has_token=$(echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print('yes' if 'access_token' in d else 'no')" 2>/dev/null || echo "no")
    if [ "$has_token" = "yes" ]; then
        pass_test "HTTP 200 with guest JWT in ${time_ms}ms"
    else
        fail_test "HTTP 200 but no access_token in response" "$body"
    fi
else
    fail_test "Expected 200, got $code" "$body"
fi
echo ""

# ─── TEST 3: Client JWT with ACTIVE license → should PASS ────────────────────
echo -e "${CYAN}📋 TEST 3: Client JWT with ACTIVE license → should allow access${NC}"
CLIENT_JWT=$(create_jwt "client" "$LICENSE_KEY")
if [ -z "$CLIENT_JWT" ]; then
    fail_test "Could not create JWT" "docker exec failed"
    echo ""
else
    result=$(http_request "/api/user/quota" "$CLIENT_JWT")
    code=$(echo "$result" | cut -d'|' -f1)
    time_ms=$(echo "$result" | cut -d'|' -f2)
    body=$(echo "$result" | cut -d'|' -f3-)
    
    # Check that we did NOT get 403 LICENSE_EXPIRED
    is_license_expired="no"
    if [ "$code" = "403" ]; then
        is_license_expired=$(echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print('yes' if d.get('detail')=='LICENSE_EXPIRED' else 'no')" 2>/dev/null || echo "no")
    fi
    
    if [ "$is_license_expired" = "yes" ]; then
        fail_test "LicenseGuard blocked an ACTIVE license!" "$body"
    else
        pass_test "LicenseGuard allowed active license (HTTP $code in ${time_ms}ms)"
    fi
fi
echo ""

# ─── TEST 4: Expire the license in DB ────────────────────────────────────────
echo -e "${CYAN}📋 TEST 4: Expire license in database (set expires_at to 2020-01-01)${NC}"
update_result=$($PSQL_CMD -c "UPDATE licenses SET expires_at = '2020-01-01 00:00:00+00' WHERE license_key = '$LICENSE_KEY';" 2>&1)
if echo "$update_result" | grep -q "UPDATE 1"; then
    pass_test "License expired in DB"
else
    fail_test "Could not expire license in DB" "$update_result"
fi
echo ""

# ─── TEST 5: Client JWT with EXPIRED license → should get 403 ────────────────
echo -e "${CYAN}📋 TEST 5: Client JWT with EXPIRED license → should get 403 LICENSE_EXPIRED${NC}"
CLIENT_JWT_EXPIRED=$(create_jwt "client" "$LICENSE_KEY")
if [ -z "$CLIENT_JWT_EXPIRED" ]; then
    fail_test "Could not create JWT" "docker exec failed"
    echo ""
else
    result=$(http_request "/api/user/quota" "$CLIENT_JWT_EXPIRED")
    code=$(echo "$result" | cut -d'|' -f1)
    time_ms=$(echo "$result" | cut -d'|' -f2)
    body=$(echo "$result" | cut -d'|' -f3-)
    
    is_403_expired="no"
    if [ "$code" = "403" ]; then
        is_403_expired=$(echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print('yes' if d.get('detail')=='LICENSE_EXPIRED' else 'no')" 2>/dev/null || echo "no")
    fi
    
    if [ "$is_403_expired" = "yes" ]; then
        reason=$(echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('reason',''))" 2>/dev/null || echo "")
        days_expired=$(echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('days_expired',''))" 2>/dev/null || echo "")
        message=$(echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message',''))" 2>/dev/null || echo "")
        pass_test "403 LICENSE_EXPIRED (reason=$reason, days_expired=$days_expired) in ${time_ms}ms"
        echo -e "  ${YELLOW}   Reason: $reason${NC}"
        echo -e "  ${YELLOW}   Days expired: $days_expired${NC}"
        echo -e "  ${YELLOW}   Message: $message${NC}"
    else
        fail_test "Expected 403 LICENSE_EXPIRED, got HTTP $code" "$body"
    fi
fi
echo ""

# ─── TEST 6: Deactivated license → should get 403 ───────────────────────────
echo -e "${CYAN}📋 TEST 6: Deactivated license → should get 403 LICENSE_DEACTIVATED${NC}"
$PSQL_CMD -c "UPDATE licenses SET is_active = false, expires_at = '2027-01-01 00:00:00+00' WHERE license_key = '$LICENSE_KEY';" >/dev/null 2>&1

CLIENT_JWT_DEACT=$(create_jwt "client" "$LICENSE_KEY")
if [ -z "$CLIENT_JWT_DEACT" ]; then
    fail_test "Could not create JWT" "docker exec failed"
    echo ""
else
    result=$(http_request "/api/user/quota" "$CLIENT_JWT_DEACT")
    code=$(echo "$result" | cut -d'|' -f1)
    time_ms=$(echo "$result" | cut -d'|' -f2)
    body=$(echo "$result" | cut -d'|' -f3-)
    
    is_403_deactivated="no"
    if [ "$code" = "403" ]; then
        is_403_deactivated=$(echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print('yes' if d.get('reason')=='license_deactivated' else 'no')" 2>/dev/null || echo "no")
    fi
    
    if [ "$is_403_deactivated" = "yes" ]; then
        pass_test "403 LICENSE_DEACTIVATED in ${time_ms}ms"
    else
        fail_test "Expected 403 with reason=license_deactivated, got HTTP $code" "$body"
    fi
fi
echo ""

# ─── TEST 7: Admin role bypasses license check ───────────────────────────────
echo -e "${CYAN}📋 TEST 7: Admin role bypasses license check (even with deactivated license)${NC}"
ADMIN_JWT=$(create_jwt "admin" "$LICENSE_KEY")
if [ -z "$ADMIN_JWT" ]; then
    fail_test "Could not create JWT" "docker exec failed"
    echo ""
else
    result=$(http_request "/api/user/quota" "$ADMIN_JWT")
    code=$(echo "$result" | cut -d'|' -f1)
    time_ms=$(echo "$result" | cut -d'|' -f2)
    body=$(echo "$result" | cut -d'|' -f3-)
    
    is_blocked_by_license="no"
    if [ "$code" = "403" ]; then
        is_blocked_by_license=$(echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print('yes' if d.get('detail')=='LICENSE_EXPIRED' else 'no')" 2>/dev/null || echo "no")
    fi
    
    if [ "$is_blocked_by_license" = "yes" ]; then
        fail_test "Admin was blocked by LicenseGuard!" "$body"
    else
        pass_test "Admin bypassed license check (HTTP $code in ${time_ms}ms)"
    fi
fi
echo ""

# ─── RESTORE: Reactivate the license ─────────────────────────────────────────
echo -e "${YELLOW}📋 RESTORE: Reactivating license in database${NC}"
restore_result=$($PSQL_CMD -c "UPDATE licenses SET is_active = true, expires_at = '2026-05-26 06:42:15+00' WHERE license_key = '$LICENSE_KEY';" 2>&1)
if echo "$restore_result" | grep -q "UPDATE 1"; then
    echo -e "  ${GREEN}✅ License restored to active state${NC}"
else
    echo -e "  ${RED}⚠️  Could not restore license: $restore_result${NC}"
fi
echo ""

# ─── Summary ─────────────────────────────────────────────────────────────────
echo "========================================================================"
echo -e "${CYAN}📊 TEST SUMMARY${NC}"
echo "========================================================================"
echo ""
echo -e "  Total:  $TOTAL"
echo -e "  Passed: ${GREEN}$PASS_COUNT${NC}"
echo -e "  Failed: ${RED}$FAIL_COUNT${NC}"
echo ""

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! LicenseGuard is working correctly.${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Review the output above.${NC}"
    exit 1
fi
