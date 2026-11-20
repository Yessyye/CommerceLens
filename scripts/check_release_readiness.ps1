param(
    [switch]$IncludeMcp
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Project Python environment is missing. See README.md.'
}

Push-Location $root
try {
    foreach ($module in @('question_routing', 'baseline', 'golden_sql', 'sql_policy', 'diagnostic_faults', 'agent_eval')) {
        $arguments = @('-m', "commercelens_eval.$module")
        if ($module -eq 'agent_eval') {
            $arguments += '--replay'
        }
        & $python @arguments
        if ($LASTEXITCODE -ne 0) {
            throw "$module failed with exit code $LASTEXITCODE"
        }
    }
    & $python -m commercelens_eval.agent_eval --replay --docker-review
    if ($LASTEXITCODE -ne 0) {
        throw "Docker trace replay failed with exit code $LASTEXITCODE"
    }
    if ($IncludeMcp) {
        & $python scripts/check_phase1_mcp.py --stdio
        if ($LASTEXITCODE -ne 0) {
            throw "MCP stdio failed with exit code $LASTEXITCODE"
        }
    }
} finally {
    Pop-Location
}
