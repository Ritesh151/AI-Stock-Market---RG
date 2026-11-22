# RG AI — Security Architecture & Policy Specification

## 1. Executive Summary

RG AI is an enterprise-grade Indian Stock Market Intelligence Platform built with Next.js (App Router), Python FastAPI, Playwright browser lifecycle automation, and MongoDB persistence. Security is enforced defense-in-depth across the transport, network, application, database, and browser orchestration layers.

This document outlines the security posture, defensive configurations, threat models, and vulnerability disclosure protocol for RG AI.

---

## 2. Threat Modeling & Security Principles

| Threat Vector | Defense Mechanism | Layer |
| :--- | :--- | :--- |
| **DDoS / Request Floods** | Sliding-window IP rate limiter (`InMemoryRateLimiter`, HTTP 429), Nginx burst rate limiting | Gateway / Application |
| **Payload Bombs (OOM)** | Request size limiter middleware (`RequestSizeLimitMiddleware`, max 2MB, HTTP 413) | Application Middleware |
| **NoSQL Operator Injection** | Recursive query filter sanitization (`sanitize_filter`) stripping dangerous `$where`, `$function`, `$expr`, null bytes | Database Repository |
| **Unauthorized Remote Automation** | Local-only network boundary enforcement (HTTP 403 Forbidden on non-loopback requests) | Route Layer |
| **Credential & Key Leaks** | Strict exclusion of external OpenAI keys/SDKs, `.gitignore` on profiles, PBKDF2 password hashing | Auth / Integration |
| **XSS / Clickjacking / MIME-sniffing** | Defensive HTTP security headers (`CSP`, `X-Frame-Options: DENY`, `HSTS`, `X-Content-Type-Options: nosniff`) | Transport / Gateway |
| **Information Leakage** | Centralized exception handling concealing internal Python/MongoDB stack traces from clients | Application Handlers |
| **Cross-Origin Abuse** | Strict CORS policy rejecting wildcards (`*`) and non-HTTPS origins in production | Network / Middleware |

---

## 3. Defense-in-Depth Security Controls

### 3.1 Defensive HTTP Security Headers
Every HTTP response emitted by the FastAPI backend includes mandatory security headers via `SecurityHeadersMiddleware`:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' http://localhost:* http://127.0.0.1:* ws://localhost:* ws://127.0.0.1:*; frame-ancestors 'none';
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
```

### 3.2 Request Size Limiting (HTTP 413)
To protect memory against payload exhaustion attacks:
- `RequestSizeLimitMiddleware` inspects both the `Content-Length` header and incoming streaming bytes.
- Requests exceeding **2,097,152 bytes (2 MB)** are immediately terminated with HTTP `413 Payload Too Large` and standard error envelope:
```json
{
  "success": false,
  "error": {
    "code": "PAYLOAD_TOO_LARGE",
    "message": "Request payload exceeds maximum allowed size of 2097152 bytes",
    "details": null
  }
}
```

### 3.3 Application-Level Rate Limiting (HTTP 429)
- Managed via `InMemoryRateLimiter` and `RateLimitMiddleware`.
- Implements a thread-safe sliding window rate limiting algorithm tracking client IPs.
- Default threshold: **120 requests per 60-second window** per client IP.
- Rate-limited responses return HTTP `429 Too Many Requests` along with a `Retry-After: <seconds>` header.
- Automatically bypassed in `APP_ENV=test` to ensure non-blocking test suite execution.

### 3.4 NoSQL Injection Sanitization
All database lookups pass through `BaseRepository.sanitize_filter(raw_filter)`:
- Recursively strips MongoDB query expression operators (`$where`, `$function`, `$expr`, `$accumulator`, `$regex` if unbounded).
- Sanitizes keys containing null bytes (`\x00`) or suspicious prototype/BSON traversal strings.
- Strips leading dollar signs (`$`) from user-controllable filter keys while allowing safe whitelist evaluation.

### 3.5 Local-Only Network Boundary Policy
Browser lifecycle control and GPT execution endpoints are strictly locked to the local host:
- Targeted routes: `/api/v1/browser/*`, `/api/v1/rg-ai/chat`, `/api/v1/rg-ai/cancel/*`.
- Handled by `verify_local_access`:
  - Validates `request.client.host` against `127.0.0.1`, `::1`, `localhost`, and `testclient`.
  - Blocks remote access with HTTP `403 Forbidden` (`FORBIDDEN: Browser management endpoints are restricted to local host access.`).
  - Ensures the user-in-the-loop browser automation environment cannot be triggered or controlled over public network interfaces.

### 3.6 Production CORS & MongoDB URI Invariants
Enforced dynamically in `backend/app/core/config.py`:
- **CORS Invariant**: When `APP_ENV=production`, `CORS_ORIGINS` cannot contain wildcards (`*`) or unencrypted `http://` URLs (except `localhost` for local testing).
- **MongoDB URI Invariant**: In production environments, `MONGODB_URI` must enforce authentication credentials and TLS encryption (`tls=true` or `ssl=true`), rejecting bare unsecured `mongodb://localhost:27017` connections.

### 3.7 Centralized Exception Concealment
Internal tracebacks and runtime exceptions are trapped by `unhandled_exception_handler`:
- Emits a sanitized error envelope:
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected internal server error occurred.",
    "details": null
  }
}
```
- Full tracebacks and diagnostic dumps are written strictly to internal structured server logs (`app.core.logging`) and are never leaked to external clients.

### 3.8 Cryptographic Password Security
User authentication credentials use standard-library cryptography:
- Algorithm: **PBKDF2-HMAC-SHA256**.
- Iterations: **600,000**.
- Salt: **16 cryptographically secure random bytes** (`os.urandom(16)`).
- Comparison: Constant-time comparison (`secrets.compare_digest`) preventing timing attacks.
- Sensitive credential fields (`password_hash`, `salt`) are excluded from all API output models and JSON serializers.

---

## 4. Playwright Browser Security & Profile Isolation

The Playwright browser automation module operates under strict security constraints:
1. **Isolated Profile**: Stored at `backend/data/chrome-profile/` with restrictive `0700` POSIX directory permissions.
2. **Exclusion from VCS**: Explicitly gitignored to prevent accidental commits of cookies, session tokens, or browser caches.
3. **Process Lock**: Uses POSIX advisory locking (`fcntl.flock(LOCK_EX | LOCK_NB)`) in `profile.lock` to prevent multi-worker concurrency corruption.
4. **No Scraping or Bypass**: Zero reverse-engineered private APIs, zero automated captcha solving, zero credential scraping. When user intervention is required, the system halts and notifies the user transparently.

---

## 5. Security Checklist for Production

Before launching into production, verify:
- [ ] `APP_ENV=production` is set in backend environment.
- [ ] `SECRET_KEY` is replaced with a 256-bit high-entropy secret (`openssl rand -hex 32`).
- [ ] `CORS_ORIGINS` lists only the verified production frontend domain(s).
- [ ] `MONGODB_URI` points to a TLS-secured cluster with authenticated read/write user.
- [ ] Nginx or reverse proxy is configured with TLS 1.3, SSL certificates, and HSTS.
- [ ] Loopback ports (`8000`, `27017`) are blocked by firewall (`ufw` or cloud security groups) from external interfaces.
- [ ] Automated security tests pass (`pytest backend/tests/test_security_audit.py`).

---

## 6. Vulnerability Disclosure & Incident Response

If you discover a security vulnerability within RG AI:
1. **Do NOT open a public GitHub issue.**
2. Email the maintainers directly at `security@rg-ai.internal` (or designated project security contact).
3. Include:
   - Vulnerability description and impact assessment
   - Step-by-step reproduction instructions or proof of concept
   - Proposed remediation if available
4. The RG AI engineering team will acknowledge receipt within 48 hours and coordinate a secure patch release.
