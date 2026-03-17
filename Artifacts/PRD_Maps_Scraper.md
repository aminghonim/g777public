# PRD: Maps Scraper Microservice

> **Document Version:** 1.0
> **Author:** CNS Squad (Orchestrator + Researcher)
> **Date:** 2026-03-16
> **Status:** APPROVED
> **Classification:** Internal - CNS Squad

---

## 1. Executive Summary & Objective

### 1.1 Background

Through a deep reverse engineering operation (V2) on the
"Google Maps Extractor" desktop application (v4.219.0, by Omkar Cloud),
we successfully unpacked the Electron ASAR archive and analyzed
the complete source code. The application is built on:

- **Electron** (Node.js + Chromium shell)
- **Playwright** (browser automation engine, 260 references in core)
- **Botasaurus** (proprietary scraping framework by the same developer)

### 1.2 Objective

Transform the resource-heavy desktop scraper (Electron: ~281 MB installed)
into a **lightweight, headless, Docker-ready Python microservice** that
integrates seamlessly into our existing FastAPI backend. The service will:

- Run as a background worker, not a standalone application.
- Expose RESTful API endpoints for task submission and data retrieval.
- Operate fully offline with zero external dependencies or telemetry.
- Be horizontally scalable via Docker containers.

---

## 2. Core Logic & Reverse Engineering Insights

### 2.1 Scraping Engine Architecture

The original application bundles Playwright inside
a Webpack-compiled `main.js`. The scraping logic resides in:
`dist/main/inputs/google_maps_scraper.js`

### 2.2 Extraction Strategies (Zoom Levels)

| Strategy       | Zoom Level |
|----------------|------------|
| `fastest`      | Auto       |
| `fast`         | Auto       |
| `detailed`     | Auto       |
| `zoom_15`      | 15         |
| `zoom_16`      | 16         |
| `zoom_17`      | 17         |
| `zoom_18`      | 18         |

### 2.3 Stealth & Anti-Detection

- **Network Interception:** Blocking images, fonts, and captures API responses directly.
- **User-Agent Rotation:** Using a list of 200+ real fingerprints.
- **Fingerprint Protection:** Proper header ordering and randomization.

---

## 3. Architecture & Tech Stack

### 3.1 Technology Stack

- **Language:** Python 3.12+
- **API Framework:** FastAPI
- **Browser Engine:** Playwright (Python)
- **Configuration:** YAML (Config-First)
- **Retry Logic:** Tenacity
- **Containerization:** Docker

---

## 4. Config-First & Modularity (CNS Rule 6)

Zero hardcoded values. All parameters (UAs, engine selection, timeouts) must be in `config/maps_scraper.yaml`.

---

## 5. The R&D Layer: Browser Engine Abstraction

The system must support a Strategy Pattern in `engine.py` to switch between:
1. **ChromiumEngine** (Stable, Playwright-based)
2. **LightpandaEngine** (R&D, CDP-based, Zig-based engine for lower RAM)

---

## 6. Security & Privacy Mandate

- **NO EXTERNAL TELEMETRY:** Zero connections to `omkar.cloud`.
- **Data Privacy:** All data remains within our controlled environment.
- **Docker Isolation:** Restricted network access.

---

## 7. Implementation Phases

1. **Phase 1:** Core Library (Engine, Stealth, Config).
2. **Phase 2:** Scraper Logic & Parser.
3. **Phase 3:** FastAPI Integration & Docker.

---

_PRD v1.0 - Maps Scraper Microservice. CNS Squad._
