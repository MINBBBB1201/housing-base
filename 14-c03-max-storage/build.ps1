param([string]$OpenScad = 'C:\Program Files\OpenSCAD\openscad.com')

$ErrorActionPreference = 'Stop'
$partDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $partDir 'base_cover.scad'
$flags = @(
    '-D', 'clips_list=[]',
    '-D', 'lid_fix="screw"',
    '-D', 'lid_gap=0.6',
    '-D', 'b12_external=false',
    '-D', 'side_cable_slot=[35,75,12]'
)

foreach ($part in @('base', 'lid')) {
    $name = if ($part -eq 'base') { 'PLA_max_storage_body.stl' } else { 'PLA_max_storage_lid.stl' }
    $out = Join-Path $partDir $name
    & $OpenScad --export-format binstl -o $out @flags '-D' "export_component=`"$part`"" $source
    if ($LASTEXITCODE -ne 0) { throw "OpenSCAD failed: $part" }
    Write-Output $out
}
