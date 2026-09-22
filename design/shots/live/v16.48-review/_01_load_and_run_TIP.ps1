# Explicit TIP runner (same as _01_load_and_run.ps1 with no -Explode).
$ErrorActionPreference = 'Stop'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
& "$dir\_01_load_and_run.ps1"
