# ChangeGuardian AI

An **autonomous change impact analysis platform** that predicts deployment risk before production rollout — built with LangGraph, Neo4j, and OpenAI/Qwen.

---

## Features

- **LangGraph Pipeline** — Stateful graph workflow: guardrail → route → retrieve → assess → recommend → report
- **Neo4j Knowledge Graph** — Models service dependencies, APIs, databases, and historical incidents
- **Graph RAG Retrieval** — Discovers affected services and ranked related incidents automatically
- **Auto Agent Discovery** — Drop a `.py` file in `agents/` and it's live — no registration needed
- **Intent Routing** — LLM classifies the change type and routes to the right agent, configured in `routes.yaml`
- **Input / Output Guardrails** — PII detection, injection blocking, score validation — toggle in `config.yaml`
- **Switchable LLM** — OpenAI or any OpenAI-compatible endpoint (Qwen, Ollama) — change one config value
- **Switchable Vector Store** — FAISS (local, free) or Pinecone (cloud) — change one config value
- **Pre-flight Verification** — `verify_setup.py` checks everything before you run
- **CLI + REST API + Docker** — Multiple run modes out of the box

---

## Quick Start

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt -c constraints.txt

# 3. Configure
cp .env.example .env
# Edit .env — set OPENAI_API_KEY and NEO4J_* values

# 4. Verify setup
python verify_setup.py

# 5. Seed Neo4j graph + index documents
python ingest.py

# 6. Run!
python main.py --interactive
```

---

## Architecture

```
Change Request
      │
      ▼
┌─────────────────────┐
│  Input Guardrails   │ ── PII / injection / length check
└──────────┬──────────┘
           │
      ▼
┌─────────────────────┐
│   Router Agent      │ ── LLM classifies intent from routes.yaml
└──────────┬──────────┘
           │
      ▼
┌─────────────────────┐
│  Graph RAG Retriever│ ── Neo4j: dependency graph + related incidents
└──────────┬──────────┘
           │
      ▼
┌─────────────────────┐
│  Agent Executor     │ ── Developer-written risk assessment agent
└──────────┬──────────┘
           │
      ▼
┌─────────────────────┐
│  Rollout Executor   │ ── Rollout strategy recommendation agent
└──────────┬──────────┘
           │
      ▼
┌─────────────────────┐
│  Output Guardrails  │ ── Score range / completeness validation
└──────────┬──────────┘
           │
      ▼
   Risk Assessment + Recommendation
```

---

## Project Structure

```
changeguardian-ai/
├── core/                     # 🚫 DO NOT MODIFY — framework internals
│   ├── __init__.py           # Config loader, ${VAR} resolution, logging
│   ├── base_agent.py         # Abstract BaseAgent class
│   ├── state.py              # WorkflowState TypedDict
│   ├── graph_client.py       # Async Neo4j client
│   ├── retriever.py          # Graph RAG retriever pipeline
│   ├── guardrails.py         # Input / output guardrail agents
│   ├── agent_discovery.py    # Auto-discovers agents in agents/
│   └── orchestrator.py       # LangGraph pipeline orchestrator
├── agents/                   # 👨‍💻 DEVELOPER ZONE — write agents here
│   ├── risk_assessment_agent.py  # Risk scoring agent
│   ├── rollout_agent.py          # Deployment strategy agent
│   ├── report_agent.py           # Executive report agent
│   └── _template.py              # Blank template with step-by-step guide
├── config/                   # 👨‍💻 DEVELOPER ZONE — configure here
│   ├── config.yaml           # All settings (LLM, Neo4j, guardrails, …)
│   └── routes.yaml           # Intent → agent routing rules
├── api/                      # FastAPI server
│   └── server.py
├── data/
│   ├── documents/            # 👨‍💻 Drop source files here
│   ├── incidents/            # Sample incident data
│   ├── deployments/          # Sample deployment history
│   └── changes/              # Sample change requests
├── tests/
│   ├── test_agents.py        # Agent discovery & contract tests
│   └── test_pipeline.py      # Config, routes, guardrail tests
├── frontend/                 # React + Material UI + Cytoscape
├── verify_setup.py           # 🚫 Pre-flight check script
├── ingest.py                 # 🚫 Neo4j seeding + document indexing
├── main.py                   # 🚫 CLI + server entry point
├── requirements.txt
├── constraints.txt
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

---

## Creating a New Agent

```bash
# 1. Copy the template
cp agents/_template.py agents/my_agent.py

# 2. Edit: set agent_name, write system prompt, implement run()

# 3. Add a route in config/routes.yaml

# 4. Verify and test
python verify_setup.py
pytest tests/ -v
python main.py -q "test query"
```

See [INSTRUCTIONS.md](INSTRUCTIONS.md) for the full step-by-step guide.

---

## Configuration

All settings in `config/config.yaml`. Use `${VAR_NAME}` to pull from `.env`.

| Setting                      | Values                     | Description                        |
|------------------------------|----------------------------|------------------------------------|
| `llm.model`                  | Any model name             | LLM for all agents and routing     |
| `llm.base_url`               | URL or blank               | Set for Qwen / non-OpenAI endpoints |
| `vector_store.type`          | `faiss` / `pinecone`       | Switch vector store backend         |
| `guardrails.input.enabled`   | `true` / `false`           | Toggle input safety checks          |
| `guardrails.output.enabled`  | `true` / `false`           | Toggle output validation            |
| `neo4j.seed_demo_data`       | `true` / `false`           | Auto-seed demo graph on startup     |

---

## API

| Method | Endpoint              | Description                    |
|--------|-----------------------|--------------------------------|
| POST   | `/api/analyze-change` | Run the full analysis pipeline |
| GET    | `/health`             | Health check                   |

**Request:**
```json
{ "change_request": "Upgrade payment-service from v4.0 to v4.2" }
```

**Response:**
```json
{
  "risk_score": 82,
  "confidence": 91,
  "impact_level": "high",
  "recommendation": "canary",
  "justification": "...",
  "affected_services": ["payment-service", "order-service"],
  "explanation": "...",
  "incidents": [...],
  "route": "service_upgrade",
  "report": { "summary": "...", "approved_for_deployment": false }
}
```

---

## Neo4j Graph Model

| Node Types                            | Relationships                        |
|---------------------------------------|--------------------------------------|
| Service, Database, API, Incident      | CALLS, USES, DEPENDS_ON, CAUSED      |

---

## Testing

```bash
pytest tests/ -v
```

---

## Docker

```bash
docker-compose up          # starts Neo4j + backend + frontend
docker-compose up neo4j    # only start Neo4j
```

---

## License

MIT
