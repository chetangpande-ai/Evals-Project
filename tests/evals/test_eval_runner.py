from __future__ import annotations

from pathlib import Path

from evals_project.dataset import load_golden_cases
from evals_project.runner import EvalRunner

DATASET = Path("datasets/golden/test_script_generator.v1.jsonl")


def test_deterministic_runner_passes_golden_dataset() -> None:
    cases = load_golden_cases(DATASET)
    report = EvalRunner().run(cases, DATASET)

    assert report.passed
    assert report.overall_score >= 0.8
    assert len(report.results) == 5


def test_missing_data_metric_surfaces_expected_keys() -> None:
    case = load_golden_cases(DATASET)[0]
    result = EvalRunner().run_case(case)
    metric = next(metric for metric in result.metrics if metric.name == "missing_data_detection")

    assert metric.passed
    assert metric.details["expected"] == ["customer_password", "customer_username"]
