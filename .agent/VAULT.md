# 🔐 G777 PROJECT VAULT

> [!CAUTION]
> **CLASSIFIED INFORMATION**: This file contains sensitive API keys and credentials.
> NEVER commit this file to public version control. Ensure it is listed in `.gitignore`.

---

## 🚀 Infrastructure & Cloud Services

### ☁️ Upstash (Redis & Management)

_Used for caching, rate limiting, and distributed state._

| Key                      | Value                                                            | Purpose                |
| :----------------------- | :--------------------------------------------------------------- | :--------------------- |
| **Management API Token** | `6867da3e-019b-41ab-a83b-a27ae87bd4b3`                           | Upstash API Automation |
| **Redis DB Name**        | `g777-cache`                                                     | Production Cache       |
| **REST URL**             | `https://patient-polliwog-95331.upstash.io`                      | Backend Connection     |
| **REST Token**           | `gQAAAAAAAXRjAAIgcDJiZjBmZDI3YjA1NWE0YWYwODFhMjQ3MDU5MGU5NDFkYw` | Redis Authentication   |

---

### 🗄️ Supabase (Production Instance)

_Primary Database & Backend._

| Key              | Value                                                                                                               | Purpose                 |
| :--------------- | :------------------------------------------------------------------------------------------------------------------ | :---------------------- |
| **Project ID**   | `zbrpwteyldwpqlcxdpmf`                                                                                              | Production Dashboard    |
| **Postgres URL** | `postgresql://postgres.zbrpwteyldwpqlcxdpmf:G777SecureCRM2026@aws-1-eu-central-1.pooler.supabase.com:6543/postgres` | Primary DB Connection   |
| **DB Password**  | `G777SecureCRM2026`                                                                                                 | Database Superuser      |
| **Access Token** | `sbp_f47240d30afa2ce82534f19a809ba64e0cb628d4`                                                                      | Supabase CLI/Management |

---

### 🤖 AI & Search (Pinecone & Gemini)

_Vector Database and Large Language Models._

| Key                  | Value                                                                         | Purpose                       |
| :------------------- | :---------------------------------------------------------------------------- | :---------------------------- |
| **Gemini API Key**   | `AIzaSyDcCH4S7TkUXAWnM-NZ8Me6CWvbdIsUjx4`                                     | Primary AI Engine (Flash 2.0) |
| **Pinecone API Key** | `pcsk_2eeGaM_US8JVNb4XKVKP7j7PNX3CY9nztih9RBrj13phJSFtHuYgi3eg5rbVHupBDBQLLQ` | Vector Store Auth             |
| **Pinecone Host**    | `https://agent-router-e43ognf.svc.aped-4627-b74a.pinecone.io`                 | Agent Router Index            |

---

### 📧 Communication & Webhooks

_WhatsApp Bridge & Email Delivery._

| Key                   | Value                                                              | Purpose                |
| :-------------------- | :----------------------------------------------------------------- | :--------------------- |
| **Evolution API Key** | `c8d7ef9ccefc092f9bf05495eca59c1610f2a45ff0eec946196e78c0b7af426c` | WhatsApp Gateway Auth  |
| **Webhook Secret**    | `c4b471f19a730998e825dcfc399883dfdd98ff5f2a7a25ba69cbe8007af17679` | Signature Verification |
| **Resend API Key**    | `re_YULgiHLD_AYW9FN5UEpe6r9FGnNn5R3Ej`                             | Email delivery Service |

---

### 🔐 Auth & Identity (Clerk)

_User authentication, session management, JWT verification._

| Key                       | Value                                                                   | Purpose                     |
| :------------------------ | :---------------------------------------------------------------------- | :-------------------------- |
| **Publishable Key**       | `pk_test_Y3JlZGlibGUta2luZ2Zpc2gtODYuY2xlcmsuYWNjb3VudHMuZGV2JA`        | Frontend (public)           |
| **Secret Key (g777-app)** | `sk_test_rg41IfQRt3IeRtZ2zc1TCqFf71NSrdU0KLX4OPFu8i`                    | Backend Admin Auth (ACTIVE) |
| **Secret Key (default)**  | `sk_test_jEGMb6KDaxhfJcbg7Xb0v6nhdkWJXCKaha72VnVCEK`                    | Legacy/Backup Key           |
| **JWKS URL**              | `https://credible-kingfish-86.clerk.accounts.dev/.well-known/jwks.json` | JWT Verification            |
| **Clerk Domain**          | `credible-kingfish-86.clerk.accounts.dev`                               | OAuth Redirects             |

---

### 🚨 Observability & Error Tracking (Sentry)

_Used for monitoring errors and performance._

| Key            | Value                                                                                             | Purpose                 |
| :------------- | :------------------------------------------------------------------------------------------------ | :---------------------- |
| **Sentry DSN** | `https://785985a45615133b8c3edbcbcc488f1c@o4510877886119936.ingest.de.sentry.io/4511006675632208` | Error tracking endpoint |

---

### 🛠️ Internal Security & Handshakes

| Token Name               | Value                              | Purpose                        |
| :----------------------- | :--------------------------------- | :----------------------------- |
| **G777_HANDSHAKE_TOKEN** | `ed6e0e8d3205358da9a4fff1a0bc255b` | Backend <-> Service Auth       |
| **N8N_ENCRYPTION_KEY**   | `7fc13a9656e428c47efe4b29e11219a0` | Workflow Credential Encryption |
| **SECRET_KEY**           | `<REDACTED — use env variable>`    | JWT / Session Signing          |
| **MCP_API_KEYS**         | `<REDACTED — use env variable>`    | Tool Execution Security        |
| **GitHub PAT**           | `<REDACTED — use env variable>`    | Source Control Automation      |

---

## ❓ Missing / Pending Secrets

_These keys are not yet provided or are placeholders._

1. **Deepseek API Key**: `CHANGE_ME` (Optional AI Engine).

---

**Last Updated:** 2026-04-27
**Authorized Personnel:** CNS Squad Agentic AI
