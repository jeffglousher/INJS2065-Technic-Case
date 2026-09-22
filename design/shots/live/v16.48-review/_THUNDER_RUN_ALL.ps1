$ErrorActionPreference = 'Stop'
$dir = 'C:\Users\jeffg\dev\INJS2065-Technic-Case\design\shots\live\v16.48-review'
# 1) TIP must Complete N/N (N>=1000) before any explode/review shots.
& "$dir\_01_load_and_run_TIP.ps1"
& "$dir\_02_capture_pack.ps1"
Write-Output 'ALL_DONE'
