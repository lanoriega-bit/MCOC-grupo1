param()
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$pythonExe = Join-Path $repoRoot '.venv-p1l5/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw 'Crea .venv-p1l5 e instala requirements.txt según README antes del reanálisis.'
}
Push-Location $repoRoot
try {
    & $pythonExe -B 'analysis/postprocessing/invalidate.py'
    if ($LASTEXITCODE -ne 0) { throw 'No fue posible invalidar CURRENT antes del reanálisis.' }
    $scripts = @(
        'analysis/opensees/apply_request.py',
        'analysis/opensees/live_loads.py',
        'tests/model/validate_model.py',
        'analysis/opensees/run_cases.py',
        'analysis/capacity/build_capacity.py',
        'analysis/postprocessing/export_unity.py',
        'entregas/P1L6/desktop/export_current_member_identity.py',
        'entregas/P1L6/desktop/export_current_materials.py',
        'ar/data/build_dataset.py',
        'ar/transforms/build_geometry_overlay.py',
        'ar/tests/validate_ar_dataset.py',
        'tests/model/validate_pipeline.py'
    )
    foreach ($script in $scripts) {
        & $pythonExe -B $script
        if ($LASTEXITCODE -ne 0) { throw "Falló $script; no declarar CURRENT actualizado." }
    }
} catch {
    & $pythonExe -B 'analysis/postprocessing/invalidate.py'
    throw
} finally { Pop-Location }
