param(
    [string]$OpenScad = 'C:\Program Files\OpenSCAD\openscad.com'
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $here 'base_cover.scad'
if (-not (Test-Path -LiteralPath $OpenScad)) { throw "OpenSCAD not found: $OpenScad" }

$common = @('-D', 'b12_external=true', '-D', 'side_cable_slot=[35,75,12]')
$jobs = @(
    @{ Name='MJF_B12_external_body.stl'; Flags=@('-D', 'export_component="base"') },
    @{ Name='MJF_B12_external_lid.stl'; Flags=@('-D', 'export_component="lid"') },
    @{ Name='FDM_B12_external_body.stl'; Flags=@('-D', 'export_component="base"', '-D', 'clips_list=[]', '-D', 'lid_fix="screw"', '-D', 'lid_gap=0.6') },
    @{ Name='FDM_B12_external_lid.stl'; Flags=@('-D', 'export_component="lid"', '-D', 'clips_list=[]', '-D', 'lid_fix="screw"', '-D', 'lid_gap=0.6') }
)
foreach ($job in $jobs) {
    $out = Join-Path $here $job.Name
    & $OpenScad -o $out @common @($job.Flags) $source
    if ($LASTEXITCODE -ne 0) { throw "OpenSCAD failed for $($job.Name), exit $LASTEXITCODE" }
    Write-Output $out
}
