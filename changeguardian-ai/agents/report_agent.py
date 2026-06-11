"""
ChangeGuardian AI — Executive Report Agent
DEVELOPER ZONE: Customise the report structure as needed.
"""
from __future__ import annotations

import json

from core.base_agent import BaseAgent


SYSTEM_PROMPT = """
You are ChangeGuardian, a technical writer for deployment risk reports.

Given the full analysis state, produce an executive summary as JSON:
  {
    "summary": "<2–3 sentence plain-English overview>",
    "key_risks": ["<risk 1>", "<risk 2>", "<risk 3>"],
    "next_steps": ["<action 1>", "<action 2>"],
    "approved_for_deployment": true | false
  }

Rules:
  - Set approved_for_deployment = false when risk_score >= 70 OR impact_level is "critical".
  - Keep key_risks to the top 3 most important items.
  - next_steps should be concrete and actionable.

Reply ONLY with valid JSON. No markdown fences.
""".strip()


class ReportAgent(BaseAgent):
    agent_name = "report_agent"

    async def run(self, state: dict) -> dict:
        context = json.dumps(
            {
                "change_request": state.get("change_request", ""),
                "risk_score": state.get("risk_score", 0),
                "confidence": state.get("confidence", 0),
                "impact_level": state.get("impact_level", "unknown"),
                "explanation": state.get("explanation", ""),
                "recommendation": state.get("recommendation", ""),
                "justification": state.get("justification", ""),
                "affected_services": state.get("affected_services", []),
                "incidents": state.get("incidents", [])[:3],
            },
            indent=2,
        )
        result = await self._llm_json(SYSTEM_PROMPT, context)
        return {"report": result}
