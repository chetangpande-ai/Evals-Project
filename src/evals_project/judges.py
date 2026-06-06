from __future__ import annotations

import json
import re

from evals_project.config import MeshAPISettings
from evals_project.llm import build_meshapi_chat_model
from evals_project.schemas import GeneratedArtifact, GoldenCase, MetricResult

SCRIPT_QUALITY_RUBRIC = """You are evaluating a generated Playwright-BDD test script.
Return only JSON with keys: score, reason.
Score from 0 to 1 using this rubric:
- The script covers every requested functional flow.
- BDD language is readable and business-facing.
- Assertions validate observable outcomes, not only page load.
- Missing test data is clearly identified instead of invented.
- Selectors and actions avoid brittle sleeps and hardcoded secrets.
"""


class MeshAPIScriptJudge:
    """LLM-as-judge evaluator backed by MeshAPI models."""

    def __init__(self, settings: MeshAPISettings | None = None) -> None:
        self.settings = settings or MeshAPISettings.from_env()
        self.model = build_meshapi_chat_model(self.settings)

    def score(self, case: GoldenCase, artifact: GeneratedArtifact) -> MetricResult:
        prompt = f"""{SCRIPT_QUALITY_RUBRIC}

Case:
{case.model_dump_json(indent=2)}

Generated feature:
{artifact.feature_text}

Generated step definitions:
{artifact.step_definition_text}

Missing data reported:
{json.dumps(artifact.missing_data)}
"""
        response = self.model.invoke(prompt)
        content = getattr(response, "content", str(response))
        payload = _extract_json(content)
        score = float(payload.get("score", 0))
        score = max(0.0, min(score, 1.0))
        return MetricResult(
            name="meshapi_llm_script_quality",
            score=score,
            passed=score >= 0.8,
            reason=str(payload.get("reason", "MeshAPI judge returned no reason")),
            details={"model": self.settings.model},
        )


def _extract_json(content: str) -> dict[str, object]:
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", content, flags=re.DOTALL)
    if match:
        parsed = json.loads(match.group(0))
        if isinstance(parsed, dict):
            return parsed
    raise ValueError(f"MeshAPI judge response was not JSON: {content[:200]}")
