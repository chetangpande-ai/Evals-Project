from __future__ import annotations

import json
from pathlib import Path

from evals_project.schemas import EvalReport


def write_json_report(path: str | Path, report: EvalReport) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )


def write_markdown_report(path: str | Path, report: EvalReport) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Eval Report",
        "",
        f"- Run: `{report.run_id}`",
        f"- Dataset: `{report.dataset_path}`",
        f"- Passed: `{report.passed}`",
        f"- Overall score: `{report.overall_score}`",
        "",
        "| Case | Passed | Score | Failed Metrics |",
        "|---|---:|---:|---|",
    ]
    for result in report.results:
        failed = ", ".join(metric.name for metric in result.metrics if not metric.passed) or "-"
        lines.append(
            f"| `{result.case_id}` | {result.passed} | {result.overall_score} | {failed} |"
        )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
