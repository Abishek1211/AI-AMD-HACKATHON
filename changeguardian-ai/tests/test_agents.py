"""Tests for agent discovery and the BaseAgent contract."""
import pytest
from core.agent_discovery import discover_agents
from core.base_agent import BaseAgent


def test_agent_discovery_finds_agents():
    registry = discover_agents()
    assert len(registry) > 0, "No agents found in agents/ — add at least one"


def test_all_agents_have_unique_names():
    registry = discover_agents()
    assert len(registry) == len(set(registry.keys())), "Duplicate agent_name detected"


def test_all_agents_inherit_base_agent():
    registry = discover_agents()
    for name, cls in registry.items():
        assert issubclass(cls, BaseAgent), f"{cls.__name__} must inherit BaseAgent"
        assert cls.agent_name == name, f"agent_name mismatch: {cls.agent_name!r} vs registry key {name!r}"


def test_required_agents_are_present():
    registry = discover_agents()
    assert "risk_assessment_agent" in registry, "risk_assessment_agent is required"
    assert "rollout_agent" in registry, "rollout_agent is required"


def test_template_agent_is_excluded():
    registry = discover_agents()
    assert "template_agent" not in registry, "_template.py should be excluded from discovery"
