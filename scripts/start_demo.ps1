param([int]$Port = 8501)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv/Scripts/python.exe'
$app = Join-Path $PSScriptRoot 'demo_app.py'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Project Python environment is missing. See README.md.'
}
& $python -m streamlit run $app --server.address 127.0.0.1 --server.port $Port --browser.gatherUsageStats false
exit $LASTEXITCODE
