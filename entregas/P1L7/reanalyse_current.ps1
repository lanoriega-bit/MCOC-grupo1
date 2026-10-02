param()
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$pythonExe = Join-Path $repoRoot '.venv-p1l5/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw 'Crea .venv-p1l5 e instala requirements.txt según README antes del reanálisis.'
}
Push-Location $repoRoot
try {
    & $pythonExe -B 'entregas/P1L7/invalidate_current.py'
    if ($LASTEXITCODE -ne 0) { throw 'No fue posible invalidar CURRENT antes del reanálisis.' }
    $scripts = @(
        'entregas/P1L5/analysis/apply_modification_request.py',
        'entregas/P1L5/analysis/week7_loads.py',
        'entregas/P1L5/modelo_central/validate_central_model.py',
        'entregas/P1L5/analysis/run_current_opensees.py',
        'entregas/P1L5/analysis/build_current_capacity.py',
        'entregas/P1L5/analysis/export_current_to_unity.py',
        'entregas/P1L6/desktop/export_current_member_identity.py',
        'entregas/P1L6/desktop/export_current_materials.py',
        'entregas/P1L6/preparation/build_ar_dataset.py',
        'entregas/P1L6/transform/build_geometry_overlay.py',
        'entregas/P1L6/transform/validate_ar_dataset.py',
        'entregas/P1L6/current_cleanup/validate_current_pipeline.py'
    )
    foreach ($script in $scripts) {
        & $pythonExe -B $script
        if ($LASTEXITCODE -ne 0) { throw "Falló $script; no declarar CURRENT actualizado." }
    }
} catch {
    & $pythonExe -B 'entregas/P1L7/invalidate_current.py'
    throw
} finally { Pop-Location }
