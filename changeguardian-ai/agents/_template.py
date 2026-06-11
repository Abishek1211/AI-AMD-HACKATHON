"""
ChangeGuardian AI — Agent Template
============================================================
HOW TO CREATE A NEW AGENT

Step 1  Copy this file
        cp agents/_template.py agents/my_agent.py

Step 2  Rename the class
        class TemplateAgent  →  class MyAgent

Step 3  Set a unique agent_name
        agent_name = "my_agent"
        (Must match agent_name in config/routes.yaml)

Step 4  Write your system prompt in SYSTEM_PROMPT
        Tell the LLM exactly what JSON to return.

Step 5  Implement run()
        Use self._llm_json() for structured output.
        Return only the state keys you want to update.

Step 6  Add a route in config/routes.yaml
        - intent: "my_intent"
          description: "When the user does X."
          agent_name: "my_agent"

Step 7  Test
        python main.py --query "your test query"
        pytest tests/ -v
============================================================
"""
from __future__ import annotations

import json

from core.base_agent import BaseAgent


SYSTEM_PROMPT = """
You are a ChangeGuardian analysis agent.

[TODO: describe what this agent does and what JSON structure to return]

Example output:
  {
    "risk_score": 45,
    "explanation": "..."
  }

Reply ONLY with valid JSON. No markdown fences.
""".strip()


class TemplateAgent(BaseAgent):
    # ------------------------------------------------------------------ #
    # REQUIRED: unique name — must match agent_name in config/routes.yaml  #
    # ------------------------------------------------------------------ #
    agent_name = "template_agent"

    async def run(self, state: dict) -> dict:
        # Build context from state for the LLM
        context = json.dumps(
            {
                "change_request": state.get("change_request", ""),
                "affected_services": state.get("affected_services", []),
                "incidents": state.get("incidents", [])[:5],
            },
            indent=2,
        )

        # Call the LLM and parse the JSON response
        result = await self._llm_json(SYSTEM_PROMPT, context)

        # Return only the state fields this agent updates
        return {
            # TODO: map result fields to WorkflowState keys, e.g.
            # "risk_score": int(result.get("risk_score", 50)),
            # "explanation": result.get("explanation", ""),
        }
