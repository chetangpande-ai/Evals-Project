from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from evals_project.dataset import load_golden_cases
from evals_project.report import write_json_report, write_markdown_report
from evals_project.runner import EvalRunner

app = typer.Typer(no_args_is_help=True)
console = Console()

DEFAULT_DATASET = Path("datasets/golden/test_script_generator.v1.jsonl")
DEFAULT_JSON_REPORT = Path("reports/eval-report.json")
DEFAULT_MD_REPORT = Path("reports/eval-report.md")


@app.callback()
def callback() -> None:
    """Evaluation commands for the test script generator agent."""


@app.command()
def run(
    dataset: Annotated[
        Path,
        typer.Option(help="Path to the JSONL golden dataset."),
    ] = DEFAULT_DATASET,
    report_json: Annotated[
        Path,
        typer.Option(help="JSON report path."),
    ] = DEFAULT_JSON_REPORT,
    report_md: Annotated[
        Path,
        typer.Option(help="Markdown report path."),
    ] = DEFAULT_MD_REPORT,
    include_llm_judge: Annotated[
        bool,
        typer.Option(help="Enable MeshAPI-backed LLM judge."),
    ] = False,
    fail_under: Annotated[
        float,
        typer.Option(min=0.0, max=1.0, help="Minimum overall score."),
    ] = 0.8,
) -> None:
    cases = load_golden_cases(dataset)
    runner = EvalRunner(include_llm_judge=include_llm_judge)
    report = runner.run(cases, dataset)
    write_json_report(report_json, report)
    write_markdown_report(report_md, report)

    table = Table(title="Test Script Generator Evals")
    table.add_column("Case")
    table.add_column("Passed", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Failed Metrics")
    for result in report.results:
        failed = ", ".join(metric.name for metric in result.metrics if not metric.passed) or "-"
        table.add_row(result.case_id, str(result.passed), f"{result.overall_score:.3f}", failed)
    console.print(table)
    console.print(f"JSON report: {report_json}")
    console.print(f"Markdown report: {report_md}")

    if not report.passed or report.overall_score < fail_under:
        raise typer.Exit(code=1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
