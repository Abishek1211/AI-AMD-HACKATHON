"""
ChangeGuardian AI — Graph RAG Retriever
DO NOT MODIFY.

Four-step strategy:
  1. Graph query     → expand dependency graph from Neo4j
  2. Incident lookup → historical incidents for affected services
  3. Semantic rank   → score incidents by keyword relevance to change text
  4. Merge           → return unified context dict
"""
from __future__ import annotations

import logging
import re

from core.graph_client import Neo4jClient, neo4j_client

logger = logging.getLogger(__name__)


class ChangeGuardianRetriever:

    def __init__(self, client: Neo4jClient | None = None) -> None:
        self._neo4j = client or neo4j_client

    @staticmethod
    def _extract_service_names(text: str) -> list[str]:
        """Heuristic: pull hyphenated service-like tokens from the change text."""
        return list({t for t in re.findall(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)+", text)})

    @staticmethod
    def _semantic_rank(change_text: str, incidents: list[dict]) -> list[dict]:
        """
        Lightweight keyword overlap scorer.
        Replace with pgvector / Qdrant for production-quality semantic search.
        """
        tokens = set(re.findall(r"\w+", change_text.lower()))
        scored: list[tuple[int, dict]] = []
        for inc in incidents:
            blob = (inc.get("title", "") + " " + inc.get("root_cause", "")).lower()
            score = len(tokens & set(re.findall(r"\w+", blob)))
            scored.append((score, inc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [inc for _, inc in scored]

    async def step1_graph_dependencies(self, change_text: str) -> list[str]:
        seeds = self._extract_service_names(change_text)
        all_deps: set[str] = set(seeds)
        for seed in seeds:
            all_deps.update(await self._neo4j.find_dependencies(seed))
        return list(all_deps)

    async def step2_incident_lookup(self, services: list[str]) -> list[dict]:
        if not services:
            return []
        return await self._neo4j.find_incidents_for_services(services)

    def step3_semantic_rank(self, change_text: str, incidents: list[dict]) -> list[dict]:
        return self._semantic_rank(change_text, incidents)

    async def retrieve(self, change_text: str) -> dict:
        logger.debug("Retriever: '%s…'", change_text[:60])
        deps = await self.step1_graph_dependencies(change_text)
        raw_incidents = await self.step2_incident_lookup(deps)
        ranked = self.step3_semantic_rank(change_text, raw_incidents)
        return {"dependencies": deps, "incidents": ranked}


retriever = ChangeGuardianRetriever()
