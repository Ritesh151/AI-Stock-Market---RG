# RG AI Developer Guide

## Prerequisites

- **Node.js**: `v20.x` or higher
- **npm**: `v10.x` or higher
- **Python**: `3.12` or higher (tested on Python 3.14)
- **Virtual Environment Tool**: `venv`

---

## 1. Quickstart

### 1.1 Backend Setup

```bash
cd backend

# 1. Create Python virtual environment
python3 -m venv .venv

# 2. Activate environment
source .venv/bin/activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Copy environment configuration
cp .env.example .env

# 5. Run local development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend will be available at: `http://127.0.0.1:8000`
Interactive Swagger Docs: `http://127.0.0.1:8000/docs`
Health Check: `http://127.0.0.1:8000/health`

### 1.2 Frontend Setup

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Copy environment configuration
cp .env.example .env.local

# 3. Run development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## 2. Quality & Testing Commands

### Backend Tests
```bash
cd backend
source .venv/bin/activate
pytest -v
```

### Frontend Build & Lint Checks
```bash
cd frontend
# Check TypeScript types
npx tsc --noEmit

# Run ESLint
npm run lint

# Run Production Build
npm run build
```

---

## 3. Coding Guidelines

1. **No Direct OpenAI SDK Usage**: Do not import `openai` or install OpenAI client packages. Browser automation integration targets the custom GPT.
2. **Strict Typing**: All TypeScript code must comply with `strict: true`. Avoid `any`.
3. **Pydantic Validation**: All FastAPI inputs and outputs must define explicit Pydantic schemas.
4. **Secrets Discipline**: Never commit `.env` or real connection strings to version control.

---

## 4. Browser Session Management & Playwright (Phase 3)

RG AI connects to the target Custom GPT (`https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market`) using a persistent Chromium/Chrome profile managed via Playwright Python.

### 4.1 Prerequisites
- **Google Chrome** or **Chromium** installed locally (e.g. `/usr/bin/google-chrome`, `/usr/bin/chromium`, or Playwright default).
- Playwright Python (`playwright>=1.49.0` included in `requirements.txt`).
- If you do not have system Chromium installed:
  ```bash
  cd backend
  source .venv/bin/activate
  playwright install chromium
  ```

### 4.2 Persistent Profile Directory
The session profile is stored at:
```
backend/data/chrome-profile/
```
- **Permission Hardening**: Directory is automatically created with restricted POSIX mode `0700` (`rwx------`).
- **Process Lock**: A `profile.lock` file is acquired via `fcntl.flock` before launching to prevent multi-process data corruption.
- **Git Ignored**: `.gitignore` ensures credentials, cookies, and local session caches are never committed.
- **No Direct Profile Copying**: RG AI does **not** copy your personal default browser profile.

### 4.3 First-Time Manual Login Flow
1. Start the backend (`uvicorn app.main:app --port 8000 --reload`) and frontend (`npm run dev`).
2. Navigate to **RG AI** in your browser (`http://localhost:3000/rg-ai`).
3. Click the **Chrome Session** button in the top right to open the drawer.
4. Click **Connect Chrome**. This will launch the persistent Chrome instance.
5. Click **Open Custom GPT**. The browser will navigate to `https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market`.
6. Complete manual authentication directly in the launched Chrome window (log in with your ChatGPT account, complete any 2FA/CAPTCHA).
7. Once logged in, click **Confirm Login** in the RG AI drawer. The status will transition to `AUTHENTICATED`.

### 4.4 Subsequent Session Reuse
Because cookies and local storage are saved in `backend/data/chrome-profile/`, restarting the backend or relaunching the browser will automatically restore your authenticated session without requiring you to re-enter your credentials.

### 4.5 Troubleshooting & Common Issues
- **`ProfileLockedError`**: Another backend worker or browser process is already holding `backend/data/chrome-profile/profile.lock`. Stop any dangling instances or call `POST /api/v1/browser/stop`.
- **`BrowserLaunchError: Chrome executable not found`**: Ensure Chrome or Chromium is installed or set `CHROME_EXECUTABLE_PATH=/path/to/chrome` in `backend/.env`.
- **`403 Forbidden` on Browser API**: Browser lifecycle endpoints reject non-local requests. Ensure requests come from `localhost` or `127.0.0.1`.

---

## 5. Request Orchestration & Automation Engine (Phase 4)

### 5.1 Architecture & Single-Context Concurrency
The RG AI backend orchestrates prompts via a centralized `RequestManager` backed by an async FIFO `RequestQueue`:
- **Serialized Concurrency (`concurrency = 1`)**: Ensures prompt execution operations never collide on the single persistent Chrome profile.
- **Duplicate Prevention**: Normalized prompts are hashed (SHA-256) while in-flight to prevent duplicate submissions from congesting the queue.
- **Configurable Limits**: Default queue capacity is 50 requests; execution timeout is 60 seconds.

### 5.2 Adapter Switching & Testing Without Live Accounts
In accordance with platform rules, RG AI never uses scraping or undocumented ChatGPT APIs. For testing purposes, the adapter layer is modular:
```python
from app.integrations.rg_ai.automation_service import get_automation_service
from app.integrations.rg_ai.gpt_adapter import MockGPTAdapter

# Inject mock adapter for test harnesses
mock_adapter = MockGPTAdapter(simulated_delay=0.05, default_response="Sample technical analysis")
get_automation_service().set_adapter(mock_adapter)
```

### 5.3 Automated Testing
Run the complete backend test suite (78 automated tests):
```bash
cd backend
source .venv/bin/activate
pytest -v
```

---

## 6. Strict JSON Response Engine (Phase 5)

### 6.1 Using the Response Processor
The `ResponseProcessor` handles JSON extraction, schema detection, type checking, financial sanity rules, and normalization into standard `ResponseEnvelope`:
```python
from app.services.response_processor import get_response_processor

processor = get_response_processor()
envelope = processor.process(
    raw_content='```json\n{"stock_name": "TCS", "symbol": "TCS", "current_price": 4250.0}\n```',
    request_id="req_123",
    expected_type="stock_analysis",
)
```

### 6.2 Prompt Templates
RG AI provides 10 versioned prompt templates configured in `backend/app/integrations/rg_ai/prompt_templates.py`:
- `complete_stock_analysis`
- `buy_sell_research`
- `short_term_investment`
- `long_term_investment`
- `technical_analysis`
- `fundamental_analysis`
- `portfolio_analysis`
- `stock_comparison`
- `market_overview`
- `risk_assessment`

These instruct the model on the exact JSON keys required, while backend validation remains strictly authoritative.


