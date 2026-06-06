from __future__ import annotations

from evals_project.schemas import GeneratedArtifact
from evals_project.validators.gherkin import validate_gherkin_structure
from evals_project.validators.safety import validate_safety
from evals_project.validators.script_static import validate_script_static


def test_gherkin_validator_rejects_missing_then() -> None:
    validation = validate_gherkin_structure(
        "Feature: Demo\n  Scenario: Missing then\n    Given a user\n    When action happens\n",
        ["Feature", "Scenario", "Given", "When", "Then"],
    )

    assert not validation.passed
    assert "Then" in validation.missing_keywords


def test_script_static_rejects_fixed_sleep() -> None:
    validation = validate_script_static(
        "from pytest_bdd import given\nfrom playwright.sync_api import expect\n"
        "def test_it():\n    time.sleep(3)\n    expect(page.locator('body')).to_be_visible()\n"
    )

    assert not validation.passed
    assert validation.score < 1.0


def test_safety_rejects_forbidden_content() -> None:
    artifact = GeneratedArtifact(
        feature_text="Feature: Unsafe\nScenario: Bad\nGiven user\nWhen delete all records\nThen ok",
        step_definition_text="",
    )

    validation = validate_safety(artifact.combined_text)

    assert not validation.passed
