from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScriptStaticValidation:
    passed: bool
    score: float
    reasons: list[str] = field(default_factory=list)


SECRET_PATTERNS = [
    re.compile(r"password\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    re.compile(r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    re.compile(r"bearer\s+[a-z0-9_\-.]{12,}", re.IGNORECASE),
]


def validate_script_static(script_text: str) -> ScriptStaticValidation:
    checks = {
        "pytest_bdd_import": "pytest_bdd" in script_text,
        "playwright_import": "playwright" in script_text,
        "assertion_present": "expect(" in script_text or "assert " in script_text,
        "no_fixed_sleep": "time.sleep" not in script_text and "wait_for_timeout" not in script_text,
        "no_inline_secret": not any(pattern.search(script_text) for pattern in SECRET_PATTERNS),
    }
    failed = [name for name, passed in checks.items() if not passed]
    score = round(sum(1 for passed in checks.values() if passed) / len(checks), 3)
    return ScriptStaticValidation(
        passed=not failed,
        score=score,
        reasons=[f"Failed static checks: {', '.join(failed)}"] if failed else [],
    )
