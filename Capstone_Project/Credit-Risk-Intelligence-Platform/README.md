# 🏦 Credit Risk Intelligence Platform — v2.0

> AI-powered financial document analysis, credit risk scoring, personalised recommendations,
> and an Early Retirement Planner — powered by Gemini + OpenAI + LangChain + FAISS.

---

## 📋 Table of Contents

1. [What Does This App Do?](#what-does-this-app-do)
2. [Prerequisites — What You Need](#prerequisites--what-you-need)
3. [Step 1 — Get Your API Keys](#step-1--get-your-api-keys)
4. [Step 2 — Clone / Unzip the Project](#step-2--clone--unzip-the-project)
5. [Step 3 — Create a Virtual Environment](#step-3--create-a-virtual-environment)
6. [Step 4 — Install Dependencies](#step-4--install-dependencies)
7. [Step 5 — Configure Your .env File](#step-5--configure-your-env-file)
8. [Step 6 — Run the Application](#step-6--run-the-application)
9. [Step 7 — Using the App](#step-7--using-the-app)
10. [Step 8 — Run the Tests](#step-8--run-the-tests)
11. [Optional — LangSmith Observability](#optional--langsmith-observability)
12. [Optional — Pinecone Cloud Vector Store](#optional--pinecone-cloud-vector-store)
13. [Optional — FastAPI Backend](#optional--fastapi-backend)
14. [Optional — Docker Deployment](#optional--docker-deployment)
15. [Troubleshooting](#troubleshooting)
16. [Project Structure](#project-structure)
17. [Bug Fixes in v2.0](#bug-fixes-in-v20)

---

## What Does This App Do?

Upload any financial PDF (bank statement, annual report, ITR, balance sheet) and get:

| Feature | Description |
|---|---|
| 📋 **Document Summary** | AI-extracted key financial figures and insights |
| 🔍 **Risk Analysis** | Credit risk score (0–100), strengths, red flags |
| 💡 **AI Recommendations** | Personalised action plan, safer loan options |
| 🏖️ **Retirement Planner** | Corpus calculation, SIP requirement, feasibility |
| 💬 **AI Chat** | Ask anything about your documents — RAG-grounded answers |

---

## Prerequisites — What You Need

| Tool | Version | Check if installed |
|---|---|---|
| Python | 3.10 or 3.11 (recommended) | `python --version` |
| pip | latest | `pip --version` |
| Internet access | For API calls | — |

> **Python 3.12** works but some packages may need extra flags.
> **Windows users**: use PowerShell or Command Prompt as Administrator.

---

## Step 1 — Get Your API Keys

You need **two API keys** to run the app. Both have free tiers.

### 🔵 Key 1: Google Gemini (AI model — FREE)

Gemini is the main AI brain. Free tier: 60 requests/minute, plenty for this app.

1. Open: **https://aistudio.google.com/app/apikey**
2. Sign in with any Google account
3. Click **"Create API key"** → **"Create API key in new project"**
4. Copy the key — it looks like: `AIzaSy...`
5. Save it somewhere safe (you'll paste it into `.env` shortly)

> 💡 If you see a quota error while using the app, the app automatically switches to OpenAI as a backup.

---

### 🟢 Key 2: OpenAI (Embeddings — PAID, ~$0.01 per document)

OpenAI is used ONLY for converting text to vectors (embeddings). It is NOT used for generating text (that's Gemini). You need a small credit balance.

1. Open: **https://platform.openai.com/api-keys**
2. Sign up / Log in
3. Add $5 credit: **Billing → Add payment method → Pay $5**
   - This $5 will last many months of normal use
4. Click **"Create new secret key"** → give it a name → **Create**
5. Copy the key immediately — OpenAI shows it only ONCE. It looks like: `sk-proj-...`

> ⚠️ If you already have an OpenAI key, just use it — no need to create a new one.

---

### 🟡 Key 3: LangSmith (Optional — traces your AI calls)

Only needed if you want to monitor AI calls. Skip for now, enable later.

1. Open: **https://smith.langchain.com**
2. Sign up free
3. Settings → API Keys → Create → Copy

---

## Step 2 — Clone / Unzip the Project

**Option A: You received a ZIP file**
```bash
# Unzip (Windows: right-click → Extract All)
unzip Credit-Risk-Platform-v2.zip
cd capstone
```

**Option B: Git clone**
```bash
git clone <your-repo-url>
cd capstone
```

Verify you see these files:
```
capstone/
├── app.py
├── requirements.txt
├── .env.example
├── config/
├── src/
├── ui/
└── ...
```

---

## Step 3 — Create a Virtual Environment

A virtual environment keeps this project's packages separate from your system Python.

### macOS / Linux:
```bash
# Create the virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# You should see (.venv) before your prompt now
```

### Windows (Command Prompt):
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1

# If you get an execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```

> ✅ Success: You see `(.venv)` at the start of your terminal prompt.

---

## Step 4 — Install Dependencies

```bash
# Make sure your virtual environment is activated first!
# You should see (.venv) in your prompt

pip install --upgrade pip
pip install -r requirements.txt
```

This installs ~50 packages. Expected time: **2–5 minutes** depending on internet speed.

> ⚠️ **If you see errors about PyMuPDF on Windows:**
> ```cmd
> pip install pymupdf --no-cache-dir
> ```

> ⚠️ **If you see errors about faiss-cpu:**
> ```bash
> # Try the prebuilt binary:
> pip install faiss-cpu --prefer-binary
> ```

> ✅ **Success:** Last line shows `Successfully installed ...`

---

## Step 5 — Configure Your .env File

```bash
# Copy the template
cp .env.example .env
```

Now open `.env` in any text editor (Notepad, VS Code, nano, etc.):

```bash
# macOS/Linux
nano .env
# OR
code .env   # if VS Code is installed

# Windows
notepad .env
```

Fill in these values (the ones you collected in Step 1):

```dotenv
# REQUIRED — paste your Gemini key here
GEMINI_API_KEY=AIzaSy_your_actual_key_here

# REQUIRED — paste your OpenAI key here
OPENAI_API_KEY=sk-proj-your_actual_key_here

# Leave everything else as-is for now
```

Save the file. **Do NOT commit `.env` to git** — it has your secret keys!

### Verify your .env is correct:
```bash
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
gemini = os.getenv('GEMINI_API_KEY', '')
openai = os.getenv('OPENAI_API_KEY', '')
print('Gemini key:', 'SET ✅' if gemini and gemini != 'your_gemini_api_key_here' else 'MISSING ❌')
print('OpenAI key:', 'SET ✅' if openai and openai != 'your_openai_api_key_here' else 'MISSING ❌')
"
```

Expected output:
```
Gemini key: SET ✅
OpenAI key: SET ✅
```

---

## Step 6 — Run the Application

```bash
# Make sure (.venv) is active
streamlit run app.py
```

Your browser opens automatically at **http://localhost:8501**

If it doesn't open automatically, copy `http://localhost:8501` into your browser.

> ✅ **Success:** You see the Credit Risk Intelligence Platform dashboard with a dark theme and the sidebar navigation.

---

## Step 7 — Using the App

### Upload a Document (start here)

1. Click **"📤 Upload Documents"** in the sidebar
2. Drag & drop a PDF file (annual report, bank statement, etc.)
   - For testing, download any public company annual report from their website
   - Example: HDFC Bank Annual Report — search "HDFC Bank annual report 2023 PDF"
3. Click **"🚀 Process All Documents"**
4. Wait for processing (30–90 seconds per document)

### Generate Analysis

5. Click **"🔍 Risk Analysis"** → Click **"Run / Refresh Risk Analysis"**
6. Click **"💡 AI Recommendations"** → Click **"Generate Recommendations"**
7. Click **"💬 AI Chat"** → Click any suggested question or type your own

### Retirement Planner

8. Click **"🏖️ Retirement Planner"**
9. Fill in your details (age, income, savings, etc.)
10. Click **"Calculate My Retirement Plan"**
11. View Results tab for corpus needed, required SIP, and AI advice

---

## Step 8 — Run the Tests

```bash
# Run all unit tests (no API keys needed)
python -m pytest tests/unit/ -v

# Expected output:
# 17 passed, 1 skipped
```

What the tests verify:
- ✅ FAISS index load path bug is FIXED
- ✅ Financial sampling selects high-value content (not boilerplate)  
- ✅ Document chunker produces correct metadata
- ✅ Retirement corpus calculations are mathematically correct
- ✅ All schema models work correctly

---

## Optional — LangSmith Observability

LangSmith shows you every AI call, embedding, and retrieval in a web dashboard. Great for debugging.

### Setup (5 minutes):
1. Go to **https://smith.langchain.com** → Sign Up (free)
2. Create a project: Settings → Projects → **"credit-risk-platform"**
3. Get API key: Settings → API Keys → Create key

### Enable in .env:
```dotenv
LANGCHAIN_API_KEY=ls__your_key_here
LANGCHAIN_PROJECT=credit-risk-platform
LANGCHAIN_TRACING_V2=true
```

4. Restart the app: `Ctrl+C` then `streamlit run app.py`
5. Use the app normally — traces appear at **https://smith.langchain.com**

---

## Optional — Pinecone Cloud Vector Store

By default the app uses **FAISS** (local files). For production deployment, use **Pinecone**.

### When to use Pinecone:
- Deploying to Railway/Render/cloud (FAISS files don't persist there)
- Need to handle many documents without running out of RAM

### Setup (10 minutes, free tier: 1 index, 1GB):
1. Go to **https://app.pinecone.io** → Sign Up
2. Click **"Create Index"**:
   - Name: `credit-risk-platform`
   - Dimensions: `1536`
   - Metric: `cosine`
   - Region: `us-east-1`
3. Go to **API Keys** → Copy your API key

### Enable in .env:
```dotenv
VECTOR_STORE_PROVIDER=pinecone
PINECONE_API_KEY=your_key_here
PINECONE_INDEX_NAME=credit-risk-platform
PINECONE_REGION=us-east-1
```

### Install Pinecone packages:
```bash
pip install pinecone-client langchain-pinecone
```

---

## Optional — FastAPI Backend

The app includes a REST API layer for external integrations.

```bash
# In a second terminal (virtual env activated):
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Test the health endpoint:
curl http://localhost:8000/health

# Interactive API docs:
open http://localhost:8000/docs
```

---

## Optional — Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose -f infra/docker-compose.yml up --build

# App available at http://localhost:8501
```

Requirements: Docker Desktop installed and running.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'X'"
```bash
# Make sure your virtual environment is activated:
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate.bat  # Windows

# Reinstall dependencies:
pip install -r requirements.txt
```

### "GEMINI_API_KEY not set" error
Your `.env` file is missing or not loaded. Check:
```bash
# The .env file should be at the ROOT of the project (same folder as app.py):
ls -la .env   # Should show the file

# Verify the key is set (not the placeholder):
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GEMINI_API_KEY', 'MISSING')[:10])"
```

### "429 Resource Exhausted" (Gemini quota error)
Gemini free tier has rate limits. Solutions:
1. Wait 60 seconds and retry
2. Or: set `LLM_PROVIDER=openai` in `.env` (uses OpenAI instead)
3. Or: upgrade Gemini to pay-as-you-go (very cheap)

### "OpenAI quota exceeded / insufficient_quota"
Your OpenAI account needs credit. Add $5 at https://platform.openai.com/billing

### "FAISS index not found" (re-indexing required)
This is expected on first run after clearing data. Just re-upload your documents.

### App is slow on first document
First run builds the embedding index. Subsequent queries are fast (cached in FAISS).

### "Streamlit: DuplicateWidgetID" error
This can happen after hot-reload. Refresh your browser (F5).

### Windows: "cannot import 'fitz'" error
```cmd
pip uninstall pymupdf fitz
pip install pymupdf --no-cache-dir
```

---

## Project Structure

```
capstone/
├── README.md               ← You are here
├── app.py                  ← Streamlit entry point (run this)
├── requirements.txt        ← All Python dependencies
├── .env.example            ← Copy to .env and fill in keys
├── .gitignore
│
├── config/
│   └── settings.py         ← All configuration (loaded from .env)
│
├── docs/
│   ├── architecture.md     ← System architecture diagrams
│   └── decisions.md        ← Why we made each technical decision
│
├── src/                    ← All backend logic
│   ├── agents/
│   │   ├── document_agent.py      ← PDF extraction + summarisation
│   │   ├── retrieval_agent.py     ← Vector search (MMR, Top-K=6)
│   │   └── chat_agent.py          ← All LLM interactions
│   ├── orchestrator/
│   │   └── orchestrator.py        ← Coordinates the 3 agents
│   ├── retrieval/
│   │   ├── chunker.py             ← Smart document chunking
│   │   ├── vector_store.py        ← FAISS (local) + Pinecone (cloud)
│   │   ├── loader.py              ← PDF loading with OCR fallback
│   │   └── sampling.py            ← Financial content extraction
│   ├── api/
│   │   └── main.py                ← FastAPI REST endpoints (optional)
│   ├── prompts/                   ← All LLM prompt templates
│   ├── evaluation/                ← RAGAS + DeepEval (backend only)
│   ├── llm/                       ← Gemini + OpenAI providers
│   ├── models/schemas.py          ← All Pydantic data models
│   ├── services/langsmith_setup.py
│   └── utils/logger.py
│
├── ui/                     ← Streamlit frontend
│   ├── theme.py            ← Global styles and component helpers
│   ├── sidebar.py          ← Navigation
│   └── pages/
│       ├── dashboard.py
│       ├── upload.py
│       ├── summary.py
│       ├── risk_analysis.py
│       ├── recommendations.py  ← 4 modules + conditional display
│       ├── chat.py             ← Validated suggested questions
│       └── retirement_planner.py   ← NEW
│
├── infra/                  ← Deployment
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── railway/            ← Railway.app deployment
│
├── tests/
│   └── unit/               ← pytest unit tests (no API keys needed)
│
└── data/
    ├── uploads/            ← PDFs you upload (git-ignored)
    ├── vectorstore/        ← FAISS index (auto-created)
    └── demo/               ← Put sample PDFs here for testing
```

---

## Bug Fixes in v2.0

| # | Bug | Location | Impact | Fix |
|---|---|---|---|---|
| 1 | FAISS index never loaded from disk | `src/retrieval/vector_store.py` | Critical — re-indexed every startup | Changed `.with_suffix(".faiss")` → `/ "index.faiss"` |
| 2 | `@lru_cache` baked LLM at import time | `src/llm/llm_factory.py` | Settings changes silently ignored | Replaced with module-level cache + `clear_provider_cache()` |
| 3 | `_extract_financial_sample` coupled across modules | `src/retrieval/sampling.py` | Circular import risk | Extracted to dedicated module |
| 4 | `similarity_search(k=settings.TOP_K)` baked at import | `src/agents/retrieval_agent.py` | Default K frozen at startup | Changed to `k: int | None = None` |
| 5 | Hex color parse crash in recommendations | `ui/pages/recommendations.py` | `int(..., 16)` crash on some colors | Replaced with pre-defined color tuples |
| 6 | Top-K=12 too noisy, no diversity | `src/retrieval/vector_store.py` | Redundant chunks, worse answers | Reduced to K=6 with MMR |
| 7 | Financial sampling used index order | `src/retrieval/sampling.py` | Late-document financial data ignored | Sort by score DESC, then reorder by index |

---

## Support

- 📖 LangChain docs: https://python.langchain.com
- 📖 Streamlit docs: https://docs.streamlit.io
- 🔑 Gemini keys: https://aistudio.google.com/app/apikey
- 🔑 OpenAI keys: https://platform.openai.com/api-keys
- 📊 LangSmith: https://smith.langchain.com
- 🗄️ Pinecone: https://app.pinecone.io
