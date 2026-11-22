# RG AI — Indian Stock Market Intelligence Platform

**RG AI** is an enterprise-grade Indian Stock Market Intelligence Platform delivering real-time market data, technical insights, and automated research workflows tailored to the Indian financial ecosystem (NSE / BSE).

---

## 1. Technology Stack

| Layer | Technologies & Tools |
| :--- | :--- |
| **Frontend** | Next.js 16 (App Router), React 19, TypeScript (Strict Mode), Tailwind CSS v4, Motion for React, Lucide Icons, ESLint |
| **Backend** | Python 3.12+, FastAPI, Uvicorn (ASGI), Pydantic v2, Pydantic Settings |
| **Integrations** | Strict JSON Response Engine, Financial Validation & Normalizer, Schema Registry, RG AI Request Orchestrator, Playwright Chrome Lifecycle |
| **Data Layer** | MongoDB (architecturally prepared with Motor async driver and generic repositories) |
| **Testing** | Pytest, Pytest-Asyncio, HTTPX, TypeScript (`tsc`), ESLint |

> **AI Policy & Constraints**:
> This platform strictly operates **without OpenAI API keys or OpenAI SDK integrations**. Future intelligence workflows interface with the designated Custom GPT (`https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market`) via browser automation; unsupported web scraping is strictly avoided.

---

## 2. Project Architecture & Structure

```
AI-Stock-Market/
├── frontend/
│   ├── app/                      # Next.js App Router (layout, page, loading, error, not-found)
│   ├── components/               # Modular UI components (Header, Footer, StatusBadge)
│   ├── features/                 # Modular domain features (market, stock-analysis, etc.)
│   ├── hooks/                    # Reusable React hooks (useHealthCheck)
│   ├── services/                 # Centralized API service & HTTP client
│   ├── lib/                      # Utilities & validated environment config
│   ├── types/                    # Strict TypeScript definitions
│   ├── public/                   # Static assets
│   ├── tests/                    # Frontend test suite
│   ├── .env.example              # Sample frontend environment config
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/                  # API routers (root health probe, /api/v1)
│   │   ├── core/                 # Centralized settings, logging, exceptions, handlers, security
│   │   ├── models/               # Domain models & MongoDB document bases
│   │   ├── schemas/              # Pydantic validation & response envelopes
│   │   ├── services/             # Domain business logic (HealthService, etc.)
│   │   ├── integrations/         # Browser automation interface stubs (Custom GPT)
│   │   ├── repositories/         # MongoDB repository abstraction layer
│   │   ├── utils/                # Date and helper utilities
│   │   └── main.py               # Application factory & ASGI entrypoint
│   │
│   ├── tests/                    # Backend test suite (pytest)
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Sample backend environment config
│   └── pytest.ini                # Pytest configuration
│
├── docs/
│   ├── ARCHITECTURE.md           # Multi-tier system architecture specification
│   ├── API.md                    # REST API documentation & envelopes
│   └── DEVELOPMENT.md            # Local developer onboarding guide
│
├── PROGRESS.md                   # Phase-by-phase implementation tracker
├── README.md                     # Platform overview & execution guide
└── .gitignore                    # Comprehensive repository gitignore
```

---

## 3. Prerequisites

- **Node.js**: `v20.x` or higher
- **npm**: `v10.x` or higher
- **Python**: `3.12` or higher (verified on Python 3.14)
- **Virtual Environment Tool**: `python3 -m venv`

---

## 4. Installation & Setup

### 4.1 Backend Installation

```bash
# Navigate to the backend directory
cd backend

# Create isolated Python virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip and install pinned dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file from template
cp .env.example .env
```

### 4.2 Frontend Installation

```bash
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Create frontend environment file
cp .env.example .env.local
```

---

## 5. Environment Configuration

### Frontend (`frontend/.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (`backend/.env`)
```env
APP_NAME=RG AI
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
CORS_ORIGINS=http://localhost:3000
MONGODB_URI=
MONGODB_DATABASE=rg_ai
```

> **Production Safety Validation**:
> If `APP_ENV=production`, the backend strictly validates that wildcard CORS (`*`) is forbidden and `MONGODB_URI` is provided, preventing accidental insecure deployments.

---

## 6. Development Commands

### Run Backend Server
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base: `http://127.0.0.1:8000`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/health`

### Run Frontend Development Server
```bash
cd frontend
npm run dev
```
- Frontend Application: `http://localhost:3000`

---

## 7. Testing & Quality Verification

### Run Backend Automated Tests
```bash
cd backend
source .venv/bin/activate
pytest -v
```
All 136 automated tests cover:
- Root `/health` endpoint response contract (`{"status": "healthy", "app": "RG AI - Indian Stock Market Platform"}`)
- API v1 system ping endpoint and database health probe
- Configuration loading, default parameters, and production invariant enforcement
- CORS origin handling and defensive security headers (CSP, HSTS, X-Frame-Options, etc.)
- Custom exception handling, 404/422 status mapping, and internal stack trace shielding
- **Browser Lifecycle & Process Locking**: File lock acquisition, duplicate lock prevention (`ProfileLockedError`), automatic lock release on stop/cleanup
- **Browser State Machine & Persistence**: Transition through `STOPPED`, `STARTING`, `RUNNING`, `LOGIN_REQUIRED`, `AUTHENTICATED`, `STOPPING`
- **DOM Login Detection**: Independent inspection for prompt textareas vs login/signup buttons
- **Request Queue & Concurrency**: Bounded queue overflow (`QueueFullError`), in-flight duplicate prompt hash protection (`DuplicateRequestError`), FIFO ordering, serialized execution (`concurrency = 1`)
- **State Machine Transitions**: 11-state formal lifecycle enforcement, illegal state jump rejection (`InvalidStateTransitionError`)
- **Cancellation & Timeouts**: In-flight task cancellation, cancellation token propagation, execution timeout handling
- **Honest Integration Handling**: `BrowserGPTAdapter` returning `INTEGRATION_UNAVAILABLE` on unsupported scraping, never fabricating AI text
- **Strict JSON Parsing**: Extraction from markdown code blocks (````json ... ````), conversational text wrappers, payload size bounds (512 KB), depth limits, multiple-object ambiguity rejection
- **Pydantic Domain Schemas**: Strict validation for all 7 analysis types (`stock_analysis`, `technical_analysis`, `fundamental_analysis`, `portfolio_analysis`, `stock_comparison`, `market_overview`, `educational_content`)
- **Financial Consistency Checks**: Positive price validation, entry zone bounds (`min <= max`), percentage boundaries, recommendation context checks, non-negative capital figures, null preservation
- **Canonical Envelope Normalization**: Standard `ResponseEnvelope` generation, ISO 8601 UTC timestamp formatting, disclaimer preservation, and structured error payloads
- **Local Access Security**: Rejection of non-local IP requests to browser and RG AI endpoints with `403 Forbidden`
- **Indian Market Price Tracking**: Quotes, OHLCV normalization, IST hours logic, Yahoo Finance provider, TTL caching
- **Overview Intelligence**: NIFTY 50, SENSEX, BANK NIFTY cards, sentiment scoring formula, news feed integration
- **Learn Trading Platform**: 14 curriculum categories, 13 candlestick patterns, deterministic server quiz grading, bookmarks
- **MongoDB Persistence**: 12 core collections, idempotent indexes, PBKDF2 cryptography, graceful offline degradation
- **Security Audit & Hardening**: Request size limiting (HTTP 413), sliding-window rate limiting (HTTP 429), NoSQL injection sanitization

### Run Frontend Quality Checks
```bash
cd frontend

# 1. Type Check
npx tsc --noEmit

# 2. Lint Check
npm run lint

# 3. Production Build
npm run build
```

---

## 8. Security & Error Handling Baseline

1. **Information Leakage Prevention**: In all production and non-debug responses, unhandled exceptions return a standardized sanitized JSON error payload. Raw Python tracebacks, database URLs, and server paths are never sent to clients.
2. **Credential Scrubbing in Logs**: A custom log formatter automatically scrubs tokens, MongoDB URIs with embedded passwords, and authorization headers before logging.
3. **Defense-in-Depth HTTP Headers**: Full security headers (`CSP`, `HSTS`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy`) are injected across all responses.
4. **Payload Size & Rate Limiting**: Max 2MB request payload size with HTTP 413, and in-memory IP rate limiter returning HTTP 429 with `Retry-After`.
5. **NoSQL Sanitization**: All repository filters stripped of `$where`, `$function`, `$expr`, `$accumulator`, and null bytes.

---

## 9. Troubleshooting

| Issue | Cause | Resolution |
| :--- | :--- | :--- |
| Frontend displays "Backend Offline" | FastAPI is not running on port 8000 | Start backend via `uvicorn app.main:app --port 8000` in `backend/` |
| CORS origin blocked in browser | Request origin not in `CORS_ORIGINS` | Add the frontend URL to `CORS_ORIGINS` in `backend/.env` |
| `ValueError: MONGODB_URI must be configured` | `APP_ENV=production` without URI | In development, set `APP_ENV=development` in `backend/.env` |
| Node build fails on prerendering | Dynamic non-deterministic dates in server components | Use static values or declare `"use client"` where hydration is required |

---

## 10. Documentation Index

- Detailed Architecture: [`docs/ARCHITECTURE.md`](file:///home/ritesh/Desktop/Projects%20Data/AI%20Stock%20Market/docs/ARCHITECTURE.md)
- REST API Reference: [`docs/API.md`](file:///home/ritesh/Desktop/Projects%20Data/AI%20Stock%20Market/docs/API.md)
- Developer Onboarding: [`docs/DEVELOPMENT.md`](file:///home/ritesh/Desktop/Projects%20Data/AI%20Stock%20Market/docs/DEVELOPMENT.md)
- Security Specification: [`SECURITY.md`](file:///home/ritesh/Desktop/Projects%20Data/AI%20Stock%20Market/SECURITY.md)
- Production Deployment Runbook: [`PRODUCTION_DEPLOYMENT.md`](file:///home/ritesh/Desktop/Projects%20Data/AI%20Stock%20Market/PRODUCTION_DEPLOYMENT.md)
- Complete Testing & Verification Report: [`TESTING_REPORT.md`](file:///home/ritesh/Desktop/Projects%20Data/AI%20Stock%20Market/TESTING_REPORT.md)
- Backup & Disaster Recovery Guide: [`BACKUP.md`](file:///home/ritesh/Desktop/Projects%20Data/AI%20Stock%20Market/BACKUP.md)
- Phase Progress Tracker: [`PROGRESS.md`](file:///home/ritesh/Desktop/Projects%20Data/AI%20Stock%20Market/PROGRESS.md)

