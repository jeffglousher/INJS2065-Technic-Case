# Thunder: exit sketch/edit, expand Load-from-path, load TIP (default), run, require Complete N/N (N>=1000).
# Fail-fast on "Playback stopped" / "Finish the current edit".
# machineId 4e34e74d-0868-455b-8851-4b5e7ceff85d
param(
  [switch]$Explode,
  [string]$ScriptPath = ''
)
$ErrorActionPreference = 'Stop'
$repo = 'C:\Users\jeffg\dev\INJS2065-Technic-Case'
$tipPath = Join-Path $repo 'design\design_v16_48.nbcad.jsonc'
$explodePath = Join-Path $repo 'design\design_v16_48.nbcad.jsonc'
if (-not $ScriptPath) {
  if ($Explode) { $ScriptPath = $explodePath } else { $ScriptPath = $tipPath }
}
$outDir = Join-Path $repo 'design\shots\live\v16.48-review'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$log = Join-Path $outDir '_load_run.log'
function Write-Log([string]$m) {
  $line = "$(Get-Date -Format o) $m"
  Add-Content -Path $log -Value $line
  Write-Host $line
}
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinL45b {
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left,Top,Right,Bottom; }
  public const byte VK_ESCAPE = 0x1B;
  public const uint KEYEVENTF_KEYUP = 0x0002;
  public static void TapEscape() {
    keybd_event(VK_ESCAPE, 0, 0, UIntPtr.Zero);
    keybd_event(VK_ESCAPE, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
  }
}
"@
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing

function Get-CadProc {
  Get-Process | Where-Object {
    $_.ProcessName -match 'noBS-CAD|nbcad' -and $_.MainWindowHandle -ne [IntPtr]::Zero
  } | Sort-Object StartTime -Descending | Select-Object -First 1
}
function Save-PW([IntPtr]$hwnd, [string]$path) {
  $rect = New-Object WinL45b+RECT
  [void][WinL45b]::GetWindowRect($hwnd, [ref]$rect)
  $w = [Math]::Max(100, $rect.Right - $rect.Left)
  $h = [Math]::Max(100, $rect.Bottom - $rect.Top)
  $bmp = New-Object System.Drawing.Bitmap $w, $h
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $hdc = $g.GetHdc()
  $ok = [WinL45b]::PrintWindow($hwnd, $hdc, 2)
  $g.ReleaseHdc($hdc); $g.Dispose()
  if (-not $ok) { throw "PrintWindow failed $path" }
  $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose()
  Write-Log "SAVED $path size=$((Get-Item $path).Length)"
}
function Find-ByName($root, [string]$name) {
  $cond = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::NameProperty, $name)
  return $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
}
function Invoke-ByName($root, [string]$name) {
  $el = Find-ByName $root $name
  if (-not $el) { Write-Log "MISSING invoke:$name"; return $false }
  try {
    $inv = $el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    $inv.Invoke()
    Write-Log "INVOKED $name"
    return $true
  } catch {
    Write-Log "INVOKE_FAIL $name : $_"
    return $false
  }
}
function Set-ByName($root, [string]$name, [string]$value) {
  $el = Find-ByName $root $name
  if (-not $el) { Write-Log "MISSING value:$name"; return $false }
  $vp = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
  $vp.SetValue($value)
  Write-Log "SET $name"
  return $true
}
function Get-StatusHits($root) {
  $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
  $stack = New-Object System.Collections.Generic.Stack[object]
  $stack.Push($root)
  $hits = New-Object System.Collections.Generic.List[string]
  $n = 0
  while ($stack.Count -gt 0 -and $n -lt 6000) {
    $n++
    $cur = $stack.Pop()
    try {
      $nm = $cur.Current.Name
      if ($nm -and ($nm -match 'Complete|Running|stopped|Stop script|Finish the current|FINISH SKETCH|Finish Sketch|Finish the current edit|\d{3,4}\s*/\s*\d{3,4}|Walkthrough|Playback|Model walkthrough')) {
        $hits.Add($nm)
      }
    } catch {}
    try {
      $ch = $walker.GetFirstChild($cur)
      while ($ch) { $stack.Push($ch); $ch = $walker.GetNextSibling($ch) }
    } catch {}
  }
  return $hits
}
function Exit-EditMode([IntPtr]$hwnd) {
  Write-Log 'Exit-EditMode'
  $root = [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
  foreach ($nm in @('FINISH SKETCH','Finish Sketch','Finish sketch')) {
    [void](Invoke-ByName $root $nm)
    Start-Sleep -Milliseconds 200
  }
  [void][WinL45b]::SetForegroundWindow($hwnd)
  Start-Sleep -Milliseconds 150
  1..4 | ForEach-Object {
    [WinL45b]::TapEscape()
    Start-Sleep -Milliseconds 200
  }
  Start-Sleep -Milliseconds 300
  return [System.Windows.Automation.AutomationElement]::FromHandle($hwnd)
}
function Expand-LoadFromPath($root) {
  foreach ($nm in @('Load from a file path','Load from file path','From file path','Load from a file path ')) {
    $el = Find-ByName $root $nm
    if (-not $el) { continue }
    try {
      $expand = $el.GetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern)
      $st = $expand.Current.ExpandCollapseState
      Write-Log "EXPAND_STATE '$nm'=$st"
      if ($st -ne [System.Windows.Automation.ExpandCollapseState]::Expanded) {
        $expand.Expand()
        Write-Log "EXPANDED $nm"
        Start-Sleep -Milliseconds 500
      }
      return $true
    } catch {
      try {
        $inv = $el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
        $inv.Invoke(); Write-Log "INVOKED_EXPAND $nm"; Start-Sleep -Milliseconds 500; return $true
      } catch { Write-Log "EXPAND_FAIL $nm : $_" }
    }
  }
  Write-Log 'WARN: Load-from-path expander not found (may already be open)'
  return $false
}

if (-not (Test-Path -LiteralPath $ScriptPath)) { throw "Missing script $ScriptPath" }
Write-Log "SCRIPT=$ScriptPath Explode=$Explode"
$p = Get-CadProc
if (-not $p) { throw 'noBS-CAD MainWindowHandle==0 / not running' }
$procId = $p.Id
Write-Log "CAD pid=$procId hwnd=$($p.MainWindowHandle) title=$($p.MainWindowTitle)"
$hp = Get-Process -Id $procId
[void][WinL45b]::ShowWindow($hp.MainWindowHandle, 3)
[void][WinL45b]::SetForegroundWindow($hp.MainWindowHandle)
Start-Sleep -Milliseconds 500
$root = Exit-EditMode $hp.MainWindowHandle
Save-PW $hp.MainWindowHandle (Join-Path $outDir '00-before.png')

# Guard: refuse to run while mid-edit (same false-fail as upper_pin_4_1_entry_c @426)
$preHits = Get-StatusHits $root
Write-Log ("PRE_EDIT_STATUS " + ($preHits -join ' || '))
$blocked = $false
foreach ($s in $preHits) {
  if ($s -match '(?i)Finish the current edit|Finish the current edit to run this script|FINISH SKETCH') { $blocked = $true }
}
if ($blocked) {
  $root = Exit-EditMode $hp.MainWindowHandle
  $preHits = Get-StatusHits $root
  Write-Log ("PRE_EDIT_STATUS2 " + ($preHits -join ' || '))
  foreach ($s in $preHits) {
    if ($s -match '(?i)Finish the current edit') {
      Save-PW $hp.MainWindowHandle (Join-Path $outDir '00-mid-edit-blocked.png')
      throw "Still mid-edit after Escape/Finish Sketch: $s"
    }
  }
}

[void](Expand-LoadFromPath $root)
$root = [System.Windows.Automation.AutomationElement]::FromHandle($hp.MainWindowHandle)

$setOk = $false
foreach ($lab in @('Script path','File path')) {
  if (Set-ByName $root $lab $ScriptPath) { $setOk = $true; break }
}
if (-not $setOk) { throw 'Script path field not found — expand Load from a file path, then re-run' }
$loaded = $false
foreach ($loadNm in @('Load script','Load')) {
  if (Invoke-ByName $root $loadNm) { $loaded = $true; break }
}
if (-not $loaded) { throw 'Load script button not found' }
Start-Sleep -Seconds 2
Save-PW $hp.MainWindowHandle (Join-Path $outDir '03-after-load.png')

$root = Exit-EditMode $hp.MainWindowHandle
$hitsPre = Get-StatusHits $root
Write-Log ("PRE_RUN_STATUS " + ($hitsPre -join ' || '))
foreach ($s in $hitsPre) {
  if ($s -match '(?i)Finish the current edit') {
    Save-PW $hp.MainWindowHandle (Join-Path $outDir '03-blocked-mid-edit.png')
    throw "UI blocked before Run: $s"
  }
}

$ran = $false
foreach ($runNm in @('Run in new design','Run script','Run')) {
  if (Invoke-ByName $root $runNm) { $ran = $true; break }
}
if (-not $ran) { throw 'Run in new design not found' }

$deadline = (Get-Date).AddMinutes(25)
$last = ''
$complete = $false
$completeCount = -1
$completeTotal = -1
do {
  Start-Sleep -Seconds 4
  $hp = Get-Process -Id $procId -ErrorAction SilentlyContinue
  if (-not $hp) { throw 'CAD exited' }
  $root = [System.Windows.Automation.AutomationElement]::FromHandle($hp.MainWindowHandle)
  $hits = Get-StatusHits $root
  $joined = ($hits -join ' || ')
  if ($joined -ne $last) { Write-Log "STATUS $joined"; $last = $joined }
  foreach ($s in $hits) {
    if ($s -match '(?i)Finish the current edit') {
      Save-PW $hp.MainWindowHandle (Join-Path $outDir '05-mid-edit-during-run.png')
      "COMPLETE=False FAIL=$s" | Set-Content (Join-Path $outDir 'COMPLETE.txt')
      throw "FALSE_FAIL mid-edit during run: $s"
    }
    if ($s -match '(?i)Playback stopped|Walkthrough Stopped|Model walkthrough Stopped|Model walkthrough Stopped:|stopped at|Playback stopped\.') {
      Save-PW $hp.MainWindowHandle (Join-Path $outDir '05-playback-stopped.png')
      "COMPLETE=False FAIL=$s" | Set-Content (Join-Path $outDir 'COMPLETE.txt')
      throw "FAIL_FAST Playback stopped: $s"
    }
    if ($s -match '(?i)Stopped:\s*\d+\s*/\s*\d+' -and $s -notmatch '(?i)Complete') {
      Save-PW $hp.MainWindowHandle (Join-Path $outDir '05-playback-stopped.png')
      "COMPLETE=False FAIL=$s" | Set-Content (Join-Path $outDir 'COMPLETE.txt')
      throw "FAIL_FAST walkthrough Stopped: $s"
    }
    if ($s -match '(?i)Complete.*?(\d{3,4})\s*/\s*(\d{3,4})') {
      $a = [int]$Matches[1]; $b = [int]$Matches[2]
      if ($a -eq $b -and $a -ge 1000) {
        Write-Log "COMPLETE count=$a/$b text=$s"
        $completeCount = $a; $completeTotal = $b; $complete = $true; break
      }
    }
  }
} while (-not $complete -and (Get-Date) -lt $deadline)

if (-not $complete) {
  Save-PW $hp.MainWindowHandle (Join-Path $outDir '05-timeout.png')
  "COMPLETE=False COUNT=$completeCount TOTAL=$completeTotal" | Set-Content (Join-Path $outDir 'COMPLETE.txt')
  throw 'TIMEOUT: did not reach Complete N/N with N>=1000'
}
Save-PW $hp.MainWindowHandle (Join-Path $outDir '05-after-complete.png')
"COMPLETE=$complete COUNT=$completeCount TOTAL=$completeTotal SCRIPT=$ScriptPath" | Set-Content (Join-Path $outDir 'COMPLETE.txt')
Write-Log "DONE complete=$complete count=$completeCount/$completeTotal"
