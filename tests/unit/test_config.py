from __future__ import annotations

import os

from evals_project.config import MeshAPISettings, load_project_env


def test_load_project_env_reads_dotenv_file(monkeypatch, tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("EVALS_PROJECT_TEST_VALUE=from-dotenv\n", encoding="utf-8")
    monkeypatch.delenv("EVALS_PROJECT_TEST_VALUE", raising=False)

    loaded_path = load_project_env(env_file)

    assert loaded_path == str(env_file)
    assert os.getenv("EVALS_PROJECT_TEST_VALUE") == "from-dotenv"


def test_meshapi_settings_reads_values_loaded_from_dotenv(monkeypatch, tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("MESHAPI_MODEL=meshapi/test-model\n", encoding="utf-8")
    monkeypatch.delenv("MESHAPI_MODEL", raising=False)

    load_project_env(env_file)

    assert MeshAPISettings.from_env().model == "meshapi/test-model"
