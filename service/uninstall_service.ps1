# Removes a Sage exporter service. Run as Administrator.
param(
    [string]$ServiceName = "SageExporter",
    [string]$NssmExe     = "nssm.exe"
)

$ErrorActionPreference = "Stop"
$NssmPath = (Get-Command $NssmExe).Source

Write-Host "Stopping $ServiceName..."
& $NssmPath stop   $ServiceName confirm 2>&1 | Out-Null

Write-Host "Removing $ServiceName..."
& $NssmPath remove $ServiceName confirm

Write-Host "Done."
