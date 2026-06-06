from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from uuid import uuid4

from evals_project.agent_contract import FixtureScriptGenerator, ScriptGenerator
from evals_project.evaluators import evaluate_artifact
from evals_project.judges import MeshAPIScriptJudge
from evals_project.schemas import EvalReport, EvaluationResult, GoldenCase

try:
    from langsmith import traceable
except ImportError:

    def traceable(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        def decorator(func):  # type: ignore[no-untyped-def]
            return func

        return decorator


class EvalRunner:
    def __init__(
        self,
        generator: ScriptGenerator | None = None,
        include_llm_judge: bool = False,
    ) -> None:
        self.generator = generator or FixtureScriptGenerator()
        self.include_llm_judge = include_llm_judge
        self.llm_judge = MeshAPIScriptJudge() if include_llm_judge else None

    def run(self, cases: Iterable[GoldenCase], dataset_path: str | Path) -> EvalReport:
        results = [self.run_case(case) for case in cases]
        overall_score = round(
            sum(result.overall_score for result in results) / max(len(results), 1),
            3,
        )
        return EvalReport(
            run_id=str(uuid4()),
            dataset_path=str(dataset_path),
            passed=all(result.passed for result in results),
            overall_score=overall_score,
            results=results,
            metadata={
                "case_count": len(results),
                "include_llm_judge": self.include_llm_judge,
                "generator": self.generator.__class__.__name__,
            },
        )

    @traceable(name="test_script_generator_eval_case")
    def run_case(self, case: GoldenCase) -> EvaluationResult:
        artifact = self.generator.generate(case.input)
        result = evaluate_artifact(case, artifact)
        if self.llm_judge:
            judge_metric = self.llm_judge.score(case, artifact)
            metrics = [*result.metrics, judge_metric]
            overall_score = round(sum(metric.score for metric in metrics) / len(metrics), 3)
            return result.model_copy(
                update={
                    "metrics": metrics,
                    "overall_score": overall_score,
                    "passed": all(metric.passed for metric in metrics),
                }
            )
        return result
