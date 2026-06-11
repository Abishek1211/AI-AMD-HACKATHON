"""
ChangeGuardian AI — Input / Output Guardrails
DO NOT MODIFY.

Toggle and tune guardrails in config/config.yaml under `guardrails:`.
"""
from __future__ import annotations

import logging
import re

from core import load_config

logger = logging.getLogger(__name__)

_PII_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),                                   # SSN
    re.compile(r"\b4[0-9]{12}(?:[0-9]{3})?\b"),                             # Visa
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),     # email
]

_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.I),
    re.compile(r"you\s+are\s+now\s+", re.I),
    re.compile(r"disregard\s+your\s+", re.I),
    re.compile(r"act\s+as\s+", re.I),
]


class InputGuardrail:
    def __init__(self) -> None:
        cfg = load_config().get("guardrails", {}).get("input", {})
        self.enabled: bool = str(cfg.get("enabled", "true")).lower() == "true"
        self.block_empty: bool = str(cfg.get("block_empty", "true")).lower() == "true"
        self.max_length: int = int(cfg.get("max_length", 2000))
        self.block_pii: bool = str(cfg.get("block_pii", "true")).lower() == "true"
        self.block_injection: bool = str(cfg.get("block_injection", "true")).lower() == "true"

    def check(self, text: str) -> tuple[bool, str]:
        """Returns (passed, reason). reason is empty on pass."""
        if not self.enabled:
            return True, ""
        if self.block_empty and not text.strip():
            return False, "change_request must not be empty"
        if len(text) > self.max_length:
            return False, f"change_request exceeds {self.max_length} characters"
        if self.block_pii:
            for pat in _PII_PATTERNS:
                if pat.search(text):
                    return False, "PII detected — remove personal data from the change request"
        if self.block_injection:
            for pat in _INJECTION_PATTERNS:
                if pat.search(text):
                    return False, "Prompt injection pattern detected"
        return True, ""


class OutputGuardrail:
    def __init__(self) -> None:
        cfg = load_config().get("guardrails", {}).get("output", {})
        self.enabled: bool = str(cfg.get("enabled", "true")).lower() == "true"
        self.min_score: int = int(cfg.get("min_risk_score", 0))
        self.max_score: int = int(cfg.get("max_risk_score", 100))

    def check(self, state: dict) -> tuple[bool, str]:
        """Returns (passed, reason)."""
        if not self.enabled:
            return True, ""
        score = state.get("risk_score", -1)
        if not isinstance(score, int) or not (self.min_score <= score <= self.max_score):
            return False, f"risk_score {score!r} is outside valid range [{self.min_score}, {self.max_score}]"
        if not state.get("recommendation"):
            return False, "Output is missing a rollout recommendation"
        return True, ""


input_guardrail = InputGuardrail()
output_guardrail = OutputGuardrail()
