"""
ChangeGuardian AI — BaseAgent
DO NOT MODIFY: Inherit from this class to create custom agents.

Quick-start:
    class MyAgent(BaseAgent):
        agent_name = "my_agent"

        async def run(self, state: dict) -> dict:
            result = await self._llm_json(SYSTEM_PROMPT, json.dumps(state))
            return {"risk_score": result["risk_score"]}
"""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod

from openai import AsyncOpenAI

from core import load_config

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    All ChangeGuardian agents must:
      1. Set a unique class-level ``agent_name`` string.
      2. Implement the ``run(state)`` async method.
    """

    agent_name: str = ""

    def __init__(self) -> None:
        if not self.agent_name:
            raise ValueError(f"{type(self).__name__} must define a non-empty agent_name")
        cfg = load_config().get("llm", {})
        self._client = AsyncOpenAI(
            api_key=cfg.get("api_key") or None,
            base_url=cfg.get("base_url") or None,
        )
        self._model: str = cfg.get("model", "gpt-4o-mini")
        self._temperature: float = float(cfg.get("temperature", 0.2))
        logger.debug("Agent '%s' initialised (model=%s)", self.agent_name, self._model)

    async def _llm(self, system: str, user: str) -> str:
        """Single-turn LLM call — returns raw content string."""
        resp = await self._client.chat.completions.create(
            model=self._model,
            temperature=self._temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content or ""

    async def _llm_json(self, system: str, user: str) -> dict:
        """Like ``_llm()`` but strips markdown fences and parses JSON."""
        raw = await self._llm(system, user)
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(raw)

    @abstractmethod
    async def run(self, state: dict) -> dict:
        """
        Process the current workflow state and return a partial state update.

        Parameters
        ----------
        state : dict
            Snapshot of the current WorkflowState.

        Returns
        -------
        dict
            Fields to merge back into the state (only changed keys needed).
        """
