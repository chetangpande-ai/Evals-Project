from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GherkinValidation:
    passed: bool
    score: float
    missing_keywords: list[str] = field(default_factory=list)
    scenario_count: int = 0
    reasons: list[str] = field(default_factory=list)


def validate_gherkin_structure(
    feature_text: str,
    required_keywords: list[str],
) -> GherkinValidation:
    normalized_lines = [line.strip().lower() for line in feature_text.splitlines()]
    missing = [
        keyword
        for keyword in required_keywords
        if not _keyword_present(normalized_lines, keyword.lower())
    ]
    scenario_count = sum(
        1
        for line in feature_text.splitlines()
        if line.strip().lower().startswith("scenario:")
    )

    reasons: list[str] = []
    if missing:
        reasons.append(f"Missing Gherkin keywords: {', '.join(missing)}")
    if scenario_count == 0:
        reasons.append("No scenarios found")

    scenario_blocks = _scenario_blocks(feature_text)
    incomplete_blocks = [
        title
        for title, body in scenario_blocks.items()
        if not all(keyword in body.lower() for keyword in ["given", "when", "then"])
    ]
    if incomplete_blocks:
        reasons.append(f"Incomplete Given/When/Then in: {', '.join(incomplete_blocks)}")

    keyword_score = 1.0 - (len(missing) / max(len(required_keywords), 1))
    scenario_score = 1.0 if scenario_count > 0 and not incomplete_blocks else 0.0
    score = round((keyword_score * 0.5) + (scenario_score * 0.5), 3)
    return GherkinValidation(
        passed=score >= 0.95,
        score=score,
        missing_keywords=missing,
        scenario_count=scenario_count,
        reasons=reasons,
    )


def _keyword_present(normalized_lines: list[str], keyword: str) -> bool:
    if keyword in {"feature", "scenario"}:
        return any(line.startswith(f"{keyword}:") for line in normalized_lines)
    return any(line == keyword or line.startswith(f"{keyword} ") for line in normalized_lines)


def _scenario_blocks(feature_text: str) -> dict[str, str]:
    blocks: dict[str, list[str]] = {}
    current_title: str | None = None
    for raw_line in feature_text.splitlines():
        line = raw_line.strip()
        if line.lower().startswith("scenario:"):
            current_title = line.removeprefix("Scenario:").strip()
            blocks[current_title] = []
        elif current_title:
            blocks[current_title].append(line)
    return {title: "\n".join(body) for title, body in blocks.items()}
