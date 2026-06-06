from __future__ import annotations

from typing import Protocol

from evals_project.schemas import EvalInput, FlowSpec, GeneratedArtifact


class ScriptGenerator(Protocol):
    """Contract implemented by the real LangGraph script generator agent."""

    def generate(self, eval_input: EvalInput) -> GeneratedArtifact:
        """Generate Playwright-BDD artifacts for the supplied application flows."""


class FixtureScriptGenerator:
    """Deterministic generator used to verify the eval harness itself.

    Replace this with the real LangGraph agent once the generator pipeline is wired.
    """

    def generate(self, eval_input: EvalInput) -> GeneratedArtifact:
        missing_data = sorted(
            {
                key
                for flow in eval_input.flows
                for key in flow.test_data_keys
                if key not in eval_input.known_test_data
            }
        )

        feature_text = self._feature_text(eval_input)
        step_definition_text = self._step_definitions(eval_input.flows)

        return GeneratedArtifact(
            feature_text=feature_text,
            step_definition_text=step_definition_text,
            missing_data=missing_data,
            assumptions=[
                "Selectors will be resolved by role, label, placeholder, or stable test id.",
                "Runtime secrets are injected from the test data provider, not hardcoded.",
            ],
            trace_metadata={
                "generator": "fixture",
                "style": eval_input.generation_style,
                "flow_count": len(eval_input.flows),
            },
        )

    def _feature_text(self, eval_input: EvalInput) -> str:
        lines = [
            f"Feature: {eval_input.app.name} browser flows",
            f"  The generated tests cover requested flows for {eval_input.app.url}.",
            "",
        ]
        for flow in eval_input.flows:
            lines.extend(self._scenario_lines(flow))
            lines.append("")
        return "\n".join(lines).strip() + "\n"

    @staticmethod
    def _scenario_lines(flow: FlowSpec) -> list[str]:
        role = flow.user_role or "standard user"
        lines = [
            f"  @{flow.id}",
            f"  Scenario: {flow.title}",
            f"    Given I am a {role}",
            "    And I open the application under test",
        ]

        if flow.steps:
            lines.append(f"    When I complete the flow step \"{flow.steps[0]}\"")
            for step in flow.steps[1:]:
                lines.append(f"    And I complete the flow step \"{step}\"")
        else:
            lines.append(f"    When I complete the requested flow \"{flow.goal}\"")

        lines.append(f"    Then I should see evidence that \"{flow.goal}\" succeeded")
        return lines

    @staticmethod
    def _step_definitions(flows: list[FlowSpec]) -> str:
        flow_titles = ", ".join(flow.title for flow in flows)
        return f'''from pytest_bdd import given, parsers, then, when
from playwright.sync_api import Page, expect


@given(parsers.parse("I am a {{role}}"))
def user_role(role: str) -> str:
    return role


@given("I open the application under test")
def open_application(page: Page, base_url: str) -> None:
    page.goto(base_url)


@when(parsers.parse('I complete the flow step "{{step}}"'))
def complete_flow_step(page: Page, step: str) -> None:
    page.get_by_text(step, exact=False).first.click()


@when(parsers.parse('I complete the requested flow "{{goal}}"'))
def complete_requested_flow(page: Page, goal: str) -> None:
    page.get_by_text(goal, exact=False).first.click()


@then(parsers.parse('I should see evidence that "{{goal}}" succeeded'))
def assert_flow_succeeded(page: Page, goal: str) -> None:
    expect(page.locator("body")).to_contain_text(goal.split()[0], timeout=10_000)


# Generated flow catalog: {flow_titles}
'''
