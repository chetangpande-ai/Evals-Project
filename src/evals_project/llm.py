from __future__ import annotations

from typing import Any

from evals_project.config import MeshAPISettings


def build_meshapi_chat_model(settings: MeshAPISettings | None = None) -> Any:
    """Build a LangChain chat model that targets MeshAPI's OpenAI-compatible endpoint."""

    mesh_settings = settings or MeshAPISettings.from_env()
    api_key = mesh_settings.require_api_key()

    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "MeshAPI LLM integration requires the ai extra: "
            "uv run --extra ai ..."
        ) from exc

    kwargs = {
        "model": mesh_settings.model,
        "temperature": mesh_settings.temperature,
        "timeout": mesh_settings.timeout_seconds,
    }

    try:
        return ChatOpenAI(api_key=api_key, base_url=mesh_settings.base_url, **kwargs)
    except TypeError:
        return ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=mesh_settings.base_url,
            **kwargs,
        )
