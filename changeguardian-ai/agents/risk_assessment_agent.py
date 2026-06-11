"""
ChangeGuardian AI — Risk Assessment Agent
DEVELOPER ZONE: Customise the prompt and scoring logic as needed.
"""
from __future__ import annotations

import json

from core.base_agent import BaseAgent


SYSTEM_PROMPT = """
You are ChangeGuardian, an AI risk analyst for software deployments.

Given a change request, a list of affected services, and historical incidents,
produce a JSON object with these exact fields:

  risk_score   (integer 0–100, where 100 = highest risk)
  confidence   (integer 0–100)
  impact_level (one of: low, medium, high, critical)
  explanation  (2–3 plain-English sentences explaining the score)

Scoring guidance:
  - More affected services → higher risk
  - CRITICAL or HIGH severity incidents in the history → higher risk
  - Schema / database changes → higher risk than config changes
  - Version upgrades with past incidents on that service → elevated risk

Reply ONLY with valid JSON. No markdown fences.
""".strip()


class RiskAssessmentAgent(BaseAgent):
    agent_name = "risk_assessment_agent"

    async def run(self, state: dict) -> dict:
        context = json.dumps(
            {
                "change_request": state.get("change_request", ""),
                "affected_services": state.get("affected_services", []),
                "related_incidents": state.get("incidents", [])[:5],
            },
            indent=2,
        )
        result = await self._llm_json(SYSTEM_PROMPT, context)
        return {
            "risk_score": int(result.get("risk_score", 50)),
            "confidence": int(result.get("confidence", 50)),
            "impact_level": result.get("impact_level", "medium"),
            "explanation": result.get("explanation", ""),
        }
