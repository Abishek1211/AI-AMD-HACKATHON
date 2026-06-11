"""
ChangeGuardian AI — FastAPI Server

Start via:
  python main.py --serve
  uvicorn api.server:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core import load_config, setup_logging
from core.graph_client import neo4j_client
from core.orchestrator import run_pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await neo4j_client.connect()
    await neo4j_client.seed_demo_data()
    yield
    await neo4j_client.close()


app = FastAPI(
    title="ChangeGuardian AI",
    description="Autonomous Change Impact Analysis Platform",
    version="0.1.0",
    lifespan=lifespan,
)

_cfg = load_config()
_origins = _cfg.get("api", {}).get("cors_origins", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins.split(",") if isinstance(_origins, str) else _origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    change_request: str


@app.post("/api/analyze-change")
async def analyze_change(body: AnalyzeRequest):
    result = await run_pipeline(body.change_request)
    if not result.get("guardrail_passed", True):
        raise HTTPException(status_code=422, detail=result.get("guardrail_reason", "Guardrail blocked request"))
    return {
        "risk_score": result.get("risk_score", 0),
        "confidence": result.get("confidence", 0),
        "recommendation": result.get("recommendation", "canary"),
        "justification": result.get("justification", ""),
        "affected_services": result.get("affected_services", []),
        "impact_level": result.get("impact_level", "unknown"),
        "explanation": result.get("explanation", ""),
        "incidents": result.get("incidents", []),
        "route": result.get("route", ""),
        "report": result.get("report", {}),
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
