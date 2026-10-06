param([string]$UnityEditor)
$ErrorActionPreference = 'Stop'
$projectConfig = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'config/project_config.json') -Raw | ConvertFrom-Json
$projectPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot $projectConfig.paths.unity)).Path
$versionFile = Join-Path $projectPath 'ProjectSettings/ProjectVersion.txt'
$version = ((Get-Content -LiteralPath $versionFile | Select-String '^m_EditorVersion:').Line -split ':',2)[1].Trim()
if (-not $UnityEditor) { $UnityEditor = Join-Path $env:ProgramFiles "Unity/Hub/Editor/$version/Editor/Unity.exe" }
if (-not (Test-Path -LiteralPath $UnityEditor)) { throw "No se encontró Unity $version. Indica su ejecutable con -UnityEditor." }
Start-Process -FilePath $UnityEditor -WindowStyle Hidden -ArgumentList @('-projectPath', ('"{0}"' -f $projectPath))
