# G777 Antigravity Platform — Architectural Summary

> **Version:** 2.0.0-legacy-restore (Config v2.2.0)
> **Last Updated:** 2026-04-25
> **Status:** Production-Ready (with ongoing hardening)
> **Primary Use Case:** WhatsApp Automation, Lead Generation, Business Intelligence

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Structure & Architecture](#2-project-structure--architecture)
3. [Technology Stack Analysis](#3-technology-stack-analysis)
4. [Database & Storage](#4-database--storage)
5. [Fallbacks & Error Handling](#5-fallbacks--error-handling)
6. [Testing Strategy](#6-testing-strategy)
7. [Frontend State Persistence](#7-frontend-state-persistence)
8. [Security Architecture & Assessment](#8-security-architecture--assessment)
9. [Authentication & Authorization](#9-authentication--authorization)
10. [AI & Agent Systems](#10-ai--agent-systems)
11. [Core Services & Modules](#11-core-services--modules)
12. [API Endpoints & Routers](#12-api-endpoints--routers)
13. [Campaign & Messaging System](#13-campaign--messaging-system)
14. [Monitoring & Analytics](#14-monitoring--analytics)
15. [Deployment & DevOps](#15-deployment--devops)
16. [Performance & Scalability](#16-performance--scalability)
17. [Vulnerabilities & Risks](#17-vulnerabilities--risks)
18. [Recommendations](#18-recommendations)

---

## 1. Executive Summary

G777 Antigravity is an enterprise-grade automation platform combining WhatsApp messaging, AI-powered intelligence, and cross-platform UI into a unified SaaS product.

| Metric | Count |
|---|---|
| Core Python Modules | 40+ |
| API Endpoints | 20+ |
| AI Agents | 4 (Persona, Researcher, Sentinel, Coder) |
| MCP Servers | 6 (Python + Node.js) |
| External Integrations | 15+ |
| Python Dependencies | 35+ packages |
| Security Guards | RTK Enforcement + Middleware |

---

## 2. Project Structure & Architecture

```
g777/
├── main.py                    # FastAPI application entry point
├── backend/
│   ├── database_manager.py    # Central DB access (Raw SQL via psycopg2)
│   ├── db_service.py          # DB context manager (psycopg2)
│   ├── campaign_manager.py    # Campaign orchestration
│   ├── whatsapp_sender.py     # WhatsApp message dispatch
│   ├── wa_gateway.py          # WA/Evolution gateway (local bridge)
│   ├── ai_engine.py           # AI orchestration engine
│   ├── ai_client.py           # Gemini API client
│   ├── scrapling_engine.py    # Stealth web scraping
│   ├── browser_core.py        # Browser automation (undetected-chromedriver)
│   ├── warmer.py              # Account warming simulation
│   ├── webhook_handler.py     # WhatsApp webhook receiver
│   ├── mcp_manager.py         # MCP tool discovery & invocation
│   ├── core/
│   │   ├── config.py          # Configuration loading
│   │   ├── security.py        # JWT, token blocklist (Upstash Redis)
│   │   ├── auth.py            # Clerk authentication
│   │   ├── middleware.py       # Security headers, CORS
│   │   ├── monitoring.py      # Sentry integration
│   │   ├── model_router.py    # Smart Task Router (Gemini model selection)
│   │   ├── quota_guard.py     # SaaS quota enforcement
│   │   ├── safety.py          # Code safety validation
│   │   ├── mcp_auth.py        # MCP authentication (HMAC)
│   │   ├── rtk_enforcement.py # Subprocess guard
│   │   ├── system_commands.py # SystemCommandExecutor
│   │   └── analytics.py       # PostHog event tracking
│   ├── agents/
│   │   ├── orchestrator.py    # Agent orchestration
│   │   ├── researcher.py      # Research agent
│   │   └── coder.py           # Code generation agent
│   ├── evolution/             # Evolution API handlers (connection, messaging)
│   ├── routers/               # FastAPI route modules (10 modules)
│   ├── services/
│   │   ├── pinecone_manager.py # Vector DB (Pinecone Serverless)
│   │   ├── cache_manager.py   # Upstash Redis cache & rate limiting
│   │   └── resend_client.py   # Email (Resend)
│   ├── models/                # Pydantic data models
│   └── mcp_server/
│       └── agent_router.py    # SAAF agent routing
├── frontend_flutter/          # Flutter cross-platform UI
│   └── lib/
│       ├── core/              # Config, networking, theme, security
│       ├── features/          # Feature modules (auth, CRM, analytics, etc.)
│       └── shared/            # Layouts, providers, widgets
├── tests/                     # Root-level test suite (pytest TDD)
│   ├── test_broadcast_logic.py
│   ├── test_group_sender.py
│   └── security/              # Security vulnerability tests
├── config/                    # YAML/JSON configuration files
├── n8n_workflows/             # n8n automation workflows
├── database/                  # DB init scripts
├── docker-compose.yml         # Container orchestration
├── Dockerfile                 # Backend image definition
├── requirements.txt           # Python dependencies
└── GEMINI.md                  # Single source of truth (CNS Squad Constitution)
```

---

## 3. Technology Stack Analysis

### Backend Stack

| Layer | Technology | Purpose |
|---|---|---|
| Web Framework | FastAPI (async) | REST API server |
| ASGI Server | Uvicorn | Production server |
| Database Driver | `psycopg2-binary` | Raw SQL to PostgreSQL (no ORM) |
| AI | Google Genai (Gemini 3.1 Flash/Pro + 2.5) | Dynamic model routing |
| HTTP Clients | httpx, aiohttp, requests | Async/sync HTTP |
| Browser Automation | Selenium + undetected-chromedriver | Stealth scraping |
| Scraping | Scrapling + Playwright | Adaptive web extraction |
| Vector DB | Pinecone (Serverless) | Semantic search |
| Cache & Rate Limit | Upstash Redis | Distributed state |
| Email | Resend | Transactional email |
| Auth | Clerk (custom httpx impl) | JWT verification |
| Observability | Sentry + PostHog | Error tracking + analytics |
| Retry/Resilience | `tenacity` | Smart retry with exponential backoff |
| Security | python-jose, python-magic | JWT crypto, file validation |
| Logging | loguru | Structured logging |

### Frontend Stack (Flutter)

| Layer | Technology | Purpose |
|---|---|---|
| Framework | Flutter (cross-platform) | Desktop, Web, Mobile UI |
| State Management | Riverpod | Live API-driven state |
| Routing | go_router | Declarative navigation |
| Secure Storage | `flutter_secure_storage` | Tokens, session data |
| Preferences | `shared_preferences` | Theme, login state |
| HTTP | Dio | API communication |
| Auth | Clerk (custom service) | License & session management |

---

## 4. Database & Storage

### 4.1 Database Access Pattern — Raw SQL (No ORM)

The backend does **not** use any ORM framework (no SQLAlchemy, no SQLModel). All database operations are performed using **high-performance Raw SQL** via the `psycopg2-binary` library, specifically leveraging:

- **`RealDictCursor`** — Returns query results as dictionaries keyed by column names, providing clean, predictable data access without ORM overhead.
- **`execute_values`** — High-performance batch insert/update operations, significantly faster than individual INSERT statements.
- **Connection Pooling** — `psycopg2.pool` manages a pool of reusable connections to minimize connection overhead.

All database operations are centralized through a single module:

> **[`backend/database_manager.py`](backend/database_manager.py)** — The sole data access layer for the entire platform.

A secondary context manager exists at [`backend/db_service.py`](backend/db_service.py) for scoped DB sessions.

**Rationale:** Raw SQL with `psycopg2-binary` provides maximum query control, predictable performance characteristics, and eliminates the abstraction leak and overhead typical of ORMs — critical for a high-throughput messaging platform.

### 4.2 Database Identity — Cloud-First Architecture

| Environment | Database | Role | Configuration |
|---|---|---|---|
| **Production (Source of Truth)** | **Supabase Cloud PostgreSQL** | Primary, sole source of truth | `DATABASE_URL` in `.env` (Pooler Port 6543) |
| **Local Development** | `postgres` container (Docker) | Dev-only, fallback | `docker-compose.yml` (Port 5432) |

**Key Rules:**
- The **Supabase Cloud** database is the **only** source of truth for production data.
- The `postgres` container defined in `docker-compose.yml` is **strictly** a local development environment and fallback — it is **never** used in production.
- All production connections route through the Supabase Pooler (`aws-1-eu-central-1.pooler.supabase.com:6543`) for connection stability.
- **Neon PostgreSQL is deprecated and removed** — any reference to Neon/Port 5432 should be avoided.

### 4.3 Vector Storage

| Service | Technology | Purpose |
|---|---|---|
| Production | Pinecone (Serverless, `us-east-1`) | Semantic search, RAG |
| Local/Dev | ChromaDB (in-memory) | Development vector search |

### 4.4 Cache & Distributed State

| Service | Technology | Purpose |
|---|---|---|
| Cache & Rate Limiting | Upstash Redis | Session cache, API response cache, rate limits |
| Token Blocklist | Upstash Redis | Distributed JWT revocation (M11 fix) |
| Guest Rate Limiting | Upstash Redis | Distributed guest request tracking (M11 fix) |

---

## 5. Fallbacks & Error Handling

### 5.1 Smart Retry with Exponential Backoff

The platform does **not** use a separate message queue (e.g., RabbitMQ, Celery) for resilience. Instead, it relies on a **Smart Retry with Exponential Backoff** strategy implemented via the `tenacity` library.

**Pattern used across all network-dependent services:**

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    reraise=True,
)
async def call_external_service():
    ...
```

**Services using tenacity retry:**

| Service | File | Retry Config |
|---|---|---|
| Evolution Manager | `backend/core/evolution_manager.py` | 3 attempts, exp backoff (2-10s) |
| Scrapling Engine | `backend/scrapling_engine.py` | 3 attempts, exp backoff (2-10s) |
| MCP Manager | `backend/mcp_manager.py` | 3 attempts, exp backoff |
| Pinecone Manager | `backend/services/pinecone_manager.py` | 3 attempts, exp backoff (1-5s) |
| Cache Manager | `backend/services/cache_manager.py` | 3 attempts, fixed 1s wait |
| Resend Client | `backend/services/resend_client.py` | 3 attempts, exp backoff (2-10s) |
| PostHog Analytics | `backend/core/analytics.py` | 2 attempts, exp backoff |
| Agent Router | `backend/mcp_server/agent_router.py` | 3 attempts, exp backoff |
| Warmer | `backend/routers/warmer.py` | 3 attempts, random wait (1-5s) |

### 5.2 WhatsApp Message Queue — Evolution API Local Buffer

For WhatsApp messaging resilience, the **Evolution API** service acts as a local buffer:

- When the backend is temporarily unreachable, Evolution API **stores and schedules messages locally** as a temporary queue.
- Messages are held until the connection is restored, ensuring no message loss during transient outages.
- This eliminates the need for a separate message broker while providing reliable delivery guarantees.

### 5.3 WhatsApp Sender Hybrid Architecture

| Mode | Service | Role |
|---|---|---|
| Primary | Azure Cloud Service | Reliable, scalable cloud dispatch |
| Fallback | Local Baileys instance (Port 3000) | Backup when cloud is unavailable |

---

## 6. Testing Strategy

### 6.1 TDD with pytest

The project follows a **Test-Driven Development (TDD)** methodology using the `pytest` framework.

**Test directory structure:**

```
tests/                              # Root-level test directory (NOT inside backend/)
├── test_broadcast_logic.py         # Broadcast campaign logic tests
├── test_group_sender.py            # Group sender model tests
└── security/                       # Security vulnerability TDD suite
    ├── __init__.py
    ├── test_critical_vulnerabilities.py  # Critical security regression tests
    ├── test_m5_quotaguard.py            # M5: QuotaGuard guest bypass fix
    ├── test_m10_safety_protocol.py      # M10: SafetyProtocol bypass fix
    ├── test_m11_distributed_state.py    # M11: In-memory state migration fix
    └── test_mcp_auth.py                 # M8: MCP authentication fix
```

**Key conventions:**
- All test files reside in the **`tests/`** directory at the **project root** — not inside `backend/`.
- Security vulnerability fixes are validated with dedicated TDD test suites under `tests/security/`.
- Each vulnerability fix (M5, M7, M8, M10, M11) has corresponding regression tests.
- The pattern is: write failing test first, implement fix, achieve GREEN status.

---

## 7. Frontend State Persistence

### 7.1 No Offline Caching — Live API-Driven Architecture

The Flutter frontend does **not** use any local database or offline caching solution (no Hive, no SQLite, no Isar). State management is entirely **live and API-driven** through Riverpod providers.

**State management flow:**

```
User Action
    |
    v
[Riverpod Provider]  ──HTTP──>  [FastAPI Backend]  ──SQL──>  [Supabase Cloud]
    |
    v
[UI Rebuild]  <──  [API Response]
```

### 7.2 Local Storage — Minimal, Session-Only

The only local persistence mechanisms are for **session-level data only**:

| Package | Purpose | Data Stored |
|---|---|---|
| `shared_preferences` | Key-value preferences | Theme selection, locale, UI preferences |
| `flutter_secure_storage` | Encrypted storage | Auth tokens, session credentials, license keys |

**What is NOT stored locally:**
- CRM contacts
- Campaign data
- Analytics/metrics
- Message history
- Any business data

All business data is fetched live from the API on every interaction, ensuring data consistency and eliminating sync conflicts.

---

## 8. Security Architecture & Assessment

### 8.1 Security Headers (ASVS V16 Compliance)

Middleware: `SecurityHeadersMiddleware`

| Header | Value | Purpose |
|---|---|---|
| Strict-Transport-Security | `max-age=31536000; includeSubDomains; preload` | HSTS enforcement |
| Content-Security-Policy | `default-src 'self'; frame-ancestors 'none'` | Clickjacking protection |
| X-Content-Type-Options | `nosniff` | MIME sniffing prevention |
| X-Frame-Options | `DENY` | Frame embedding prevention |
| X-XSS-Protection | `1; mode=block` | XSS filtering |

### 8.2 RTK Enforcement Guard

**File:** `backend/core/rtk_enforcement.py`

| Category | Modules | Access |
|---|---|---|
| Whitelisted | `backend.browser_core`, `backend.routers.system`, `backend.market_intelligence`, `tests.*` | Allowed subprocess |
| Blocked | `backend.tools.*`, `backend.mcp_server.*`, `backend.executors.sandbox` | RuntimeError on attempt |

Guarded calls: `subprocess.run()`, `subprocess.Popen()`, `subprocess.call()`

### 8.3 Vulnerability Fixes (Completed)

| ID | Vulnerability | Fix | Status |
|---|---|---|---|
| M5 | QuotaGuard Guest Fallback Bypass | Explicit guard replacing silent `or` chain | GREEN (5/5 tests) |
| M7 | Unauthenticated Webhooks | HMAC-SHA256 signature verification | GREEN (5/5 tests) |
| M8 | MCP Auth Missing | `MCPAuthenticator` with `hmac.compare_digest` | GREEN (5/5 tests) |
| M10 | SafetyProtocol Bypass | Fail-closed for unsupported languages | GREEN (5/5 tests) |
| M11 | In-Memory State | Migrated to Upstash Redis (distributed) | GREEN (2/2 tests) |

---

## 9. Authentication & Authorization

### 9.1 Clerk Integration

**File:** `backend/core/auth.py`

- JWT verification via custom `httpx` implementation (not `clerk-sdk-python` due to Pydantic version conflict)
- User context injection via `get_current_user` dependency
- Guest access mode with limited quota

### 9.2 Guest Access

| Setting | Value |
|---|---|
| Guest Access | Enabled |
| Guest Username | `guest_admin` |
| Guest Instance | `G777_Guest` |
| Guest Email | `guest@localhost` |

**Recommended restrictions:** Limited quota (10 msgs/day), read-only data access, no export, 30-min session timeout.

### 9.3 SaaS Quota Management (SaaS-013)

**Database method:** `db_manager.get_user_quota_info(user_id)`

| Tier | Daily Limit | Monthly Cost | Features |
|---|---|---|---|
| Free | 50 | $0 | Basic, ads |
| Pro | 1,000 | $29 | API, analytics |
| Enterprise | Unlimited | Custom | Dedicated support |

**Enforcement points:** Campaign initialization, per-message loop, fallback (429 Too Many Requests).

---

## 10. AI & Agent Systems

### 10.1 Smart Task Router

**File:** `backend/core/model_router.py`

Dynamic model selection configured in `config.yaml`:

| Task | Model | Purpose |
|---|---|---|
| `intent_analysis` | Gemini 3.1 Flash | Fast intent classification |
| `customer_chat` | Gemini 3.1 Pro | High-quality conversation |
| `extraction` | Gemini 3.1 Flash | Data extraction |
| `computer_use` | Gemini 2.5 Computer Use | Visual RPA |
| `content_generation` | Gemini 3.1 Pro | Content creation |

### 10.2 Agent Roster

| Agent | Role |
|---|---|
| Persona | Customer interaction |
| Researcher | Market research & data gathering |
| Sentinel | Security monitoring |
| Coder | Code generation & modification |

### 10.3 SAAF Governance

- All AI interventions MUST use `agent-router` (Backend) or `impeccable-protocol` (Frontend)
- Emergency reset: `[SAAF ENFORCEMENT - HALT]`
- `GEMINI.md` is the single source of truth for SAAF Governance

---

## 11. Core Services & Modules

### 11.1 Modern Free Stack

| Service | Technology | File | Purpose |
|---|---|---|---|
| Email | Resend | `backend/services/resend_client.py` | Transactional email (3k/mo free) |
| Vector DB | Pinecone | `backend/services/pinecone_manager.py` | Semantic search (tenant-isolated) |
| Cache | Upstash Redis | `backend/services/cache_manager.py` | Cache & AI budget protection |
| Auth | Clerk | `backend/core/auth.py` | JWT + middleware |
| Observability | Sentry | `backend/core/monitoring.py` | Error & performance tracking |

### 11.2 Communication Engine

| Component | File | Role |
|---|---|---|
| WA Gateway | `backend/wa_gateway.py` | Local gateway (WAGateway class) |
| Evolution Handlers | `backend/evolution/` | Connection, messaging mixins |
| Evolution API | Docker container (Port 3000) | Baileys WhatsApp bridge |

### 11.3 Automation

| Component | Endpoint | Purpose |
|---|---|---|
| n8n | `http://127.0.0.1:5678` | Workflow automation |
| Webhook Gateway | `http://172.17.0.1:5678/webhook/whatsapp` | Internal webhook relay |

---

## 12. API Endpoints & Routers

**10 Registered API Modules:**

| Router | Prefix | Function |
|---|---|---|
| System | `/` | Health, version, bootstrap |
| Users | `/users` | Auth, profile, quota management |
| License | `/license` | License validation, upgrades |
| CRM | `/api/crm` | Contact management, database |
| Campaigns | `/api/campaigns` | Pause/resume, status, scheduling |
| Connector | `/api/connector` | External service integration |
| Intelligence | `/api/intelligence` | Market research, data extraction |
| Evolution | `/api/evolution` | Baileys WhatsApp gateway |
| Analytics | `/api/analytics` | Campaign metrics, reports |
| Warmer | `/api/warmer` | Account warming, activity simulation |

**Campaign Management Endpoints:**

- `POST /campaigns/pause/{campaign_id}` — Pause active campaign
- `POST /campaigns/resume/{campaign_id}` — Resume from pause point
- `GET /campaigns/status/{campaign_id}` — Get real-time status

---

## 13. Campaign & Messaging System

### WhatsApp Sender Architecture

**File:** `backend/whatsapp_sender.py` (WhatsAppSender class)

```
WhatsAppSender
  +-- Cloud integration (AzureCloudService)
  +-- Contact management (Excel -> DB)
  +-- Message templating & variables ({name}, {phone})
  +-- Rate limiting & delays
  +-- Quota enforcement (daily limits)
  +-- Progress callbacks & logging
```

### Campaign Manager Features

**File:** `backend/campaign_manager.py` (CampaignManager class)

- Multi-message rotation
- SaaS identity management (user_id isolation)
- Working hours enforcement (9 AM - 10 PM)
- Smart random delays (5-15 sec default)
- Quota tracking & enforcement (SaaS-013)
- Media support (images, documents)
- Group link attachment
- Async processing with callbacks
- Error handling & retry logic

---

## 14. Monitoring & Analytics

### Sentry Integration

**File:** `backend/core/monitoring.py`

| Setting | Value |
|---|---|
| FastAPI Integration | Enabled |
| Logging Breadcrumbs | INFO level |
| Error Events | ERROR+ level |
| Transaction Tracking | 20% sample |
| Profile Capture | 20% sample |
| PII Capture | Enabled (GDPR review needed) |

### PostHog Analytics

| Setting | Value |
|---|---|
| Free Tier | 1M events/month |
| Features | Campaign tracking, user behavior, feature usage, funnel analysis |

### Security Logging

- Structured JSON logs (UTC ISO timestamps)
- Event types: request, auth, error
- Client IP tracking
- PII protection (no payloads logged)

---

## 15. Deployment & DevOps

### Docker Compose Services

| Service | Image | Port | Purpose |
|---|---|---|---|
| `postgres` | `postgres:15-alpine` | 5432 | **Local dev DB only** (NOT production) |
| `backend` | Custom Dockerfile | 8081:8000 | FastAPI + Chrome |
| `evolution` | `evoapicloud/evolution-api:v1.8.2` | 3000 | WhatsApp bridge |
| `n8n` | `n8nio/n8n` | 5678 | Workflow automation |

**Key deployment notes:**
- Backend `.env.docker.local` contains production secrets (gitignored)
- `.env.docker` is the committed template with `CHANGE_ME` placeholders
- Chrome flags: `--no-sandbox --disable-dev-shm-usage --disable-gpu`
- Persistent volumes: `chrome_profile`, `auth_info`, `app_data`, `postgres_data`

---

## 16. Performance & Scalability

### Identified Bottlenecks

| Bottleneck | Impact | Solution |
|---|---|---|
| Selenium Browser Automation | 5-15 sec/action, 100-200MB/instance | Headless + pool management |
| API Rate Limits | Gemini: quota-dependent; WhatsApp: 60 msgs/min | Request queuing |
| Vector Search (ChromaDB local) | In-memory, single-machine | Pinecone for production |
| Database Connections | Need pooling at scale | PgBouncer for connection pooling |

### Optimization Recommendations

1. **Async I/O** — Already implemented (FastAPI async routes, `asyncio.to_thread()`)
2. **Caching** — Upstash Redis for session/API response cache (1h TTL)
3. **Database Optimization** — Connection pooling, query indexing on `user_id`/`campaign_id`, materialized views
4. **Horizontal Scaling** — Multiple FastAPI instances behind nginx/HAProxy, shared Redis for session state

---

## 17. Vulnerabilities & Risks

### Active Issues

| Severity | Issue | Status |
|---|---|---|
| CRITICAL | Production credentials in `.env` files | Needs secrets manager (AWS/Azure) |
| HIGH | undetected-chromedriver anti-detection | Legal/TOS review needed |
| MEDIUM | PII captured in Sentry (`send_default_pii=true`) | Set to `false`, filter explicitly |
| MEDIUM | Mock API keys in config | Inject real keys via env vars |

### Resolved Vulnerabilities

| ID | Vulnerability | Resolution |
|---|---|---|
| M5 | QuotaGuard Guest Bypass | Explicit guard, no silent fallback |
| M7 | Unauthenticated Webhooks | HMAC-SHA256 verification |
| M8 | MCP Auth Missing | Token-based HMAC authentication |
| M10 | SafetyProtocol Bypass | Fail-closed for unknown languages |
| M11 | In-Memory State | Migrated to Upstash Redis |

### Positive Security Measures

- RTK Enforcement Guard (subprocess protection)
- ASVS V16 Security Headers
- CORS middleware configured
- Rate limiting (200 msgs/hour)
- JWT authentication with Clerk
- SaaS multi-tenant isolation (user_id checks)
- Sentry error tracking
- Structured security logging
- Session vault (local, configurable)
- PII encryption option
- HMAC webhook verification
- MCP token authentication
- Distributed state (Redis)

---

## 18. Recommendations

### Production Readiness Checklist

| Priority | Action | Status |
|---|---|---|
| P0 | Regenerate `G777_HANDSHAKE_TOKEN` (use secrets manager) | TODO |
| P0 | Inject real `GEMINI_API_KEY` from Google Cloud | TODO |
| P0 | Enable real Clerk authentication (configure backend key) | TODO |
| P0 | Configure HTTPS/TLS certificates (Let's Encrypt) | TODO |
| P1 | Set up Pinecone for vector search (replaces ChromaDB in prod) | TODO |
| P1 | Configure Upstash Redis for caching & rate limiting | Active |
| P1 | Enable Sentry error tracking with production DSN | TODO |
| P1 | Update CORS origins for production domain | TODO |
| P1 | Set up database backups (daily automated) | TODO |
| P2 | Configure PostHog analytics | TODO |
| P2 | Set up CI/CD pipeline (GitHub Actions) | TODO |
| P2 | Load testing with k6 (1000+ concurrent users) | TODO |
| P2 | Document deployment procedure | TODO |
| P3 | Security audit by third-party firm | TODO |
| P3 | GDPR/CCPA compliance audit | TODO |

---

## Known Technical Pitfalls

| Pitfall | Cause | Prevention |
|---|---|---|
| Pydantic Version Hell | `clerk-sdk-python` requires `pydantic<2.0.0` | Use direct `httpx` calls to `api.clerk.com` |
| CodeRabbit YAML Schema | Tools must be objects, not booleans | Use `{enabled: false}`, not `false` |
| Evolution API Webhooks | May stop after container restart | `sudo docker restart evolution-api` |
| Rule Consolidation | Scattered `.mdc`/`.md` files | `GEMINI.md` is the single source of truth |

---

## Known Secrets & Required Environment Variables

| Variable | Purpose | File |
|---|---|---|
| `EVOLUTION_WEBHOOK_SECRET` | HMAC-SHA256 webhook signature (M7) | `backend/webhook_handler.py` |
| `MCP_API_KEY` | MCP tool invocation auth (M8) | `backend/core/mcp_auth.py` |
| `EVOLUTION_API_KEY` | Evolution API bridge auth | `backend/evolution/` |
| `G777_HANDSHAKE_TOKEN` | Internal service handshake | `backend/routers/` |
| `BRIDGE_API_KEY` | Internal bridge authentication | `backend/` |
| `DATABASE_URL` | Supabase Cloud connection string | `.env` |

---

*End of Architectural Summary — G777 Antigravity Platform*
