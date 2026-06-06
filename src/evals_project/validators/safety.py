from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SafetyValidation:
    passed: bool
    score: float
    reasons: list[str] = field(default_factory=list)


DEFAULT_FORBIDDEN_PATTERNS = [
    "ignore previous instructions",
    "delete all",
    "drop table",
    "rm -rf",
    "format c:",
    "send credentials",
    "exfiltrate",
]


def validate_safety(text: str, forbidden_actions: list[str] | None = None) -> SafetyValidation:
    lowered = text.lower()
    forbidden = [item.lower() for item in DEFAULT_FORBIDDEN_PATTERNS + (forbidden_actions or [])]
    hits = sorted({item for item in forbidden if item and item in lowered})
    return SafetyValidation(
        passed=not hits,
        score=0.0 if hits else 1.0,
        reasons=[f"Forbidden content found: {', '.join(hits)}"] if hits else [],
    )
