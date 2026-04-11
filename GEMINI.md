# G777 AI Agent Configuration

> This file defines operational rules for AI agents interacting with the
> G777 codebase. All agents MUST follow these directives.

---

## RTK Token Optimization Protocol

### Overview

RTK (Runtime Toolkit) is a Rust CLI proxy that rewrites shell commands
transparently to reduce LLM token consumption by 60-90%. Combined with
the G777 SmartOutputFilter, it provides compression with full auditability.

**Current Status:**
- RTK v0.35.0 installed and operational
- SmartOutputFilter with 19/19 unit tests passing
- Real-world compression: 94.3% on `git status`
- Zero critical data loss guarantee via priority-ordered classification

### Architecture

```
Agent Command Request
    |
    v
[SystemCommandExecutor]         -- Tenant isolation + RTK detection
    |
    v
[RTK Hook - Transparent]        -- git status -> rtk git status (automatic)
    |
    v
[System Execution]              -- Run command in shell
    |
    v
[RTK Output Compression]        -- 60-90% token reduction
    |
    v
[SmartOutputFilter]             -- Audit trail + sensitive data redaction
    |
    v
[Agent Receives Output]         -- Compressed + fully auditable
```

---

### Rule 1: SystemCommandExecutor REQUIRED

All shell command execution in agent-facing tools MUST go through
`SystemCommandExecutor`. Direct `subprocess.run()` is forbidden in
any tool that returns output to an AI agent.

```python
# FORBIDDEN:
result = subprocess.run(command, shell=True, ...)

# REQUIRED:
from backend.core.system_commands import SystemCommandExecutor

executor = SystemCommandExecutor(self.instance_name)
result = await executor.execute(command)
```

**Rationale:** SystemCommandExecutor ensures tenant isolation, automatic
RTK detection, SmartOutputFilter compliance, and structured audit trails.

### Rule 2: instance_name Must Be Passed

Every executor instance MUST receive a tenant identifier.

```python
# FORBIDDEN:
executor = SystemCommandExecutor("")

# REQUIRED:
executor = SystemCommandExecutor(self.instance_name)
```

**Rationale:** Tenant isolation in multi-tenant environments. Audit trails
are meaningless without instance context.

### Rule 3: Async/Await Pattern

All tool methods that call SystemCommandExecutor MUST be async.

```python
# FORBIDDEN:
def execute(self, command: str):
    result = subprocess.run(...)  # Blocks the event loop

# REQUIRED:
async def execute(self, command: str):
    result = await executor.execute(command)  # Non-blocking
```

**Rationale:** SystemCommandExecutor uses `asyncio.create_subprocess_shell`.
Blocking calls exhaust the thread pool under concurrent load.

### Rule 4: No Manual Output Truncation

SmartOutputFilter handles all output compression. Do not manually
truncate, regex-strip, or slice command output.

```python
# FORBIDDEN:
output = result.stdout[:1000]
output = re.sub(r'PASSED.*', '', result.stdout)

# REQUIRED:
result = await executor.execute(command)
output = result["output"]  # Already filtered intelligently
```

**Rationale:** Manual truncation can silently discard error messages.
SmartOutputFilter guarantees ERROR > WARNING > SUMMARY > INFO > NOISE
priority ordering.

### Rule 5: Handle Unfiltered Copy for Critical Errors

When critical signals (PANIC, Traceback, FATAL) are detected, the
SmartOutputFilter automatically preserves the full unfiltered output.

```python
result = await executor.execute(command)

if "unfiltered" in result:
    # Critical errors found - full output preserved
    logger.warning(
        "Critical signals detected",
        extra={"unfiltered_length": len(result["unfiltered"])},
    )
```

---

### Safety Guarantees

**Guarantee 1: No Critical Data Loss**
- ERROR, FAILED, PANIC, CRITICAL keywords are NEVER filtered out
- Stack traces and exception messages are ALWAYS preserved
- Test failure details are ALWAYS preserved
- Unfiltered copy automatically preserved if critical signals detected

**Guarantee 2: Sensitive Data Redaction**
- password, secret_key, api_key, auth_token patterns are auto-redacted
- bearer tokens are auto-redacted
- All redaction decisions logged in audit trail

**Guarantee 3: Tenant Isolation**
- Each tenant's output is filtered independently via instance_name
- No cross-tenant data leakage possible
- Audit trails are per-tenant for compliance

**Guarantee 4: Full Auditability**
- Every filtering decision recorded with line_number, signal_type, reason
- Recoverable: check audit_trail in metadata
- Reversible: check unfiltered field if critical

---

### Compression Expectations

| Command Category | Examples | Typical Savings |
|---|---|---|
| File Operations | cat, ls, find, tree | 70-90% |
| Git | git status, diff, log | 80-95% |
| Tests | pytest, cargo test | 85-95% |
| Docker | docker ps, logs | 80-90% |
| Build | cargo build, npm build | 70-85% |
| AWS CLI | aws s3, ec2, lambda | 80-90% |

Unexpected low compression (<30%) should be logged for review.

---

### Monitoring

```bash
# View RTK savings
rtk gain                    # Summary stats
rtk gain --graph            # ASCII graph (last 30 days)
rtk gain --daily            # Daily breakdown
rtk discover                # Find missed opportunities
```

---

### Troubleshooting

| Symptom | Likely Cause | Solution |
|---|---|---|
| Low compression (<30%) | RTK hook not active | Run `rtk init -g` |
| Missing audit trail | Direct subprocess used | Use SystemCommandExecutor |
| Sensitive data exposed | Pattern not covered | Add to `_SENSITIVE_PATTERNS` in output_filter.py |
| Event loop blocked | sync subprocess in async | Use `await executor.execute()` |
| RTK not in container | Missing from Dockerfile | Check RTK layer in Dockerfile |

---

## General Project Rules

### Code Standards
- Python: PEP 8, type hints mandatory, `logging` module only (no `print()`)
- Dart: camelCase, `debugPrint()` only
- Line length: 100 characters maximum
- All functions require docstrings

### Architecture
- Backend logic: `backend/` directory only
- Frontend UI: `frontend_flutter/` directory only
- Database: `database_manager.py` is the single source of truth
- Config: `.env` or `config.yaml` only (no hardcoded values)

### Testing
- All changes require corresponding tests
- Zero-regression: existing tests must continue passing
- Sandbox testing only: never test against production databases
