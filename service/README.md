# Optional: Run as a Windows Service via NSSM

For exporters that need to run on a schedule and survive reboots,
NSSM (Non-Sucking Service Manager) wraps a Python script as a real
Windows service.

These files assume the project layout from `../template/`. Drop them
into your project root.

## Files

- `run_service.py` - long-running entrypoint NSSM calls
- `install_service.ps1` - one-shot installer (run as Administrator)
- `uninstall_service.ps1` - removes the service

## Quick install

```powershell
# Prerequisites:
#   - 32-bit Python at C:\Python311-32\python.exe
#   - nssm.exe somewhere on PATH (https://nssm.cc/download)
#   - instance\sage_credentials.ini exists with real UID/PWD

cd C:\Path\To\Your\Project
.\install_service.ps1                   # uses defaults
.\install_service.ps1 -ServiceName MyExporter -PythonExe "C:\Python311-32\python.exe"
```

The service auto-starts on boot, auto-restarts after a 5-second delay
if it crashes, and pipes stdout/stderr to rotating log files in
`instance\logs\`.

## Manage

```powershell
nssm status   <ServiceName>
nssm restart  <ServiceName>
nssm edit     <ServiceName>     # GUI editor
```

## Customizing run_service.py

The default entrypoint just runs `app.exporter.run_export()` in a loop
with a sleep between runs. For more sophisticated needs (web server,
APScheduler, multiple jobs), replace the body of `main()`.
