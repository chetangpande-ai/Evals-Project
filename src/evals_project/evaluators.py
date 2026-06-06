from __future__ import annotations

from evals_project.schemas import EvaluationResult, GeneratedArtifact, GoldenCase, MetricResult
from evals_project.validators.gherkin import validate_gherkin_structure
from evals_project.validators.safety import validate_safety
from evals_project.validators.script_static import validate_script_static


def evaluate_artifact(case: GoldenCase, artifact: GeneratedArtifact) -> EvaluationResult:
    metrics = [
        _bdd_structure_metric(case, artifact),
        _flow_coverage_metric(case, artifact),
        _missing_data_metric(case, artifact),
        _script_static_metric(artifact),
        _safety_metric(case, artifact),
    ]
    overall_score = round(sum(metric.score for metric in metrics) / len(metrics), 3)
    passed = all(metric.passed for metric in metrics)
    return EvaluationResult(
        case_id=case.case_id,
        passed=passed,
        overall_score=overall_score,
        metrics=metrics,
        artifact_summary={
            "missing_data": artifact.missing_data,
            "assumption_count": len(artifact.assumptions),
            "trace_metadata": artifact.trace_metadata,
        },
    )


def _bdd_structure_metric(case: GoldenCase, artifact: GeneratedArtifact) -> MetricResult:
    validation = validate_gherkin_structure(
        artifact.feature_text,
        case.expected.required_bdd_keywords,
    )
    return MetricResult(
        name="bdd_structure",
        score=validation.score,
        passed=validation.passed,
        reason="BDD structure is valid" if validation.passed else "; ".join(validation.reasons),
        details={
            "scenario_count": validation.scenario_count,
            "missing_keywords": validation.missing_keywords,
        },
    )


def _flow_coverage_metric(case: GoldenCase, artifact: GeneratedArtifact) -> MetricResult:
    combined = artifact.combined_text.lower()
    covered = [
        flow_id
        for flow_id in case.expected.required_flow_ids
        if f"@{flow_id.lower()}" in combined
    ]
    missing = [flow_id for flow_id in case.expected.required_flow_ids if flow_id not in covered]
    score = round(len(covered) / max(len(case.expected.required_flow_ids), 1), 3)
    reason = (
        "All required flows are covered"
        if not missing
        else f"Missing flows: {', '.join(missing)}"
    )
    return MetricResult(
        name="flow_coverage",
        score=score,
        passed=not missing,
        reason=reason,
        details={"covered": covered, "missing": missing},
    )


def _missing_data_metric(case: GoldenCase, artifact: GeneratedArtifact) -> MetricResult:
    expected = set(case.expected.required_missing_data_keys)
    actual = set(artifact.missing_data)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    score = 1.0 if not missing else round((len(expected) - len(missing)) / max(len(expected), 1), 3)
    return MetricResult(
        name="missing_data_detection",
        score=score,
        passed=not missing,
        reason=(
            "Required missing data is surfaced"
            if not missing
            else f"Missing data keys not surfaced: {', '.join(missing)}"
        ),
        details={"expected": sorted(expected), "actual": sorted(actual), "unexpected": unexpected},
    )


def _script_static_metric(artifact: GeneratedArtifact) -> MetricResult:
    validation = validate_script_static(artifact.step_definition_text)
    reason = (
        "Script passes static quality checks"
        if validation.passed
        else "; ".join(validation.reasons)
    )
    return MetricResult(
        name="script_static_quality",
        score=validation.score,
        passed=validation.passed,
        reason=reason,
    )


def _safety_metric(case: GoldenCase, artifact: GeneratedArtifact) -> MetricResult:
    validation = validate_safety(artifact.combined_text, case.expected.forbidden_actions)
    return MetricResult(
        name="safety",
        score=validation.score,
        passed=validation.passed,
        reason="No forbidden content found" if validation.passed else "; ".join(validation.reasons),
    )
