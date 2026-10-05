param([string]$UnityData='C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Data')
$ErrorActionPreference='Stop'
$projectRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$output=Join-Path $PSScriptRoot 'Compile'
New-Item -ItemType Directory -Force $output|Out-Null
$sourceRsp=Join-Path $projectRoot 'Library/Bee/artifacts/1300b0aE.dag/Assembly-CSharp.rsp'
$compiler=Join-Path $UnityData 'DotNetSdk/sdk/8.0.318/Roslyn/bincore/csc.dll'
$dotnet=Join-Path $UnityData 'DotNetSdk/dotnet.exe'
$base=@(Get-Content -LiteralPath $sourceRsp)
$runtime=@($base|Where-Object {$_ -notmatch '^-(out|refout):'})
$runtime+='-out:"'+(Join-Path $output 'Assembly-CSharp.dll')+'"'
$runtime+='"Assets/Scripts/P1L6AR/ARGeometryScale.cs"'
$rsp=Join-Path $output 'Runtime.rsp';$runtime|Set-Content $rsp
Push-Location $projectRoot
try {
    & $dotnet exec $compiler ('@'+$rsp) 2>&1|Tee-Object (Join-Path $output 'Runtime.log')
    if($LASTEXITCODE -ne 0){throw 'Runtime compilation failed'}
    $checks=@($base|Where-Object {$_ -notmatch '^-(out|refout):' -and $_ -notmatch '^".*\.cs"$'})
    $checks+='-out:"'+(Join-Path $output 'ScaleTests.dll')+'"'
    $checks+='-r:"'+(Join-Path $output 'Assembly-CSharp.dll')+'"'
    foreach($file in @('Tests/ARScale/ScaleChecks.cs','Tests/ARScale/ScaleBoot.cs','Tests/ARScale/AndroidScaleBuild.cs','Tests/ARScale/ValidatedAutoPlacementMath.cs',
        'Tests/ARSurfacePlacement/SurfaceChecks.cs','Tests/ARFreePlacement/FreePlacementChecks.cs',
        'Tests/AROverlay3D/OverlayChecks.cs','Tests/AROverlay3D/ValidatedBeamDiagram3DRenderer.cs','Tests/ARDiagrams/ARDiagramChecks.cs')) {$checks+='"'+$file+'"'}
    $rsp=Join-Path $output 'Tests.rsp';$checks|Set-Content $rsp
    & $dotnet exec $compiler ('@'+$rsp) 2>&1|Tee-Object (Join-Path $output 'Tests.log')
    if($LASTEXITCODE -ne 0){throw 'Test scripts compilation failed'}
    Write-Output 'SCALE_SCRIPTS_COMPILE_PASSED (Unity Roslyn and cached project references; execution requires licensed Unity Editor)'
} finally {Pop-Location}
