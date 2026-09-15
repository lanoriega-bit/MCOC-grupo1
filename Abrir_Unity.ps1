$ErrorActionPreference = 'Stop'

$unityExe = 'C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe'
$p1l3Path = Join-Path $PSScriptRoot 'entregas\P1L3'
$projectCandidates = @(
    Get-ChildItem -LiteralPath $p1l3Path -Directory | Where-Object {
        Test-Path -LiteralPath (Join-Path $_.FullName 'viewer_unity\ProjectSettings\ProjectVersion.txt')
    } | ForEach-Object {
        Join-Path $_.FullName 'viewer_unity'
    }
)

if (-not (Test-Path -LiteralPath $unityExe)) {
    throw "No se encontró Unity en: $unityExe"
}

if ($projectCandidates.Count -ne 1) {
    throw "Se esperaba un unico Unity canonico bajo entregas\P1L3; encontrados: $($projectCandidates.Count)"
}
$projectPath = $projectCandidates[0]

Start-Process -FilePath $unityExe -WorkingDirectory (Split-Path -Parent $unityExe) -ArgumentList @(
    '-projectPath'
    ('"{0}"' -f $projectPath)
)
