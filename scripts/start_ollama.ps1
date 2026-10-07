param([switch]$Cpu)

$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:OLLAMA_HOST = '127.0.0.1:11434'
$env:OLLAMA_NO_CLOUD = 'true'
if ($Cpu) {
    $env:CUDA_VISIBLE_DEVICES = '-1'
    $env:OLLAMA_VULKAN = '0'
}
if (Test-Path -LiteralPath '.tools/ollama/ollama.exe') {
    $env:OLLAMA_MODELS = Join-Path (Get-Location) '.tools/models'
    & ./.tools/ollama/ollama.exe serve
} else {
    & ollama serve
}
if ($LASTEXITCODE -ne 0) { throw 'Ollama server failed' }
