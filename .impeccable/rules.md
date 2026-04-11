## Checkpoint: RTK + SmartFilter Integration Compliance

**Purpose:** Verify that RTK token optimization and SmartOutputFilter compliance
are maintained across all commits. Prevents regression of token savings and
audit trail functionality.

**Frequency:** Every commit to `backend/` directory touching `tools/`, `executors/`,
or `mcp_server/`.

---

### Phase 1: Pre-Execution Validation (form_impeccable_squad)

```bash
✓ RTK binary installed and accessible
  rtk --version
  # Expected: rtk 0.35.0 (or higher)

✓ RTK hook initialized for Claude Code
  rtk init --show
  # Expected: Hook installed = true

✓ RTK telemetry disabled
  echo $RTK_TELEMETRY_DISABLED
  # Expected: 1
```

**Checkpoint Gate:**
- [ ] RTK version >= 0.35.0
- [ ] Hook initialization shows "installed = true"
- [ ] RTK_TELEMETRY_DISABLED environment variable set

---

### Phase 2: Code Audit (run_impeccable_audit)

**Scan 1: No Direct subprocess Calls in Agent Tools**

```bash
grep -r "subprocess.run\|subprocess.Popen" \
  backend/tools/ \
  backend/mcp_server/ \
  --include="*.py" \
  --exclude="test_*.py"

# Expected output: EMPTY (no matches)
```

**Scan 2: All SystemCommandExecutor Calls Have instance_name**

```bash
grep -r "SystemCommandExecutor(" \
  backend/ \
  --include="*.py" | \
  grep -v "instance_name"

# Expected output: EMPTY (no matches without instance_name)
```

**Scan 3: All SystemCommandExecutor.execute() Calls Are Awaited**

```bash
grep -r "executor.execute\|\.execute(" \
  backend/ \
  --include="*.py" | \
  grep -v "await"

# Expected output: EMPTY (all calls are awaited)
```

**Checkpoint Gate:**
- [ ] No direct subprocess in agent-facing tools
- [ ] All SystemCommandExecutor calls include instance_name parameter
- [ ] All executor.execute() calls use `await`

---

### Phase 3: Unit Test Verification (verify_regression_lock)

**Test Suite: SmartOutputFilter**

```bash
cd backend/
pytest tests/test_output_filter.py -v

# Expected: 19/19 PASSED in ~0.2s
```

**Test Suite: SystemCommandExecutor**

```bash
cd backend/
pytest tests/test_system_commands.py -v

# Expected: All tests PASSED
```

**Specific Test Cases to Verify:**

```python
pytest tests/test_output_filter.py::test_critical_errors_preserved
pytest tests/test_output_filter.py::test_error_keywords_not_filtered
pytest tests/test_output_filter.py::test_sensitive_data_redacted
pytest tests/test_output_filter.py::test_compression_ratio_positive
pytest tests/test_output_filter.py::test_audit_trail_complete
```

**Checkpoint Gate:**
- [ ] test_output_filter.py: 19/19 PASSED
- [ ] test_system_commands.py: All PASSED
- [ ] No test failures or warnings

---

### Phase 4: Integration Check (generate_checkpoint_gate)

**Real-World Compression Test**

```bash
# Test on actual git repository
cd backend/
executor = SystemCommandExecutor("checkpoint_test")
result = await executor.execute("git status")

# Verify compression ratio
echo "Compression Ratio: $(result['metadata']['compression_ratio'])"
# Expected: >= 0.3 (at least 30% reduction for git status)
```

**Verify Audit Trail Logging**

```python
# Check that audit_trail was recorded
assert len(result['metadata']['audit_trail']) > 0
assert all('reason' in entry for entry in result['metadata']['audit_trail'])
assert all('signal_type' in entry for entry in result['metadata']['audit_trail'])

# Expected: Full audit trail present with all required fields
```

**Verify Tenant Isolation**

```python
# instance_name must be in metadata
assert result['metadata']['instance_name'] == "checkpoint_test"

# Expected: Tenant context preserved throughout filtering pipeline
```

**Verify Sensitive Data Redaction**

```python
# If sensitive data is detected, it must be redacted
if result['metadata']['sensitive_data_detected']:
    assert "[REDACTED]" in result['output']
    assert "password" not in result['output'].lower()
    assert "secret" not in result['output'].lower()

# Expected: All sensitive patterns automatically redacted
```

**Checkpoint Gate:**
- [ ] Compression ratio >= 30% for typical commands
- [ ] Audit trail has entries with signal_type and reason
- [ ] instance_name preserved in metadata
- [ ] No unredacted sensitive data in output

---

### Phase 5: Regression Prevention (generate_checkpoint_gate - continued)

**Docker Build Verification**

```bash
docker build -t g777:test .

# Inside container, verify:
docker run g777:test rtk --version
# Expected: rtk 0.35.0+

docker run g777:test python -c "
from backend.core.system_commands import SystemCommandExecutor
from backend.core.output_filter import SmartOutputFilter
print('Imports successful')
"
# Expected: "Imports successful" (no import errors)
```

**Compression Ratio Benchmark**

```bash
# Run benchmark on common commands
echo "=== git status ==="
rtk git status | wc -c  # Should be << standard output

echo "=== pytest (simulated) ==="
# [Run pytest with RTK and compare output sizes]

echo "=== docker ps ==="
rtk docker ps | wc -c  # Should be << standard output
```

**Checkpoint Gate:**
- [ ] Docker build succeeds
- [ ] RTK binary available in container
- [ ] SmartOutputFilter imports successfully
- [ ] Compression ratio benchmarks are consistent with Phase 1
