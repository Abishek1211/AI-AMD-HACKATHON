"""
ChangeGuardian AI — Agent Auto-Discovery
DO NOT MODIFY.

Scans the agents/ directory and registers every class that:
  • Inherits BaseAgent
  • Is not BaseAgent itself
  • Has a non-empty agent_name class variable

Files prefixed with _ (e.g. _template.py) are skipped.
"""
from __future__ import annotations

import importlib
import inspect
import logging
from pathlib import Path

from core.base_agent import BaseAgent

logger = logging.getLogger(__name__)


def discover_agents(agents_dir: str | Path = "agents") -> dict[str, type[BaseAgent]]:
    """
    Return ``{agent_name: AgentClass}`` for all discoverable agents.
    Called automatically by the orchestrator — no manual registration needed.
    """
    registry: dict[str, type[BaseAgent]] = {}
    agents_path = Path(agents_dir)

    for py_file in sorted(agents_path.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        module_name = f"agents.{py_file.stem}"
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            logger.warning("Could not import %s: %s", module_name, exc)
            continue

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(cls, BaseAgent)
                and cls is not BaseAgent
                and cls.agent_name
                and cls.agent_name not in registry
            ):
                registry[cls.agent_name] = cls
                logger.debug("Discovered: %s → %s", cls.agent_name, cls.__name__)

    logger.info(
        "Agent discovery complete — %d agent(s): %s",
        len(registry),
        list(registry),
    )
    return registry
