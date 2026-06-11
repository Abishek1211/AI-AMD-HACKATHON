"""Tests for config loading, route validation, and guardrails."""
import pytest
from core import load_config, load_routes
from core.guardrails import InputGuardrail, OutputGuardrail


# ── Config ────────────────────────────────────────────────────────────────


def test_config_loads():
    cfg = load_config()
    assert isinstance(cfg, dict)


def test_config_required_sections():
    cfg = load_config()
    for section in ["llm", "neo4j", "vector_store", "guardrails", "api", "documents"]:
        assert section in cfg, f"Missing config section: {section}"


def test_config_llm_has_model():
    cfg = load_config()
    assert cfg["llm"].get("model"), "llm.model must not be empty"


# ── Routes ────────────────────────────────────────────────────────────────


def test_routes_load():
    routes = load_routes()
    assert isinstance(routes, list) and len(routes) > 0


def test_routes_required_fields():
    for r in load_routes():
        assert "intent" in r
        assert "description" in r
        assert "agent_name" in r


def test_route_agents_discoverable():
    from core.agent_discovery import discover_agents
    registry = discover_agents()
    for r in load_routes():
        assert r["agent_name"] in registry, (
            f"Route agent '{r['agent_name']}' not found — "
            f"create agents/{r['agent_name']}.py"
        )


# ── Guardrails ────────────────────────────────────────────────────────────


def test_input_guardrail_blocks_empty():
    g = InputGuardrail()
    passed, reason = g.check("")
    assert not passed


def test_input_guardrail_passes_valid():
    g = InputGuardrail()
    passed, _ = g.check("Upgrade payment-service from v4.0 to v4.2")
    assert passed


def test_input_guardrail_blocks_pii():
    g = InputGuardrail()
    passed, reason = g.check("Change made by john@example.com")
    assert not passed
    assert "PII" in reason


def test_output_guardrail_passes_valid():
    g = OutputGuardrail()
    state = {"risk_score": 55, "recommendation": "canary"}
    passed, _ = g.check(state)
    assert passed


def test_output_guardrail_blocks_out_of_range():
    g = OutputGuardrail()
    state = {"risk_score": 150, "recommendation": "canary"}
    passed, _ = g.check(state)
    assert not passed


def test_output_guardrail_blocks_missing_recommendation():
    g = OutputGuardrail()
    state = {"risk_score": 40, "recommendation": ""}
    passed, _ = g.check(state)
    assert not passed
