"""
ChangeGuardian AI — Demo Server
Uses Ollama (single batched LLM call) + in-memory mock graph. No Neo4j needed.

Run: py demo_server.py
"""
import json
import re
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from pydantic import BaseModel

OLLAMA_BASE_URL = "http://localhost:11434/v1"
MODEL = "qwen2.5:latest"

client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

# ---------------------------------------------------------------------------
# In-memory mock graph  (replaces Neo4j for the demo)
# ---------------------------------------------------------------------------

GRAPH: dict[str, list[str]] = {
    "payment-service":      ["order-service", "postgres-payments", "redis-cache", "payment-gateway-api"],
    "order-service":        ["payment-service", "user-service", "notification-service"],
    "user-service":         [],
    "notification-service": ["order-service"],
    "postgres-payments":    [],
    "redis-cache":          [],
    "payment-gateway-api":  [],
}

_p = Path("data/incidents/sample_incidents.json")
INCIDENTS: list[dict] = json.loads(_p.read_text()) if _p.exists() else [
    {"id": "INC-001", "title": "Payment timeout spike",   "severity": "HIGH",
     "root_cause": "payment-service v3.9 memory leak",     "impacted_services": ["payment-service"]},
    {"id": "INC-002", "title": "Order cascade failure",  "severity": "CRITICAL",
     "root_cause": "payment-service outage cascaded",       "impacted_services": ["order-service", "payment-service"]},
    {"id": "INC-003", "title": "Redis cache stampede",   "severity": "MEDIUM",
     "root_cause": "Cold start thundering herd",            "impacted_services": ["payment-service", "redis-cache"]},
]

# Strategies description map (used in the response to the frontend)
STRATEGY_DESC = {
    "direct":         "Deploy to all instances immediately. Low-risk only.",
    "canary":         "Route small traffic % first, then expand gradually.",
    "blue-green":     "Switch between two identical environments instantly.",
    "feature-flag":   "Deploy behind a flag; enable per user segment.",
    "staged-rollout": "Progress through regions with automated health gates.",
}

# ---------------------------------------------------------------------------
# Single-call prompt  — everything in one LLM call for speed
# ---------------------------------------------------------------------------

ANALYSIS_PROMPT = """
You are ChangeGuardian AI, a deployment risk analyst.
Given the change request, affected services, and historical incidents below,
produce a complete analysis as a single JSON object with these exact fields:

{
  "intent":          "<one of: service_upgrade|schema_change|config_change|dependency_update|infrastructure_change|general_change>",
  "risk_score":      <integer 0-100, higher = riskier>,
  "confidence":      <integer 0-100>,
  "impact_level":    "<low|medium|high|critical>",
  "explanation":     "<2-3 plain-English sentences explaining the risk score>",
  "recommendation":  "<one of: direct|canary|blue-green|feature-flag|staged-rollout>",
  "justification":   "<1-2 sentence rationale for the recommended strategy>",
  "key_risks":       ["<risk 1>", "<risk 2>", "<risk 3>"],
  "next_steps":      ["<action 1>", "<action 2>", "<action 3>"],
  "approved_for_deployment": <true|false>
}

Rules:
- risk_score >= 70 or impact_level = "critical"  →  approved_for_deployment = false
- More services affected + CRITICAL/HIGH incidents in history  →  higher risk_score
- Database/schema changes are riskier than config changes
- direct only for risk_score < 30; canary for 30-60; blue-green or staged-rollout for > 60

Reply ONLY with valid JSON. No markdown fences. No explanation outside the JSON.
""".strip()


def _extract_services(text: str) -> list[str]:
    return list({t for t in re.findall(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)+", text)})


def _get_affected(seeds: list[str]) -> list[str]:
    deps: set[str] = set(seeds)
    for s in seeds:
        deps.update(GRAPH.get(s, []))
    return list(deps)


def _get_incidents(services: list[str]) -> list[dict]:
    return [i for i in INCIDENTS if any(s in services for s in i.get("impacted_services", []))]


async def _llm_json(user_content: str) -> dict:
    resp = await client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": ANALYSIS_PROMPT},
            {"role": "user",   "content": user_content},
        ],
    )
    raw = resp.choices[0].message.content or "{}"
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[demo] ChangeGuardian AI demo server ready")
    print(f"[demo] LLM: {MODEL} via Ollama")
    print(f"[demo] Graph: {len(GRAPH)} nodes | {len(INCIDENTS)} incidents")
    yield


app = FastAPI(title="ChangeGuardian AI (Demo)", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    change_request: str


@app.post("/api/analyze-change")
async def analyze_change(body: AnalyzeRequest):
    text = body.change_request.strip()
    if not text:
        raise HTTPException(422, "change_request must not be empty")

    seeds = _extract_services(text)
    affected = _get_affected(seeds)
    incidents = _get_incidents(affected)

    user_msg = json.dumps({
        "change_request":    text,
        "affected_services": affected,
        "incidents":         incidents,
    }, indent=2)

    result = await _llm_json(user_msg)

    return {
        "risk_score":        int(result.get("risk_score", 50)),
        "confidence":        int(result.get("confidence", 50)),
        "impact_level":      result.get("impact_level", "medium"),
        "explanation":       result.get("explanation", ""),
        "recommendation":    result.get("recommendation", "canary"),
        "justification":     result.get("justification", ""),
        "affected_services": affected,
        "incidents":         incidents,
        "route":             result.get("intent", "general_change"),
        "report": {
            "summary":                 result.get("explanation", ""),
            "key_risks":               result.get("key_risks", []),
            "next_steps":              result.get("next_steps", []),
            "approved_for_deployment": result.get("approved_for_deployment", True),
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL, "backend": "ollama"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
