from __future__ import annotations

from typing import TypedDict

from evals_project.agent_contract import FixtureScriptGenerator, ScriptGenerator
from evals_project.evaluators import evaluate_artifact
from evals_project.schemas import EvaluationResult, GeneratedArtifact, GoldenCase


class EvalGraphState(TypedDict):
    case: GoldenCase
    artifact: GeneratedArtifact | None
    result: EvaluationResult | None


def build_eval_graph(generator: ScriptGenerator | None = None):
    """Build a LangGraph workflow for generate -> evaluate.

    This keeps eval execution structurally aligned with the production agent graph.
    """

    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise RuntimeError(
            "LangGraph support requires the ai extra: uv run --extra ai ..."
        ) from exc

    script_generator = generator or FixtureScriptGenerator()

    def generate_node(state: EvalGraphState) -> EvalGraphState:
        artifact = script_generator.generate(state["case"].input)
        return {**state, "artifact": artifact}

    def evaluate_node(state: EvalGraphState) -> EvalGraphState:
        artifact = state["artifact"]
        if artifact is None:
            raise RuntimeError("Evaluation graph reached evaluate_node without an artifact")
        result = evaluate_artifact(state["case"], artifact)
        return {**state, "result": result}

    graph = StateGraph(EvalGraphState)
    graph.add_node("generate_script", generate_node)
    graph.add_node("evaluate_artifact", evaluate_node)
    graph.add_edge(START, "generate_script")
    graph.add_edge("generate_script", "evaluate_artifact")
    graph.add_edge("evaluate_artifact", END)
    return graph.compile()
