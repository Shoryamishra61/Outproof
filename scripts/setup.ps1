$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
uv sync --python 3.12 --locked
if ($LASTEXITCODE -ne 0) { throw 'Python dependency setup failed' }
npm ci --prefix apps/web
if ($LASTEXITCODE -ne 0) { throw 'Web dependency setup failed' }
Write-Host 'Start API: uv run uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8000'
Write-Host 'Start web: npm run dev --prefix apps/web'
