from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import find_dotenv, load_dotenv


def load_project_env(env_file: str | Path | None = None, *, override: bool = False) -> str | None:
    """Load local .env configuration without overriding exported shell variables."""

    requested_env_file = env_file or os.getenv("EVALS_ENV_FILE")
    if requested_env_file:
        resolved_env_file = Path(requested_env_file)
        if not resolved_env_file.exists():
            return None
        load_dotenv(resolved_env_file, override=override)
        return str(resolved_env_file)

    discovered_env_file = find_dotenv(".env", usecwd=True)
    if not discovered_env_file:
        return None

    load_dotenv(discovered_env_file, override=override)
    return discovered_env_file


load_project_env()


@dataclass(frozen=True)
class MeshAPISettings:
    """OpenAI-compatible MeshAPI settings."""

    api_key: str | None
    base_url: str = "https://api.meshapi.ai/v1"
    model: str = "openai/gpt-4o"
    temperature: float = 0.0
    timeout_seconds: float = 60.0

    @classmethod
    def from_env(cls) -> MeshAPISettings:
        return cls(
            api_key=os.getenv("MESHAPI_API_KEY") or os.getenv("MESH_API_KEY"),
            base_url=os.getenv("MESHAPI_BASE_URL", "https://api.meshapi.ai/v1"),
            model=os.getenv("MESHAPI_MODEL", "openai/gpt-4o"),
            temperature=float(os.getenv("MESHAPI_TEMPERATURE", "0")),
            timeout_seconds=float(os.getenv("MESHAPI_TIMEOUT_SECONDS", "60")),
        )

    def require_api_key(self) -> str:
        if not self.api_key:
            raise RuntimeError(
                "MeshAPI judge requested but MESHAPI_API_KEY is not set. "
                "Create a MeshAPI key and set MESHAPI_API_KEY=rsk_..."
            )
        return self.api_key


@dataclass(frozen=True)
class LangSmithSettings:
    tracing_enabled: bool
    project: str = "test-script-generator-evals"

    @classmethod
    def from_env(cls) -> LangSmithSettings:
        tracing_raw = os.getenv("LANGSMITH_TRACING") or os.getenv("LANGCHAIN_TRACING_V2")
        return cls(
            tracing_enabled=(tracing_raw or "").lower() in {"1", "true", "yes", "on"},
            project=os.getenv("LANGSMITH_PROJECT", "test-script-generator-evals"),
        )
