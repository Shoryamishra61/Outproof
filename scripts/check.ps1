$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
uv run ruff check .
if ($LASTEXITCODE -ne 0) { throw 'Python lint failed' }
uv run ruff format --check .
if ($LASTEXITCODE -ne 0) { throw 'Python format check failed' }
uv run pytest
if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
uv run python scripts/export_contracts.py --check
if ($LASTEXITCODE -ne 0) { throw 'Schema drift check failed' }
uv run python evals/runner/contracts.py
if ($LASTEXITCODE -ne 0) { throw 'Contract eval failed' }
uv run python -m evals.runner.policy
if ($LASTEXITCODE -ne 0) { throw 'Policy eval failed' }
npm run check --prefix apps/web
if ($LASTEXITCODE -ne 0) { throw 'Web checks failed' }
