# ============================================================================
# install_service.ps1
#
# Wraps a Sage exporter project as a Windows service via NSSM.
#
# REQUIREMENTS (do these once on the server):
#   1. Install 32-bit Python 3.11 (e.g. C:\Python311-32\python.exe).
#      The Sage Pervasive ODBC driver is 32-bit only.
#   2. Download nssm.exe and put it on PATH (https://nssm.cc/download).
#   3. Verify the 32-bit ODBC DSN exists:
#        C:\Windows\SysWOW64\odbcad32.exe -> System DSN tab.
#   4. Create instance\sage_credentials.ini with UID= and PWD= lines.
#
# RUN AS ADMINISTRATOR.
# ============================================================================

param(
    [string]$ServiceName = "SageExporter",
    [string]$PythonExe   = "C:\Python311-32\python.exe",
    [string]$NssmExe     = "nssm.exe",
    [string]$ProjectRoot = $PSScriptRoot,
    [string]$Entrypoint  = "$PSScriptRoot\run_service.py"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Installing $ServiceName ==="
Write-Host "Project root: $ProjectRoot"
Write-Host "Python exe:   $PythonExe"
Write-Host "Entrypoint:   $Entrypoint"

if (-not (Test-Path $PythonExe)) {
    throw "Python not found at $PythonExe. Install 32-bit Python first."
}
if (-not (Test-Path $Entrypoint)) {
    throw "Entrypoint not found at $Entrypoint."
}

try {
    $NssmPath = (Get-Command $NssmExe -ErrorAction Stop).Source
} catch {
    throw "nssm.exe not found on PATH. Download from https://nssm.cc/download"
}
Write-Host "NSSM:         $NssmPath"

Write-Host ""
Write-Host "Installing Python dependencies..."
& $PythonExe -m pip install --upgrade pip
& $PythonExe -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }

# Stop & remove any existing service of the same name (idempotent).
# nssm writes "Can't open service!" to stderr when the service doesn't
# exist; that's fine, we just want to make sure no stale install is
# present. Suppress stderr and check the exit code without letting
# PowerShell treat native stderr as a terminating error.
$prevEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& $NssmPath status $ServiceName 2>&1 | Out-Null
$existed = ($LASTEXITCODE -eq 0)
if ($existed) {
    Write-Host "Existing service found - stopping & removing..."
    & $NssmPath stop   $ServiceName confirm 2>&1 | Out-Null
    & $NssmPath remove $ServiceName confirm 2>&1 | Out-Null
}
$ErrorActionPreference = $prevEAP

$logDir = Join-Path $ProjectRoot "instance\logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

Write-Host ""
Write-Host "Installing service..."
# Install with just the executable; set AppParameters separately so we
# can quote the script path properly. NSSM otherwise stores it
# unquoted, and any space in the project path breaks it.
& $NssmPath install $ServiceName $PythonExe
& $NssmPath set $ServiceName AppParameters "`"$Entrypoint`""
& $NssmPath set $ServiceName AppDirectory $ProjectRoot

# Auto-start on boot, restart after crash with throttling
& $NssmPath set $ServiceName Start SERVICE_AUTO_START
& $NssmPath set $ServiceName AppExit Default Restart
& $NssmPath set $ServiceName AppRestartDelay 5000
& $NssmPath set $ServiceName AppThrottle 10000

# Stdout/stderr -> rotating log files (5 MB cap)
& $NssmPath set $ServiceName AppStdout (Join-Path $logDir "stdout.log")
& $NssmPath set $ServiceName AppStderr (Join-Path $logDir "stderr.log")
& $NssmPath set $ServiceName AppRotateFiles 1
& $NssmPath set $ServiceName AppRotateOnline 1
& $NssmPath set $ServiceName AppRotateBytes 5242880

Write-Host ""
Write-Host "Starting service..."
& $NssmPath start $ServiceName
Start-Sleep -Seconds 2
& $NssmPath status $ServiceName

Write-Host ""
Write-Host "=== Done ==="
Write-Host "Logs: $logDir"
Write-Host "Manage: nssm edit $ServiceName  |  nssm restart $ServiceName"
