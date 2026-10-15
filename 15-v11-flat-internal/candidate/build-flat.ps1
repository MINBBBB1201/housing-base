param([string]$OpenScad = 'C:\Program Files\OpenSCAD\openscad.com')

$ErrorActionPreference = 'Stop'
$partDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $partDir 'base_cover_source.scad'
foreach ($part in @('body','lid')) {
    $name = if ($part -eq 'body') { 'RAW_NONMANIFOLD_v11_body.stl' } else { 'DRAFT_v11_internal_lid.stl' }
    $output = Join-Path $partDir $name
    & $OpenScad --export-format binstl -o $output '-D' ("export_component=`"{0}`"" -f $part) $source
    if ($LASTEXITCODE -ne 0) { throw "OpenSCAD failed for $part" }
    Write-Output $output
}
& python (Join-Path $partDir 'repair_export.py')
if ($LASTEXITCODE -ne 0) { throw 'Mesh regularization failed' }
& python (Join-Path $partDir 'audit_mesh.py')
if ($LASTEXITCODE -ne 0) { throw 'Mesh audit failed' }
