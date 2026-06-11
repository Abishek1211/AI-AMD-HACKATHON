"""
ChangeGuardian AI — LangGraph Orchestrator
DO NOT MODIFY.

Pipeline:
  input_guardrail → router → retriever → agent_executor
                           → rollout_executor → output_guardrail → END
  (input_guardrail → END  when guardrail blocks)
"""
from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import StateGraph, END

from core import load_config, load_routes
from core.base_agent import BaseAgent
from core.guardrails import input_guardrail, output_guardrail
from core.retriever import retriever
from core.agent_discovery import discover_agents

logger = logging.getLogger(__name__)

_ROUTER_SYSTEM = """
You are a change-request classifier for ChangeGuardian AI.
Given a change request and a list of intent definitions, reply with the
single intent name (from the list) that best matches. No explanation.
""".strip()

_agent_registry: dict[str, type[BaseAgent]] | None = None
_agent_instances: dict[str, BaseAgent] = {}


def _registry() -> dict[str, type[BaseAgent]]:
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = discover_agents()
    return _agent_registry


def _get_agent(name: str) -> BaseAgent:
    if name not in _agent_instances:
        reg = _registry()
        if name not in reg:
            raise KeyError(f"Agent '{name}' not found. Available: {list(reg)}")
        _agent_instances[name] = reg[name]()
    return _agent_instances[name]


# ---------------------------------------------------------------------------
# Node functions
# ---------------------------------------------------------------------------

async def _node_input_guardrail(state: dict[str, Any]) -> dict[str, Any]:
    passed, reason = input_guardrail.check(state.get("change_request", ""))
    return {**state, "guardrail_passed": passed, "guardrail_reason": reason}


async def _node_router(state: dict[str, Any]) -> dict[str, Any]:
    routes = load_routes()
    cfg = load_config().get("llm", {})
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=cfg.get("api_key") or None, base_url=cfg.get("base_url") or None)
    intent_list = "\n".join(f"- {r['intent']}: {r['description']}" for r in routes)
    resp = await client.chat.completions.create(
        model=cfg.get("model", "gpt-4o-mini"),
        temperature=0,
        messages=[
            {"role": "system", "content": _ROUTER_SYSTEM},
            {"role": "user", "content": f"Change: {state['change_request']}\n\nIntents:\n{intent_list}"},
        ],
    )
    intent = resp.choices[0].message.content.strip()
    agent_name = next(
        (r["agent_name"] for r in routes if r["intent"] == intent),
        routes[-1]["agent_name"],
    )
    logger.info("Router: intent=%s → agent=%s", intent, agent_name)
    return {**state, "route": intent, "agent_name": agent_name}


async def _node_retrieve(state: dict[str, Any]) -> dict[str, Any]:
    result = await retriever.retrieve(state["change_request"])
    return {**state, "dependencies": result["dependencies"], "affected_services": result["dependencies"], "incidents": result["incidents"]}


async def _node_agent_executor(state: dict[str, Any]) -> dict[str, Any]:
    agent = _get_agent(state.get("agent_name", "risk_assessment_agent"))
    return {**state, **await agent.run(state)}


async def _node_rollout_executor(state: dict[str, Any]) -> dict[str, Any]:
    try:
        return {**state, **await _get_agent("rollout_agent").run(state)}
    except KeyError:
        logger.warning("rollout_agent not found — skipping rollout step")
        return state


async def _node_output_guardrail(state: dict[str, Any]) -> dict[str, Any]:
    passed, reason = output_guardrail.check(state)
    return {**state, "guardrail_passed": passed, "guardrail_reason": reason}


def _route_after_input(state: dict[str, Any]) -> str:
    return "continue" if state.get("guardrail_passed", True) else "blocked"


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

_workflow = None


def build_workflow():
    builder = StateGraph(dict)
    builder.add_node("input_guardrail", _node_input_guardrail)
    builder.add_node("router", _node_router)
    builder.add_node("retriever", _node_retrieve)
    builder.add_node("agent_executor", _node_agent_executor)
    builder.add_node("rollout_executor", _node_rollout_executor)
    builder.add_node("output_guardrail", _node_output_guardrail)

    builder.set_entry_point("input_guardrail")
    builder.add_conditional_edges(
        "input_guardrail",
        _route_after_input,
        {"continue": "router", "blocked": END},
    )
    builder.add_edge("router", "retriever")
    builder.add_edge("retriever", "agent_executor")
    builder.add_edge("agent_executor", "rollout_executor")
    builder.add_edge("rollout_executor", "output_guardrail")
    builder.add_edge("output_guardrail", END)
    return builder.compile()


def get_workflow():
    global _workflow
    if _workflow is None:
        _workflow = build_workflow()
    return _workflow


async def run_pipeline(change_request: str) -> dict[str, Any]:
    initial: dict[str, Any] = {
        "raw_input": change_request,
        "change_request": change_request.strip(),
        "dependencies": [],
        "affected_services": [],
        "incidents": [],
        "risk_score": 0,
        "confidence": 0,
        "impact_level": "unknown",
        "explanation": "",
        "recommendation": "",
        "justification": "",
        "guardrail_passed": True,
        "guardrail_reason": "",
        "report": {},
    }
    return await get_workflow().ainvoke(initial)
