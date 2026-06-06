from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class AppUnderTest(BaseModel):
    name: str
    url: str
    domain: str | None = None


class FlowSpec(BaseModel):
    id: str
    title: str
    goal: str
    user_role: str | None = None
    steps: list[str] = Field(default_factory=list)
    test_data_keys: list[str] = Field(default_factory=list)


class EvalInput(BaseModel):
    app: AppUnderTest
    flows: list[FlowSpec]
    known_test_data: dict[str, str] = Field(default_factory=dict)
    generation_style: Literal["python-pytest-bdd-playwright"] = "python-pytest-bdd-playwright"
    notes: str | None = None


class ExpectedOutput(BaseModel):
    required_flow_ids: list[str] = Field(default_factory=list)
    required_missing_data_keys: list[str] = Field(default_factory=list)
    required_bdd_keywords: list[str] = Field(
        default_factory=lambda: ["Feature", "Scenario", "Given", "When", "Then"]
    )
    forbidden_actions: list[str] = Field(default_factory=list)


class GoldenCase(BaseModel):
    case_id: str
    input: EvalInput
    expected: ExpectedOutput
    metadata: dict[str, Any] = Field(default_factory=dict)


class GeneratedArtifact(BaseModel):
    feature_text: str
    step_definition_text: str
    page_object_text: str = ""
    missing_data: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    trace_metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def combined_text(self) -> str:
        return "\n".join([self.feature_text, self.step_definition_text, self.page_object_text])


class MetricResult(BaseModel):
    name: str
    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    reason: str
    details: dict[str, Any] = Field(default_factory=dict)


class EvaluationResult(BaseModel):
    case_id: str
    passed: bool
    overall_score: float = Field(ge=0.0, le=1.0)
    metrics: list[MetricResult]
    artifact_summary: dict[str, Any] = Field(default_factory=dict)


class EvalReport(BaseModel):
    version: str = "1.0"
    run_id: str
    dataset_path: str
    passed: bool
    overall_score: float
    results: list[EvaluationResult]
    metadata: dict[str, Any] = Field(default_factory=dict)
