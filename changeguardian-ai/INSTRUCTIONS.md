# INSTRUCTIONS.md — ChangeGuardian AI Developer Guide

## Architecture Overview

```
┌──────────────────┐     ┌──────────────────────┐     ┌────────────────┐
│  Change Request  │────▶│  Input Guardrails     │────▶│ Router Agent   │
│  (user / API)    │     │  (empty, PII,         │     │ (LLM classifies│
└──────────────────┘     │   injection checks)   │     │  intent from   │
                         └──────────────────────┘     │  routes.yaml)  │
                                                       └───────┬────────┘
                                                               │
                         ┌──────────────────────┐             ▼
                         │  Final Response       │    ┌────────────────┐
                         │  (API / CLI output)   │    │  Graph RAG     │
                         └──────────▲────────────┘    │  Retriever     │
                                    │                 │  (Neo4j deps + │
                         ┌──────────┴────────────┐    │   incidents)   │
                         │  Output Guardrails    │    └───────┬────────┘
                         │  (score range,        │            │
                         │   completeness)       │            ▼
                         └──────────────────────┘    ┌────────────────┐
                                    ▲                │ Agent Executor │
                                    │                │ (developer-    │
                                    └────────────────│  written)      │
                                                     └────────────────┘
```

---

## What to Touch vs. What NOT to Touch

| File / Folder            | Zone              | Action                                      |
|--------------------------|-------------------|---------------------------------------------|
| `config/config.yaml`     | 👨‍💻 DEVELOPER     | Set models, toggles, API settings            |
| `config/routes.yaml`     | 👨‍💻 DEVELOPER     | Define intent → agent routing rules          |
| `agents/*.py`            | 👨‍💻 DEVELOPER     | Write your custom analysis agents here       |
| `data/documents/`        | 👨‍💻 DEVELOPER     | Drop source documents for ingestion          |
| `.env`                   | 👨‍💻 DEVELOPER     | Set API keys and environment values          |
| `core/*`                 | 🚫 DO NOT MODIFY  | Framework internals — no changes needed      |
| `verify_setup.py`        | 🚫 DO NOT MODIFY  | Pre-flight check script                      |
| `ingest.py`              | 🚫 DO NOT MODIFY  | Data ingestion entry point                   |
| `main.py`                | 🚫 DO NOT MODIFY  | CLI / server entry point                     |

---

## 6-Step Setup Guide

### Step 1: Install Dependencies

```bash
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt -c constraints.txt
```

### Step 2: Configure

```bash
cp .env.example .env
# Edit .env — set at minimum:
#   OPENAI_API_KEY=sk-...
#   NEO4J_URI=bolt://localhost:7687
#   NEO4J_USER=neo4j
#   NEO4J_PASSWORD=password
```

Then open `config/config.yaml` and adjust:
- `llm.model` — which LLM to use (`gpt-4o-mini`, `qwen2.5-72b-instruct`, …)
- `llm.base_url` — leave blank for OpenAI; set for Qwen or other compatible endpoints
- `vector_store.type` — `"faiss"` (local, free) or `"pinecone"` (cloud)
- `guardrails.input.enabled` / `guardrails.output.enabled` — toggle safety checks

### Step 3: Verify Setup

```bash
python verify_setup.py
```

Fix all **FAIL** items before proceeding. **WARN** items are non-blocking.

### Step 4: Add Documents (optional)

Drop `.txt`, `.pdf`, `.md`, `.json`, or `.csv` files into `data/documents/`.

### Step 5: Ingest Data

```bash
python ingest.py              # seed Neo4j + index documents
python ingest.py --neo4j-only # only seed Neo4j graph
python ingest.py --docs-only  # only index documents
```

### Step 6: Run

```bash
# Demo mode (runs example queries)
python main.py

# Single query
python main.py -q "Upgrade payment-service from v4.0 to v4.2"

# Interactive chat
python main.py -i

# Start FastAPI server (for the frontend)
python main.py --serve
```

---

## 4-Step New Agent Creation

### Step 1: Copy the Template

```bash
cp agents/_template.py agents/compliance_agent.py
```

### Step 2: Edit the Agent

Open `agents/compliance_agent.py` and:
1. **Rename the class**: `TemplateAgent` → `ComplianceAgent`
2. **Set agent_name**: `agent_name = "compliance_agent"`
3. **Write your system prompt**: instruct the LLM and define the JSON schema
4. **Implement run()**: build context from `state`, call `self._llm_json()`, return updated keys

### Step 3: Add a Route

Open `config/routes.yaml` and add:

```yaml
routes:
  # ... existing routes ...
  - intent: "compliance_check"
    description: "User wants to verify if a change meets compliance or regulatory requirements."
    agent_name: "compliance_agent"
```

### Step 4: Test

```bash
python verify_setup.py
pytest tests/ -v
python main.py -q "Is this change GDPR compliant?"
```

---

## Switching LLM Providers

Change **one value** in `config/config.yaml`:

```yaml
llm:
  model: "qwen2.5-72b-instruct"
  base_url: "https://your-qwen-endpoint/v1"
```

Set the matching key in `.env`:
```
OPENAI_API_KEY=your-qwen-compatible-key
OPENAI_BASE_URL=https://your-qwen-endpoint/v1
LLM_MODEL=qwen2.5-72b-instruct
```

No code changes needed — all agents use `self._llm_json()` from `BaseAgent`.

---

## Switching Vector Stores

Change **one value** in `config/config.yaml`:

```yaml
vector_store:
  type: "pinecone"    # was "faiss"
```

Fill in the Pinecone sub-config and re-run:
```bash
python ingest.py --docs-only
```

---

## Toggling Guardrails

All guardrail settings live in `config/config.yaml` — no code changes:

```yaml
guardrails:
  input:
    enabled: false        # disable all input checks
    block_pii: false      # allow PII in requests
    max_length: 5000      # raise the limit
  output:
    enabled: true
```

---

## Delivery Checklist

Before pushing your work:

- [ ] `python verify_setup.py` — all critical checks pass
- [ ] `pytest tests/ -v` — all tests pass
- [ ] `.env` is NOT committed (`.gitignore` covers it)
- [ ] Your agent file is in `agents/` and inherits `BaseAgent`
- [ ] Your route is in `config/routes.yaml` with matching `agent_name`
- [ ] Data is ingested (`python ingest.py` ran successfully)
- [ ] `python main.py -q "test"` returns a valid risk assessment

---

## Troubleshooting

| Problem                          | Fix                                                              |
|----------------------------------|------------------------------------------------------------------|
| `ModuleNotFoundError`            | `pip install -r requirements.txt -c constraints.txt`             |
| `FileNotFoundError: config.yaml` | Run from the project root directory (`changeguardian-ai/`)       |
| `OPENAI_API_KEY` not set         | Copy `.env.example` → `.env` and fill in the key                 |
| `No agents discovered`           | Add a `.py` file in `agents/` that inherits `BaseAgent`          |
| Route agent not found            | `agent_name` in `routes.yaml` must match the class `agent_name`  |
| Neo4j connection error           | Start Neo4j (`docker-compose up neo4j`) and check `.env` values  |
| Guardrail blocks valid input     | Tune `guardrails.input` settings in `config/config.yaml`         |

---

## Developer Cheat Sheet

```
┌─────────────────────────────────────────────────────────────┐
│               CHANGEGUARDIAN AI — QUICK REFERENCE           │
├─────────────────────────────────────────────────────────────┤
│  Verify:    python verify_setup.py                          │
│  Ingest:    python ingest.py                                │
│  Demo:      python main.py                                  │
│  Query:     python main.py -q "your change"                 │
│  Chat:      python main.py -i                               │
│  Server:    python main.py --serve                          │
│  Test:      pytest tests/ -v                                │
│  Docker:    docker-compose up                               │
│                                                             │
│  New agent: cp agents/_template.py agents/mine.py           │
│             Edit class, agent_name, prompt, run()           │
│             Add route in config/routes.yaml                 │
│             python verify_setup.py                          │
│                                                             │
│  Config:    config/config.yaml   (all settings)             │
│  Routes:    config/routes.yaml   (intent routing)           │
│  Docs:      data/documents/      (source files)             │
│  Env:       .env                 (API keys)                 │
└─────────────────────────────────────────────────────────────┘
```
