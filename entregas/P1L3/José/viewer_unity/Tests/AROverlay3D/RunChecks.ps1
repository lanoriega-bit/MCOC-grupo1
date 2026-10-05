param([string]$UnityEditor = 'C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe', [switch]$Visual)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$checkRoot = Join-Path $projectRoot '.overlay-check'
foreach($folder in @('Assets/Editor','Assets/P1L6AR','Assets/Plugins','Assets/StreamingAssets','Packages','ProjectSettings')) {
    New-Item -ItemType Directory -Force (Join-Path $checkRoot $folder) | Out-Null
}
Copy-Item (Join-Path $projectRoot 'Assets/Scripts/P1L6AR/*') (Join-Path $checkRoot 'Assets/P1L6AR') -Recurse -Force
foreach($name in @('LuisARDiagrams','LuisARImageAnchor','LuisARTrackingUI')) {
    Copy-Item (Join-Path $projectRoot "Assets/AR/$name.cs") (Join-Path $checkRoot 'Assets') -Force
}
Copy-Item (Join-Path $projectRoot 'Assets/StreamingAssets/p1l6_current_ar_elements.json') (Join-Path $checkRoot 'Assets/StreamingAssets') -Force
New-Item -ItemType Directory -Force (Join-Path $checkRoot 'Assets/Resources') | Out-Null
Copy-Item (Join-Path $projectRoot 'Assets/Resources/ARForceOverlay.shader*') (Join-Path $checkRoot 'Assets/Resources') -Force
foreach($name in @('ProjectVersion.txt','ProjectSettings.asset')) {
    Copy-Item (Join-Path $projectRoot "ProjectSettings/$name") (Join-Path $checkRoot 'ProjectSettings') -Force
}
foreach($name in @('Unity.XR.ARFoundation','Unity.XR.ARFoundation.InternalUtils','Unity.XR.ARSubsystems','Unity.XR.CoreUtils','Unity.XR.Management','Unity.Mathematics','UnityEngine.SpatialTracking','UnityEngine.XR.LegacyInputHelpers')) {
    Copy-Item (Join-Path $projectRoot "Library/ScriptAssemblies/$name.dll") (Join-Path $checkRoot 'Assets/Plugins') -Force
}
$dependencies = @{}
foreach($package in @('com.unity.ugui','com.unity.inputsystem')) {
    $cached = Get-ChildItem (Join-Path $projectRoot 'Library/PackageCache') -Directory -Filter "$package@*" | Select-Object -First 1
    if(!$cached) { throw "Missing existing package cache: $package" }
    $dependencies[$package] = 'file:' + $cached.FullName.Replace('\','/')
}
foreach($module in @('animation','audio','jsonserialize','ui','xr','unitywebrequest')) { $dependencies["com.unity.modules.$module"]='1.0.0' }
$dependencies['com.unity.modules.imageconversion']='1.0.0'
@{dependencies=$dependencies} | ConvertTo-Json -Depth 3 | Set-Content (Join-Path $checkRoot 'Packages/manifest.json')
Copy-Item (Join-Path $PSScriptRoot 'OverlayChecks.cs') (Join-Path $checkRoot 'Assets') -Force
Copy-Item (Join-Path $PSScriptRoot 'ValidatedBeamDiagram3DRenderer.cs') (Join-Path $checkRoot 'Assets') -Force
Copy-Item (Join-Path $PSScriptRoot 'OverlayBoot.cs') (Join-Path $checkRoot 'Assets/Editor') -Force
Copy-Item (Join-Path $projectRoot 'Tests/ARSurfacePlacement/SurfaceChecks.cs') (Join-Path $checkRoot 'Assets') -Force
$log = Join-Path $checkRoot 'checks.log'
$argsList = @('-batchmode','-nographics','-projectPath',('"'+$checkRoot+'"'),'-executeMethod','OverlayBoot.Run','-logFile',('"'+$log+'"'))
if ($Visual) { $argsList = $argsList | Where-Object { $_ -ne '-nographics' }; $argsList += @('-force-d3d11','-uiScreenshots') }
$process = Start-Process -FilePath $UnityEditor -ArgumentList $argsList -WindowStyle Hidden -PassThru -Wait
Copy-Item -LiteralPath $log -Destination (Join-Path $PSScriptRoot 'UnityChecks.log') -Force
if($process.ExitCode -ne 0 -or !(Select-String -LiteralPath $log -SimpleMatch 'OVERLAY_CHECKS_PASSED' -Quiet)) { throw "Diagram tests failed: $log" }
Write-Output 'OVERLAY_CHECKS_PASSED'



