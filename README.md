# Evals Project

Evaluation foundation for a Python/LangChain/LangGraph test script generator agent that produces Playwright-BDD style scripts.

![2D evaluation system overview](docs/assets/evals-system-2d.png)

The visual above summarizes the intended eval operating system: golden datasets, deterministic checks, tracing, CI gates, online monitoring, and human review around the generated Playwright-BDD scripts.

The first checkpoint implements:

- Versioned golden dataset for app-flow-to-test-script generation.
- Deterministic evaluators for BDD structure, flow coverage, missing data, static script quality, and safety.
- MeshAPI-compatible LLM judge adapter for semantic quality checks.
- LangSmith-ready tracing hooks and optional LangGraph eval workflow.
- CI-friendly pytest runner.
- React dashboard scaffold for viewing eval reports.

## MeshAPI Configuration

MeshAPI is OpenAI-compatible. Configure it through environment variables:

```powershell
$env:MESHAPI_API_KEY = "rsk_your_key"
$env:MESHAPI_BASE_URL = "https://api.meshapi.ai/v1"
$env:MESHAPI_MODEL = "openai/gpt-4o"
```

Optional LangSmith tracing:

```powershell
$env:LANGSMITH_TRACING = "true"
$env:LANGSMITH_API_KEY = "lsv2_your_key"
$env:LANGSMITH_PROJECT = "test-script-generator-evals"
```

## Local Commands

Install and run deterministic eval tests:

```powershell
uv run --extra dev pytest
```

Run the eval harness over the golden dataset:

```powershell
uv run --extra dev evals-project run `
  --dataset datasets/golden/test_script_generator.v1.jsonl `
  --report-json reports/eval-report.json `
  --report-md reports/eval-report.md
```

Run with MeshAPI-backed LLM judge enabled:

```powershell
uv run --extra ai --extra dev evals-project run `
  --dataset datasets/golden/test_script_generator.v1.jsonl `
  --include-llm-judge
```

## Current Eval Gates

- BDD structure score must pass.
- Required flows must be represented.
- Required missing-data keys must be surfaced.
- Generated script must include Playwright and BDD integration markers.
- Unsafe/destructive content must be absent.
- Overall score defaults to `0.8`.

## React Dashboard

The UI scaffold lives in `ui/` and reads the same report shape emitted by the CLI.

```powershell
cd ui
npm install
npm run dev
```
