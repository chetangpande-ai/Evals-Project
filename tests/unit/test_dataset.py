from __future__ import annotations

from pathlib import Path

from evals_project.dataset import load_golden_cases


def test_load_golden_cases() -> None:
    cases = load_golden_cases(Path("datasets/golden/test_script_generator.v1.jsonl"))

    assert cases
    assert cases[0].case_id == "auth_login_valid_missing_credentials"
    assert cases[0].input.generation_style == "python-pytest-bdd-playwright"
