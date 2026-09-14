$ErrorActionPreference = 'Stop'

$unityExe = 'C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe'
$projectPath = Join-Path $PSScriptRoot 'entregas\P1L3\José\viewer_unity'

if (-not (Test-Path -LiteralPath $unityExe)) {
    throw "No se encontró Unity en: $unityExe"
}

if (-not (Test-Path -LiteralPath $projectPath)) {
    throw "No se encontró el proyecto en: $projectPath"
}

Start-Process -FilePath $unityExe -WorkingDirectory (Split-Path -Parent $unityExe) -ArgumentList @(
    '-projectPath'
    ('"{0}"' -f $projectPath)
)
