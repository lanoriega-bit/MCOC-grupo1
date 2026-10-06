param([string]$UnityData='C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Data')
$ErrorActionPreference='Stop'
$projectRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$output=Join-Path $PSScriptRoot 'Compile'
$dotnet=Join-Path $UnityData 'DotNetSdk/dotnet.exe'
$compiler=Join-Path $UnityData 'DotNetSdk/sdk/8.0.318/Roslyn/bincore/csc.dll'
$references=Join-Path $UnityData 'DotNetSdk/packs/Microsoft.NETCore.App.Ref/8.0.21/ref/net8.0'
$unityCore=Join-Path $UnityData 'Managed/UnityEngine/UnityEngine.CoreModule.dll'
$argsList=@('-nologo','-target:exe')
$argsList+='-out:"'+(Join-Path $output 'OfflineMetricChecks.dll')+'"'
foreach($file in Get-ChildItem $references -Filter *.dll){$argsList+='-r:"'+$file.FullName+'"'}
$argsList+='-r:"'+(Join-Path $output 'Assembly-CSharp.dll')+'"'
$argsList+='-r:"'+$unityCore+'"'
$argsList+='"'+(Join-Path $PSScriptRoot 'OfflineMetricChecks.cs')+'"'
$rsp=Join-Path $output 'Metrics.rsp';$argsList|Set-Content $rsp
& $dotnet exec $compiler ('@'+$rsp)
if($LASTEXITCODE -ne 0){throw 'Managed metric checks compilation failed'}
Copy-Item $unityCore $output -Force
Copy-Item (Join-Path $UnityData 'Managed/UnityEngine/UnityEngine.dll') $output -Force
'{"runtimeOptions":{"tfm":"net8.0","framework":{"name":"Microsoft.NETCore.App","version":"8.0.21"}}}'|Set-Content (Join-Path $output 'OfflineMetricChecks.runtimeconfig.json')
& $dotnet (Join-Path $output 'OfflineMetricChecks.dll') (Join-Path $projectRoot 'Assets/StreamingAssets/p1l6_current_ar_elements.json') 2>&1|Tee-Object (Join-Path $PSScriptRoot 'OfflineMetricChecks.log')
if($LASTEXITCODE -ne 0){throw 'Managed metric checks failed'}
