"""
ChangeGuardian AI — Core Framework
DO NOT MODIFY: These are the framework internals.
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()

_config: dict | None = None
_routes: list[dict] | None = None

_CONFIG_PATH = Path("config/config.yaml")
_ROUTES_PATH = Path("config/routes.yaml")


def _resolve(obj: Any) -> Any:
    """Recursively replace ${VAR_NAME} placeholders with environment variable values."""
    if isinstance(obj, str):
        return re.sub(r"\$\{(\w+)\}", lambda m: os.environ.get(m.group(1), ""), obj)
    if isinstance(obj, dict):
        return {k: _resolve(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolve(i) for i in obj]
    return obj


def load_config(path: str | Path | None = None) -> dict:
    global _config
    if _config is None:
        p = Path(path) if path else _CONFIG_PATH
        with p.open() as fh:
            _config = _resolve(yaml.safe_load(fh))
    return _config


def load_routes(path: str | Path | None = None) -> list[dict]:
    global _routes
    if _routes is None:
        p = Path(path) if path else _ROUTES_PATH
        with p.open() as fh:
            raw = yaml.safe_load(fh)
        _routes = raw.get("routes", [])
    return _routes


def setup_logging() -> None:
    cfg = load_config()
    level = cfg.get("logging", {}).get("level", "INFO") or "INFO"
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        level=getattr(logging, level.upper(), logging.INFO),
    )
