"""
ChangeGuardian AI — Pre-flight Verification
DO NOT MODIFY.

Usage:
  python verify_setup.py

Fix all FAIL items before running the pipeline.
WARN items are non-blocking but recommended.
"""
import importlib
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
WARN = "\033[93mWARN\033[0m"


def check(label: str, condition: bool, message: str = "", warn: bool = False) -> bool:
    tag = PASS if condition else (WARN if warn else FAIL)
    print(f"  [{tag}] {label}")
    if not condition and message:
        print(f"         ↳ {message}")
    return condition


def main() -> int:
    print()
    print("=" * 58)
    print("    ChangeGuardian AI — Setup Verification")
    print("=" * 58)
    failures = 0

    # ── Python version ────────────────────────────────────────
    ok = sys.version_info >= (3, 12)
    if not check("Python 3.12+", ok, f"Found {sys.version.split()[0]} — upgrade required"):
        failures += 1

    # ── Required packages ─────────────────────────────────────
    packages = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "langgraph": "langgraph",
        "openai": "openai",
        "neo4j": "neo4j",
        "yaml": "pyyaml",
        "pydantic": "pydantic",
        "dotenv": "python-dotenv",
    }
    for import_name, install_name in packages.items():
        try:
            importlib.import_module(import_name)
            check(f"Package: {install_name}", True)
        except ImportError:
            check(f"Package: {install_name}", False, f"pip install {install_name}")
            failures += 1

    # ── Config files ──────────────────────────────────────────
    for f in ["config/config.yaml", "config/routes.yaml"]:
        ok = Path(f).exists()
        if not check(f"Config: {f}", ok, f"File not found — restore {f}"):
            failures += 1

    # ── .env / API keys ───────────────────────────────────────
    key = os.getenv("OPENAI_API_KEY", "")
    if not check("OPENAI_API_KEY set", bool(key), "Add OPENAI_API_KEY to .env"):
        failures += 1

    for var in ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"]:
        val = os.getenv(var, "")
        check(f"Env: {var}", bool(val), f"Set {var} in .env  (WARN — non-blocking)", warn=not bool(val))

    # ── Agent discovery ───────────────────────────────────────
    try:
        from core.agent_discovery import discover_agents
        registry = discover_agents()
        ok = len(registry) > 0
        if not check(f"Agents discovered ({len(registry)} found)", ok, "Add at least one agent in agents/"):
            failures += 1
    except Exception as exc:
        check("Agent discovery", False, str(exc))
        failures += 1

    # ── Route ↔ agent consistency ─────────────────────────────
    try:
        from core import load_routes
        from core.agent_discovery import discover_agents
        routes = load_routes()
        registry = discover_agents()
        check(f"Routes loaded ({len(routes)} defined)", len(routes) > 0, "Add routes in config/routes.yaml")
        for r in routes:
            name = r["agent_name"]
            ok = name in registry
            if not check(f"Route agent exists: {name}", ok, f"Create agents/{name}.py with agent_name='{name}'"):
                failures += 1
    except Exception as exc:
        check("Route validation", False, str(exc))
        failures += 1

    # ── Required agents ───────────────────────────────────────
    try:
        from core.agent_discovery import discover_agents
        registry = discover_agents()
        for required in ["risk_assessment_agent", "rollout_agent"]:
            if not check(f"Required agent: {required}", required in registry,
                         f"Ensure agents/{required}.py exists and agent_name='{required}'"):
                failures += 1
    except Exception:
        pass

    print("=" * 58)
    if failures == 0:
        print("  All checks passed — ready to run!")
        print("  Next: python ingest.py && python main.py")
    else:
        print(f"  {failures} check(s) FAILED — fix before running.")
    print("=" * 58)
    print()
    return failures


if __name__ == "__main__":
    sys.exit(main())
