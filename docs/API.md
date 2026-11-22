# RG AI API Specification

## 1. Overview & Conventions

All endpoints under the RG AI platform adhere to the following principles:
- **Root Health Probe**: `GET /health` is maintained at root for deployment orchestrators and uptime checks.
- **API Versioning**: All domain endpoints are prefixed with `/api/v1/`.
- **Content Type**: `application/json; charset=utf-8`
- **Predictable Envelopes**: Responses follow a structured schema with consistent status indicators.

---

## 2. Global Response Contracts

### 2.1 Success Envelope
```json
{
  "success": true,
  "data": { ... }
}
```

### 2.2 Error Envelope
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested item could not be found.",
    "details": null
  }
}
```

### 2.3 Validation Error Envelope (HTTP 422)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters.",
    "details": [
      {
        "field": "symbol",
        "issue": "Field required"
      }
    ]
  }
}
```

---

## 3. Endpoints

### 3.1 Health Check

```http
GET /health
```

Returns the immediate operational state of the backend service.

#### Response: `200 OK`
```json
{
  "success": true,
  "application": "RG AI",
  "status": "healthy"
}
```

---

### 3.2 System Ping (v1)

```http
GET /api/v1/ping
```

Lightweight connectivity verification within the versioned API router.

#### Response: `200 OK`
```json
{
  "success": true,
  "data": {
    "version": "1.0.0",
    "environment": "development",
    "timestamp": "2026-11-17T05:07:00Z"
  }
}
```

---

### 3.3 Browser Lifecycle & Session Management (v1)

> **Security & Local Access Policy**:
> All `/api/v1/browser/*` lifecycle endpoints enforce strict local access control (`verify_local_access_policy`). Requests from non-loopback addresses (`127.0.0.1`, `::1`, `localhost`, `testclient`) are rejected with `403 Forbidden`.

#### 3.3.1 Get Browser Status
```http
GET /api/v1/browser/status
```
Returns live browser state, login status, profile path, active page details, and last activity timestamp.

**Response: `200 OK`**
```json
{
  "state": "RUNNING",
  "login_state": "AUTHENTICATED",
  "is_running": true,
  "profile_dir": "/abs/path/to/backend/data/chrome-profile",
  "target_url": "https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market",
  "current_url": "https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market",
  "current_title": "Indian Stock Market Intelligence",
  "is_target_open": true,
  "last_activity": "2026-11-17T05:30:00Z",
  "error_message": null
}
```

#### 3.3.2 Start Browser
```http
POST /api/v1/browser/start
```
Launches a persistent Chrome process with POSIX advisory lock protection (`profile.lock`), restoring cookies and session state from `backend/data/chrome-profile/`.

#### 3.3.3 Open Target Custom GPT
```http
POST /api/v1/browser/open-gpt
```
Navigates the persistent context page to the centralized Custom GPT URL (`https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market`), analyzes DOM elements, and updates login state.

#### 3.3.4 Confirm Manual Login
```http
POST /api/v1/browser/confirm-login
```
Triggers a live DOM inspection of ChatGPT's interface (checking for message textarea, user profile avatar, or login/sign-up buttons) to verify user authentication without automated credential submission.

#### 3.3.5 Disconnect / Stop Browser
```http
POST /api/v1/browser/stop
```
Gracefully saves browser state and storage, closes the Playwright persistent context, and releases the process file lock.

#### 3.3.6 Reconnect Browser
```http
POST /api/v1/browser/reconnect
```
Probes browser health and re-establishes a clean persistent context if previous connection dropped or page closed.

---

### 3.4 RG AI Intelligence Request Orchestration (v1)

> **Security & Local Access Policy**:
> All `/api/v1/rg-ai/*` orchestration endpoints enforce strict local access control (`verify_local_access_policy`). Requests from non-loopback addresses (`127.0.0.1`, `::1`, `localhost`, `testclient`) are rejected with `403 Forbidden`.

#### 3.4.1 Submit Chat Prompt
```http
POST /api/v1/rg-ai/chat
```
Accepts user analysis prompt, performs bounds checking and sanitization, and queues the request in the single-concurrency pipeline.

**Request Body:**
```json
{
  "prompt": "Analyze NIFTY 50 technical support and resistance levels.",
  "conversation_id": "optional-thread-id",
  "metadata": {
    "focus": "equities"
  }
}
```

**Response: `202 Accepted`**
```json
{
  "success": true,
  "request_id": "req_8b3f20a91e4b",
  "status": "queued",
  "created_at": "2026-11-17T06:30:00Z",
  "queue_position": 1,
  "message": "Prompt successfully queued for orchestration."
}
```

#### 3.4.2 Get Request Status
```http
GET /api/v1/rg-ai/status/{request_id}
```
Retrieves real-time execution status, timestamp records, queue position, and normalized results or structured error details.

**Response: `200 OK` (Completed Example)**
```json
{
  "success": true,
  "request_id": "req_8b3f20a91e4b",
  "status": "completed",
  "created_at": "2026-11-17T06:30:00Z",
  "updated_at": "2026-11-17T06:30:02Z",
  "started_at": "2026-11-17T06:30:00Z",
  "completed_at": "2026-11-17T06:30:02Z",
  "queue_position": null,
  "result": {
    "content": "Technical analysis of NIFTY 50: Primary support at 24,200.",
    "metadata": {
      "template": "v1_indian_stock_analysis"
    },
    "format_type": "text/plain"
  },
  "error": null
}
```

**Response: `200 OK` (Integration Unavailable Example)**
```json
{
  "success": false,
  "request_id": "req_8b3f20a91e4b",
  "status": "integration_unavailable",
  "created_at": "2026-11-17T06:30:00Z",
  "updated_at": "2026-11-17T06:30:01Z",
  "started_at": "2026-11-17T06:30:00Z",
  "completed_at": "2026-11-17T06:30:01Z",
  "queue_position": null,
  "result": null,
  "error": {
    "code": "UNSUPPORTED_INTEGRATION",
    "message": "The configured browser integration does not support this operation without unsupported scraping."
  }
}
```

#### 3.4.3 Cancel Request
```http
POST /api/v1/rg-ai/cancel/{request_id}
```
Cancels an in-flight or queued request, stops active adapter execution, and frees queue slots.

**Response: `200 OK`**
```json
{
  "success": true,
  "request_id": "req_8b3f20a91e4b",
  "status": "cancelled",
  "message": "Request req_8b3f20a91e4b has been cancelled."
}
```

#### 3.4.4 Engine Health & Telemetry
```http
GET /api/v1/rg-ai/health
```
Reports worker state, queue capacity, concurrency configuration, and lifetime request counters.

**Response: `200 OK`**
```json
{
  "status": "healthy",
  "queue_size": 0,
  "max_queue_size": 50,
  "active_worker": true,
  "concurrency_limit": 1,
  "total_processed": 14,
  "total_failed": 0,
  "total_cancelled": 1
}
```

#### 3.4.5 Check Adapter Availability
```http
POST /api/v1/rg-ai/availability
```
Probes browser process state and authentication status on the centralized Custom GPT URL.

**Response: `200 OK`**
```json
{
  "is_available": true,
  "is_browser_running": true,
  "login_state": "authenticated",
  "target_url": "https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market",
  "adapter_type": "BrowserGPTAdapter",
  "message": "Managed Chrome browser session available"
}
```

---

### 3.5 RG AI Response Validation & Normalization (v1)

> **Security & Local Access Policy**:
> All `/api/v1/rg-ai/*` response validation endpoints enforce strict local access control (`verify_local_access_policy`). Requests from non-loopback addresses are rejected with `403 Forbidden`.

#### 3.5.1 Validate Raw Response
```http
POST /api/v1/rg-ai/validate-response
```
Extracts JSON from raw text or markdown code fences, validates against registered Pydantic models, and runs domain financial consistency checks.

**Request Body:**
```json
{
  "raw_response": "```json\n{\n  \"stock_name\": \"TCS\",\n  \"symbol\": \"TCS\",\n  \"recommendation\": \"BUY\",\n  \"current_price\": 4250.0\n}\n```",
  "request_id": "val_req_1",
  "expected_type": "stock_analysis"
}
```

**Response: `200 OK` (Valid)**
```json
{
  "success": true,
  "type": "stock_analysis",
  "schema_version": "1.0",
  "request_id": "val_req_1",
  "data": {
    "stock_name": "TCS",
    "symbol": "TCS",
    "exchange": "NSE",
    "currency": "INR",
    "current_price": 4250.0,
    "recommendation": "BUY"
  },
  "warnings": [
    "Analysis lacks explicit quote timestamp metadata."
  ],
  "disclaimer": "Informational research only. Not financial advice."
}
```

**Response: `200 OK` (Validation Failure)**
```json
{
  "success": false,
  "type": "validation_error",
  "request_id": "val_req_1",
  "error": {
    "code": "SCHEMA_VALIDATION_FAILED",
    "message": "The response does not match the expected 'stock_analysis' schema.",
    "details": [
      {
        "field": "symbol",
        "issue": "Field required"
      }
    ]
  }
}
```

#### 3.5.2 Normalize Response
```http
POST /api/v1/rg-ai/normalize-response
```
Normalizes a validated payload into canonical ResponseEnvelope format with ISO 8601 timestamps and standard disclaimer.

#### 3.5.3 List Supported Schemas
```http
GET /api/v1/rg-ai/schemas
```
Returns list of all registered response types supported by the validation engine.

**Response: `200 OK`**
```json
{
  "supported_types": [
    "stock_analysis",
    "technical_analysis",
    "fundamental_analysis",
    "portfolio_analysis",
    "stock_comparison",
    "market_overview",
    "educational_content"
  ],
  "count": 7
}
```

#### 3.5.4 Get Schema Specification
```http
GET /api/v1/rg-ai/schemas/{response_type}
```
Returns standard JSON Schema definition for schema introspection and client validation.



