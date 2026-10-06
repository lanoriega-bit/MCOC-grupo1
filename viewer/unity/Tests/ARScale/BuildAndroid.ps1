param([string]$UnityEditor='C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe')
$ErrorActionPreference='Stop'
$projectRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$checkRoot=Join-Path $projectRoot '.scale-android-check'
New-Item -ItemType Directory -Force $checkRoot|Out-Null
foreach($folder in @('Assets','Packages','ProjectSettings')){Copy-Item (Join-Path $projectRoot $folder) $checkRoot -Recurse -Force}
# Remove only the copy's automatic Main.unity opener, preserving the real file.
Remove-Item -LiteralPath (Join-Path $checkRoot 'Assets/Editor/AutoOpenScene.cs') -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $checkRoot 'Assets/Editor/AutoOpenScene.cs.meta') -ErrorAction SilentlyContinue
Copy-Item (Join-Path $PSScriptRoot 'AndroidScaleBuild.cs') (Join-Path $checkRoot 'Assets/Editor') -Force
# Reuse installed packages without changing the user's package configuration.
$manifest=Get-Content (Join-Path $checkRoot 'Packages/manifest.json') -Raw|ConvertFrom-Json
foreach($package in Get-ChildItem (Join-Path $projectRoot 'Library/PackageCache') -Directory){
    $packageJson=Join-Path $package.FullName 'package.json'
    if(!(Test-Path $packageJson)){continue}
    $name=(Get-Content $packageJson -Raw|ConvertFrom-Json).name
    if($name.StartsWith('com.unity.modules.')){continue}
    $manifest.dependencies|Add-Member -NotePropertyName $name -NotePropertyValue ('file:'+$package.FullName.Replace('\','/')) -Force
}
$manifest|ConvertTo-Json -Depth 6|Set-Content (Join-Path $checkRoot 'Packages/manifest.json')
$log=Join-Path $checkRoot 'android-build.log'
$argsList=@('-batchmode','-nographics','-buildTarget','Android','-projectPath',('"'+$checkRoot+'"'),'-executeMethod','AndroidScaleBuild.Run','-logFile',('"'+$log+'"'))
$process=Start-Process -FilePath $UnityEditor -ArgumentList $argsList -WindowStyle Hidden -PassThru -Wait
Copy-Item $log (Join-Path $PSScriptRoot 'AndroidBuild.log') -Force
if($process.ExitCode -ne 0 -or !(Select-String -LiteralPath $log -Pattern 'ANDROID_SCALE_BUILD_PASSED' -SimpleMatch -Quiet)){throw 'Android scale validation build did not pass'}
$destination=Join-Path $projectRoot ('BuildsAndroid/AR_Scales_2026-10-05_'+(Get-Date -Format 'HHmmss')+'.apk')
if(Test-Path $destination){throw 'Refusing to overwrite an APK'}
Copy-Item (Join-Path $checkRoot 'ARScaleValidation.apk') $destination
Write-Output ('ANDROID_SCALE_BUILD_PASSED: '+$destination)
