"""
ChangeGuardian AI — Shared Workflow State
DO NOT MODIFY.
"""
from typing import TypedDict


class WorkflowState(TypedDict, total=False):
    # ---- Input ----
    raw_input: str
    change_request: str

    # ---- Routing ----
    route: str          # intent name resolved from routes.yaml
    agent_name: str     # agent class name to execute

    # ---- Retrieved context ----
    dependencies: list[str]
    affected_services: list[str]
    incidents: list[dict]

    # ---- Risk assessment ----
    risk_score: int     # 0–100
    confidence: int     # 0–100
    impact_level: str   # low | medium | high | critical
    explanation: str

    # ---- Rollout recommendation ----
    recommendation: str  # direct | canary | blue-green | feature-flag | staged-rollout
    justification: str

    # ---- Guardrails ----
    guardrail_passed: bool
    guardrail_reason: str

    # ---- Final report ----
    report: dict
