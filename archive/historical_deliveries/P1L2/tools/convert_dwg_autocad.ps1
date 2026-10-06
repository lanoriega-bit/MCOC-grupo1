param(
    [Parameter(Mandatory = $true)]
    [string]$SourceDirectory,
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory
)

$ErrorActionPreference = 'Stop'
$autoCad = 'C:\Program Files\Autodesk\AutoCAD 2026\accoreconsole.exe'
$script = Join-Path $PSScriptRoot 'autocad_export_dxf.scr'

if (-not (Test-Path -LiteralPath $autoCad)) {
    throw "No se encontro AutoCAD Core Console: $autoCad"
}
if (-not (Test-Path -LiteralPath $script)) {
    throw "No se encontro el script de exportacion: $script"
}

$source = (Resolve-Path -LiteralPath $SourceDirectory).Path
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$output = (Resolve-Path -LiteralPath $OutputDirectory).Path
$env:MCOC_DXF_OUT = $output.Replace('\', '/')

$drawings = Get-ChildItem -LiteralPath $source -Recurse -File -Filter '*.dwg' | Sort-Object FullName
$failures = @()

foreach ($drawing in $drawings) {
    Write-Host "[$($drawing.Name)] DWG -> DXF"
    & $autoCad /i $drawing.FullName /s $script | Out-Null
    $expected = Join-Path $output ($drawing.BaseName + '.dxf')
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $expected)) {
        $failures += $drawing.FullName
    }
}

if ($failures.Count -gt 0) {
    throw "Fallaron $($failures.Count) conversiones: $($failures -join '; ')"
}

Write-Host "Conversion completa: $($drawings.Count) DXF en $output"
