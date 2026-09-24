param(
    [switch]$UnityCompile
)

$ErrorActionPreference = 'Stop'
$p1l5Root = $PSScriptRoot
$repoRoot = (Resolve-Path (Join-Path $p1l5Root '..\..')).Path
$bundledPython = 'C:\Users\matis\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'

if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonExe = (Get-Command python).Source
} elseif (Test-Path -LiteralPath $bundledPython) {
    $pythonExe = $bundledPython
} else {
    throw 'No se encontró Python. Instala Python 3 o ejecuta desde Codex.'
}

Push-Location $repoRoot
try {
    function Invoke-CheckedPython([string]$script) {
        & $pythonExe $script
        if ($LASTEXITCODE -ne 0) { throw "Falló $script (exit $LASTEXITCODE)" }
    }

    Invoke-CheckedPython 'entregas/P1L5/modelo_central/validate_central_model.py'
    Invoke-CheckedPython 'entregas/P1L5/modelo_central/build_central_derivatives.py'
    Invoke-CheckedPython 'entregas/P1L5/modelo_central/Jose/qa_dinamico_p1l1_p1l4.py'
    Invoke-CheckedPython 'entregas/P1L5/modelo_central/Jose/qa_tributario.py'
    Invoke-CheckedPython 'entregas/P1L5/validation/audit_integrated_model.py'
    Invoke-CheckedPython 'entregas/P1L5/validation/test_single_source_propagation.py'

    if ($UnityCompile) {
        $unity = 'C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe'
        $project = Join-Path $repoRoot 'entregas\P1L3\José\viewer_unity'
        $log = Join-Path $p1l5Root 'validation\unity_compile.log'
        if (-not (Test-Path -LiteralPath $unity)) { throw 'Unity 6000.6.0f1 no está instalado.' }
        & $unity -batchmode -nographics -quit -projectPath $project -logFile $log
        if ($LASTEXITCODE -ne 0) { throw "Unity compile falló. Revisa $log" }
    }

    Write-Host 'Integridad central: PASS'
    Write-Host 'Análisis CURRENT: revisar bloqueos en entregas/P1L5/validation/INTEGRATION_QA.md'
} finally {
    Pop-Location
}
