"""
ChangeGuardian AI — Rollout Recommendation Agent
DEVELOPER ZONE: Customise the strategy definitions or add new ones.
"""
from __future__ import annotations

import json

from core.base_agent import BaseAgent


SYSTEM_PROMPT = """
You are ChangeGuardian, a deployment strategy advisor.

Given a risk score and context, recommend ONE of these rollout strategies:

  direct         — Deploy to all instances immediately. Use only for low-risk, well-tested changes.
  canary         — Route a small traffic percentage first, monitor, then expand gradually.
  blue-green     — Maintain two identical environments and switch traffic instantly after validation.
  feature-flag   — Deploy behind a flag and enable incrementally per user segment.
  staged-rollout — Progress through regions or clusters with automated health checks at each stage.

Reply ONLY with valid JSON:
  {
    "recommendation": "<strategy>",
    "justification": "<1–2 sentence rationale>"
  }

No markdown fences.
""".strip()


class RolloutAgent(BaseAgent):
    agent_name = "rollout_agent"

    async def run(self, state: dict) -> dict:
        context = json.dumps(
            {
                "change_request": state.get("change_request", ""),
                "risk_score": state.get("risk_score", 50),
                "impact_level": state.get("impact_level", "medium"),
                "risk_explanation": state.get("explanation", ""),
                "affected_services": state.get("affected_services", []),
            },
            indent=2,
        )
        result = await self._llm_json(SYSTEM_PROMPT, context)
        return {
            "recommendation": result.get("recommendation", "canary"),
            "justification": result.get("justification", ""),
        }
