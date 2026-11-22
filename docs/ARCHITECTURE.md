# RG AI System Architecture

## 1. System Overview

**RG AI** is an enterprise-grade Indian Stock Market Intelligence Platform designed to deliver structured market insights, technical analysis, and research intelligence.

The architecture is built on a clean multi-tier decoupling pattern:
1. **Frontend Presentation Tier**: Next.js App Router (React, TypeScript, Tailwind CSS, Motion design).
2. **Backend Application Tier**: FastAPI (Python 3.12+), asynchronous ASGI runtime, Pydantic data validation, structured logging, centralized error interception.
3. **Integration Tier (Phase 3)**: Playwright-based persistent Chrome browser integration service targeted exclusively at the designated Custom GPT (`https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market`), strictly adhering to the constraint of **no OpenAI API keys or OpenAI API SDK integrations**.
4. **Data Persistence Tier**: MongoDB document store (architecturally prepared with repository patterns; fully provisioned in subsequent phases).

```
+-------------------------------------------------------------------------+
|                          Next.js Frontend (App Router)                   |
|  - Layout / App Shell       - Centralized API Service (fetch wrapper)   |
|  - Reusable Motion Design   - BrowserConnectionCard & Status Polling    |
|  - 4 Pages: Overview, Stocks, RG AI Assistant, Learn Trading             |
+-------------------------------------------------------------------------+
                                    |
                               HTTP / JSON
                                    v
+-------------------------------------------------------------------------+
|                          FastAPI Application Tier                       |
|  +--------------------+  +--------------------+  +--------------------+ |
|  | /health Endpoint   |  | API v1 (/browser)  |  | CORS & Security    | |
|  +--------------------+  +--------------------+  +--------------------+ |
|  +--------------------+  +--------------------+  +--------------------+ |
|  | Pydantic Settings  |  | Central Handlers   |  | Structured Logging | |
|  +--------------------+  +--------------------+  +--------------------+ |
+-------------------------------------------------------------------------+
             |                                              |
             v                                              v
+-----------------------------------------+   +---------------------------+
|    Integration Tier (Playwright)        |   |     Data Layer (Async)    |
| - BrowserManager Singleton (Process Lock|   | - Motor MongoDB Driver    |
| - Persistent Profile: data/chrome-profile   | - Document Repositories   |
| - Independent Login Verification        |   | - Schema Validation       |
| - Target: Custom GPT (Strictly No OpenAI|   +---------------------------+
+-----------------------------------------+
```

---

## 2. Browser & Playwright Architecture (Phase 3)

### 2.1 Persistent User-Data Directory
- **Location**: `backend/data/chrome-profile/` (isolated, never committed, restricted `0700` permissions).
- **Session Longevity**: Preserves cookies, localStorage, and authentication state across backend restarts so that manual login is performed only once.
- **Process Protection**: A non-blocking OS-level file lock (`fcntl.flock` on `backend/data/chrome-profile.lock`) ensures multiple worker processes or instances never corrupt the persistent profile.

### 2.2 First-Time Login Workflow
1. User clicks **"Connect Browser"** in the RG AI frontend interface.
2. FastAPI triggers `BrowserManager.start_browser()`, launching Chrome with the dedicated profile.
3. User triggers **"Open Custom GPT"** to navigate to `https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market`.
4. User manually inputs credentials and solves any CAPTCHA/MFA challenges.
5. User clicks **"Confirm Login"** (`POST /api/v1/browser/confirm-login`).
6. The backend independently verifies authentication by checking active DOM elements (verifies absence of unauthenticated login buttons and presence of chat prompt composer).
7. Profile data persists automatically on disk for subsequent restarts.

### 2.3 Strict Constraints
- **Zero OpenAI API Policy**: No OpenAI SDK or secret keys.
- **Zero Automated Bypasses**: No automated CAPTCHA bypassing or credential stuffing.
- **Local Security Boundary**: Browser control endpoints are restricted to localhost clients.

---

## 3. Automation Engine & Request Orchestration (Phase 4)

Phase 4 introduces a resilient, asynchronous orchestration engine that manages user analysis prompts, coordinates execution across replaceable adapters, and honestly enforces compliance boundaries regarding website automation.

```
Frontend (Next.js 16 + React 19)
  │ (Prompt Submission, Real-time Status Polling, Cancellation Trigger)
  ▼
API Tier (/api/v1/rg-ai)
  ├─ POST /chat (Validates prompt bounds & enqueues)
  ├─ GET /status/{request_id} (Real-time state & normalized results)
  ├─ POST /cancel/{request_id} (Cancels in-flight or queued request)
  ├─ GET /health (Reports queue occupancy & worker metrics)
  └─ POST /availability (Checks adapter readiness & browser session)
  ▼
RequestManager & RequestQueue
  ├─ Bounded Async Queue (Default capacity: 50, duplicate prompt SHA-256 rejection)
  ├─ Serialized Worker Loop (Concurrency = 1 to protect single persistent Chrome profile)
  ├─ State Machine (IDLE -> QUEUED -> INITIALIZING -> [WAITING_FOR_LOGIN | SUBMITTING] -> PROCESSING -> VALIDATING -> COMPLETED)
  └─ Terminal Outcomes: COMPLETED, FAILED, CANCELLED, INTEGRATION_UNAVAILABLE
  ▼
AutomationService & BaseGPTAdapter
  ├─ BrowserGPTAdapter (uses Phase 3 BrowserManager, verifies login, raises UnsupportedIntegrationError when scraping is disabled)
  └─ MockGPTAdapter (for automated testing of completions, cancellations, timeouts, and errors)
```

### 3.1 11-State Formal Lifecycle
Requests progress through strict state transitions:
1. `IDLE` -> Initial internal state.
2. `QUEUED` -> Enqueued in FIFO queue with position tracking.
3. `INITIALIZING` -> Picked up by worker; verifying browser session and adapter readiness.
4. `WAITING_FOR_LOGIN` -> Target Custom GPT requires user authentication.
5. `SUBMITTING` -> Prepared prompt dispatched to adapter.
6. `PROCESSING` -> In-flight execution (protected by configurable timeout).
7. `VALIDATING` -> Response content presence and integrity verification.
8. `COMPLETED` -> Terminal state containing verified `NormalizedResult`.
9. `FAILED` -> Terminal failure with structured error code and sanitized message.
10. `CANCELLED` -> Terminal state triggered by user cancellation.
11. `INTEGRATION_UNAVAILABLE` -> Terminal state honestly reported when programmatic extraction on Custom GPT requires unsupported scraping.

### 3.2 Single-Context Profile Protection
Because the underlying persistent Chrome profile (`backend/data/chrome-profile/`) cannot be safely accessed concurrently by multiple sessions, the `RequestManager` serializes all execution (`concurrency = 1`). In-flight prompts are tracked via SHA-256 hashes to prevent duplicate submissions from clogging the pipeline.

### 3.3 Strict Non-Scraping Policy
In adherence to the platform's constraints:
- Unsupported DOM scraping or reverse-engineered private ChatGPT endpoints are strictly forbidden.
- When an operation lacks an officially supported programmatic integration protocol on the ChatGPT Custom GPT, `BrowserGPTAdapter` cleanly returns `INTEGRATION_UNAVAILABLE`.
- Users are prompted to interact directly with the Custom GPT in their connected persistent Chrome session.
- Fabricated or simulated "AI chat" responses are never generated or presented as real integration outputs.

---

## 4. Strict JSON Response Engine (Phase 5)

Phase 5 establishes a robust, deterministic response validation and normalization layer ensuring that all stock market intelligence outputs conform to strict Pydantic schemas before being marked as completed.

```
Raw Response (String or Code Fence)
       │
       ▼
JsonParser (Safe extraction, Markdown fence stripping, depth & payload limits)
       │
       ▼
SchemaRegistry & Type Detection
  ├─ stock_analysis
  ├─ technical_analysis
  ├─ fundamental_analysis
  ├─ portfolio_analysis
  ├─ stock_comparison
  ├─ market_overview
  └─ educational_content
       │
       ▼
JsonValidator & Domain Consistency Checks
  ├─ Pydantic field, type, and enum checks
  ├─ Financial consistency (entry min <= max, positive prices, percentage bounds)
  └─ Warning generation for context-dependent signals
       │
       ▼
ResponseNormalizer
  └─ Canonical ResponseEnvelope (schema_version "1.0", request_id, ISO 8601 timestamps, disclaimer)
```

### 4.1 Authoritative Backend Validation
Because natural language prompts cannot guarantee structured JSON output from language models, the backend validation layer is strictly authoritative:
- Malformed JSON is rejected with code `INVALID_JSON`.
- Schema mismatches are rejected with code `SCHEMA_VALIDATION_FAILED` and field-level details.
- Unsupported formats return `UNSUPPORTED_RESPONSE_TYPE`.
- Missing values remain `null`. The engine never fabricates prices, metrics, or estimates.

### 4.2 Standard Response Envelope
All validated analysis responses are encapsulated within:
```json
{
  "success": true,
  "type": "stock_analysis",
  "schema_version": "1.0",
  "request_id": "req_8b3f20a91e4b",
  "data": { ... },
  "warnings": null,
  "disclaimer": "Informational research only. Not financial advice."
}
```


