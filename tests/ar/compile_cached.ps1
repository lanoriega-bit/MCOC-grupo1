param([string]$UnityData)
# Diagnostic only: cached references cannot replace a licensed clean Unity build.
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$config = Get-Content -LiteralPath (Join-Path $repoRoot 'config/project_config.json') -Raw | ConvertFrom-Json
$projectRoot = (Resolve-Path (Join-Path $repoRoot $config.paths.unity)).Path
if (-not $UnityData) {
    $versionLine = Get-Content -LiteralPath (Join-Path $projectRoot 'ProjectSettings/ProjectVersion.txt') | Select-String '^m_EditorVersion:'
    $editorVersion = ($versionLine.Line -split ':',2)[1].Trim()
    $UnityData = Join-Path $env:ProgramFiles "Unity/Hub/Editor/$editorVersion/Editor/Data"
}
$response = Get-ChildItem -LiteralPath (Join-Path $projectRoot 'Library/Bee/artifacts') -Recurse -Filter 'Assembly-CSharp.rsp' |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $response) { throw 'No cached compiler response. Open the project with a licensed Unity Editor first.' }
$sdk = Get-ChildItem -LiteralPath (Join-Path $UnityData 'DotNetSdk/sdk') -Directory |
    Sort-Object { [version]$_.Name } -Descending | Select-Object -First 1
$compiler = Join-Path $sdk.FullName 'Roslyn/bincore/csc.dll'
$dotnet = Join-Path $UnityData 'DotNetSdk/dotnet.exe'
$output = Join-Path $repoRoot 'results/validation/ar_offline_compile'
New-Item -ItemType Directory -Force -Path $output | Out-Null
$base = @(Get-Content -LiteralPath $response.FullName)
$runtime = @($base | Where-Object { $_ -notmatch '^-(out|refout):' })
$runtime += '-out:"' + (Join-Path $output 'Assembly-CSharp.dll') + '"'
foreach ($folder in @('Assets/Scripts/P1L6AR','Assets/AR')) {
    foreach ($file in Get-ChildItem -LiteralPath (Join-Path $projectRoot $folder) -Filter '*.cs') {
        $relative = $file.FullName.Substring($projectRoot.Length+1).Replace('\','/')
        $quoted = '"' + $relative + '"'
        if (-not ($base | Where-Object { $_.Replace('\','/') -eq $quoted })) { $runtime += $quoted }
    }
}
$runtimeRsp = Join-Path $output 'Runtime.rsp'
$runtime | Set-Content -LiteralPath $runtimeRsp
Push-Location $projectRoot
try {
    & $dotnet exec $compiler ('@'+$runtimeRsp) 2>&1 | Tee-Object -FilePath (Join-Path $output 'Runtime.log')
    if ($LASTEXITCODE -ne 0) { throw 'Cached-reference runtime compilation failed.' }
    $checks = @($base | Where-Object { $_ -notmatch '^-(out|refout):' -and $_ -notmatch '^".*\.cs"$' })
    $checks += '-out:"' + (Join-Path $output 'ARChecks.dll') + '"'
    $checks += '-r:"' + (Join-Path $output 'Assembly-CSharp.dll') + '"'
    foreach ($folder in @('ARScale','ARSurfacePlacement','ARFreePlacement','AROverlay3D','ARDiagrams')) {
        foreach ($file in Get-ChildItem -LiteralPath (Join-Path $projectRoot "Tests/$folder") -Filter '*.cs') {
            if ($file.Name -eq 'OfflineMetricChecks.cs') { continue }
            $checks += '"' + $file.FullName + '"'
        }
    }
    $checksRsp = Join-Path $output 'Checks.rsp'
    $checks | Set-Content -LiteralPath $checksRsp
    & $dotnet exec $compiler ('@'+$checksRsp) 2>&1 | Tee-Object -FilePath (Join-Path $output 'Checks.log')
    if ($LASTEXITCODE -ne 0) { throw 'Cached-reference AR test compilation failed.' }
    $refPack = Get-ChildItem -LiteralPath (Join-Path $UnityData 'DotNetSdk/packs/Microsoft.NETCore.App.Ref') -Directory |
        Sort-Object { [version]$_.Name } -Descending | Select-Object -First 1
    $referenceDirectory = Get-ChildItem -LiteralPath (Join-Path $refPack.FullName 'ref') -Directory | Select-Object -First 1
    $unityCore = Join-Path $UnityData 'Managed/UnityEngine/UnityEngine.CoreModule.dll'
    $metrics = @('-nologo','-target:exe')
    $metrics += '-out:"'+(Join-Path $output 'OfflineMetricChecks.dll')+'"'
    foreach ($reference in Get-ChildItem -LiteralPath $referenceDirectory.FullName -Filter '*.dll') {
        $metrics += '-r:"'+$reference.FullName+'"'
    }
    $metrics += '-r:"'+(Join-Path $output 'Assembly-CSharp.dll')+'"'
    $metrics += '-r:"'+$unityCore+'"'
    $metrics += '"'+(Join-Path $projectRoot 'Tests/ARScale/OfflineMetricChecks.cs')+'"'
    $metricsRsp = Join-Path $output 'Metrics.rsp'
    $metrics | Set-Content -LiteralPath $metricsRsp
    & $dotnet exec $compiler ('@'+$metricsRsp)
    if ($LASTEXITCODE -ne 0) { throw 'Offline metric compilation failed.' }
    Copy-Item -LiteralPath $unityCore -Destination $output -Force
    Copy-Item -LiteralPath (Join-Path $UnityData 'Managed/UnityEngine/UnityEngine.dll') -Destination $output -Force
    @{runtimeOptions=@{tfm=$referenceDirectory.Name;framework=@{name='Microsoft.NETCore.App';version=$refPack.Name}}} |
        ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $output 'OfflineMetricChecks.runtimeconfig.json')
    & $dotnet (Join-Path $output 'OfflineMetricChecks.dll') (Join-Path $projectRoot 'Assets/StreamingAssets/p1l6_current_ar_elements.json') 2>&1 |
        Tee-Object -FilePath (Join-Path $output 'Metrics.log')
    if ($LASTEXITCODE -ne 0) { throw 'Offline dimension/factor checks failed.' }
    Write-Output 'PASS_WITH_NOTE: cached compilation and managed dimension/factor checks; Play NOT VERIFIED.'
} finally { Pop-Location }
