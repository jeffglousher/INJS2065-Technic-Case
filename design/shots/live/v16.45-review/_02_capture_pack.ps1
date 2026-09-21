# Thunder: opaque view pack after Complete (PrintWindow).
# machineId 4e34e74d-0868-455b-8851-4b5e7ceff85d
$ErrorActionPreference = 'Stop'
$outDir = 'C:\Users\jeffg\dev\INJS2065-Technic-Case\design\shots\live\v16.45-review'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$log = Join-Path $outDir '_capture.log'
function Write-Log([string]$m) {
  $line = "$(Get-Date -Format o) $m"
  Add-Content -Path $log -Value $line
  Write-Output $line
}
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinC {
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left,Top,Right,Bottom; }
}
"@
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

function Get-CadProc {
  Get-Process | Where-Object {
    $_.ProcessName -match 'noBS-CAD|nbcad' -and $_.MainWindowHandle -ne [IntPtr]::Zero
  } | Sort-Object StartTime -Descending | Select-Object -First 1
}
function Save-PW([IntPtr]$hwnd, [string]$path) {
  Start-Sleep -Milliseconds 300
  $rect = New-Object WinC+RECT
  [void][WinC]::GetWindowRect($hwnd, [ref]$rect)
  $w = [Math]::Max(100, $rect.Right - $rect.Left)
  $h = [Math]::Max(100, $rect.Bottom - $rect.Top)
  $bmp = New-Object System.Drawing.Bitmap $w, $h
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $hdc = $g.GetHdc()
  $ok = [WinC]::PrintWindow($hwnd, $hdc, 2)
  $g.ReleaseHdc($hdc); $g.Dispose()
  if (-not $ok) { throw "PrintWindow failed $path" }
  $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose()
  Write-Log "SAVED $path size=$((Get-Item $path).Length)"
}
function Find-Name($root, [string]$name) {
  $cond = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::NameProperty, $name)
  return $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
}
function Invoke-Name($root, [string]$name) {
  $el = Find-Name $root $name
  if (-not $el) { Write-Log "MISSING $name"; return $false }
  try {
    $inv = $el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    $inv.Invoke(); Write-Log "INVOKED $name"; return $true
  } catch {
    Write-Log "INVOKE_FAIL $name $($_.Exception.Message)"; return $false
  }
}
function Invoke-Any($root, [string[]]$names) {
  foreach ($n in $names) { if (Invoke-Name $root $n) { return $true } }
  return $false
}

$p = Get-CadProc
if (-not $p) { throw 'noBS-CAD missing' }
$procId = $p.Id
$hp = Get-Process -Id $procId
[void][WinC]::ShowWindow($hp.MainWindowHandle, 3)
[void][WinC]::SetForegroundWindow($hp.MainWindowHandle)
Start-Sleep -Milliseconds 400
$root = [System.Windows.Automation.AutomationElement]::FromHandle($hp.MainWindowHandle)
Invoke-Any $root @('Shaded','Opaque','Solid','Shaded with edges') | Out-Null

function Shot([string[]]$views, [string]$stem) {
  $hp = Get-Process -Id $procId
  $root = [System.Windows.Automation.AutomationElement]::FromHandle($hp.MainWindowHandle)
  [void][WinC]::SetForegroundWindow($hp.MainWindowHandle)
  Invoke-Any $root $views | Out-Null
  Start-Sleep -Milliseconds 200
  Invoke-Any $root @('Fit','Fit All','Zoom Fit','Zoom to Fit') | Out-Null
  Start-Sleep -Milliseconds 450
  Save-PW $hp.MainWindowHandle (Join-Path $outDir "$stem.png")
}

Shot @('Front','View Front') '11-front'
Shot @('Back','View Back') '12-back'
Shot @('Left','View Left') '13-left'
Shot @('Right','View Right') '14-right'
Shot @('Top','View Top') '15-top'
Shot @('Bottom','View Bottom') '16-bottom'
Shot @('Isometric','Iso','Home') '17-iso'

# Section Analysis optional
$hp = Get-Process -Id $procId
$root = [System.Windows.Automation.AutomationElement]::FromHandle($hp.MainWindowHandle)
if (Invoke-Any $root @('Section Analysis','Section')) {
  Start-Sleep -Seconds 1
  Save-PW $hp.MainWindowHandle (Join-Path $outDir '18-section.png')
  Invoke-Any $root @('Section Analysis','Close') | Out-Null
  Write-Log 'SECTION_OK'
} else {
  'Section Analysis UIA not found — skipped' | Set-Content (Join-Path $outDir '18-section.SKIPPED.txt')
  Write-Log 'SECTION_SKIPPED'
}

function ClipShot([string]$side, [string]$stem) {
  $hp = Get-Process -Id $procId
  $root = [System.Windows.Automation.AutomationElement]::FromHandle($hp.MainWindowHandle)
  Invoke-Any $root @($side, "View $side") | Out-Null
  Invoke-Any $root @('Fit','Fit All') | Out-Null
  Start-Sleep -Milliseconds 300
  $rect = New-Object WinC+RECT
  [void][WinC]::GetWindowRect($hp.MainWindowHandle, [ref]$rect)
  $cx = [int](($rect.Left + $rect.Right)/2)
  $cy = [int](($rect.Top + $rect.Bottom)/2 + 40)
  if ($side -eq 'Right') { $cx = [int]($rect.Left + ($rect.Right-$rect.Left)*0.62) }
  if ($side -eq 'Left')  { $cx = [int]($rect.Left + ($rect.Right-$rect.Left)*0.38) }
  [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($cx, $cy)
  for ($i=0; $i -lt 8; $i++) {
    [System.Windows.Forms.SendKeys]::SendWait('^{ADD}')
    Start-Sleep -Milliseconds 80
  }
  Start-Sleep -Milliseconds 400
  Save-PW $hp.MainWindowHandle (Join-Path $outDir "$stem.png")
  Invoke-Any $root @('Fit','Fit All') | Out-Null
}

ClipShot 'Right' '19-right-clip'
ClipShot 'Left' '20-left-clip'

Write-Log 'CAPTURE_PACK_DONE'
Get-ChildItem $outDir -Filter '*.png' | ForEach-Object {
  Write-Log ("PNG {0} {1}" -f $_.Name, $_.Length)
}
