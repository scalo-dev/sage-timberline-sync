# 04 - Deploying as a Windows Service

Three deployment options, ranked by complexity:

1. **Task Scheduler** - simplest, fine for "run once a night"
2. **NSSM service** - best balance for "run on a schedule, survive reboots"
3. **NSSM service hosting Flask + APScheduler** - if you also have a UI

## Option 1: Task Scheduler

Create a Basic Task:

| Field | Value |
|---|---|
| Trigger | Daily at 2 AM |
| Action | Start a program |
| Program | `C:\Python311-32\python.exe` |
| Arguments | `-m app.exporter` |
| Start in | `C:\Path\To\Your\Project` |

Run as a service account that has both Sage permission and write
permission to your output folder. Task Scheduler will not survive
the script crashing mid-run gracefully, so use it for short cron-style
exports rather than long-running processes.

## Option 2: NSSM service

Use the files in `service/` of this guide. Drop `run_service.py`,
`install_service.ps1`, and `uninstall_service.ps1` into your project
root, then:

```powershell
# As Administrator:
.\install_service.ps1
```

The defaults install a service named `SageExporter`, set it to start
at boot, restart-on-crash with a 5-second delay, and pipe stdout/stderr
to rotating log files in `instance\logs\`.

Override the defaults:
```powershell
.\install_service.ps1 `
    -ServiceName "SageJobExporter" `
    -PythonExe "C:\Python311-32\python.exe" `
    -Entrypoint "C:\Projects\jobs\run_service.py"
```

### Crucial detail: paths with spaces

If your project is at `C:\Job List Service\`, NSSM needs the script
path quoted. The shipped `install_service.ps1` does this correctly by
calling `nssm install` with **just** the Python exe, then setting
`AppParameters` separately with embedded quotes:

```powershell
& nssm install $ServiceName $PythonExe
& nssm set $ServiceName AppParameters "`"$Entrypoint`""
```

If you ever see a service entering `SERVICE_PAUSED` immediately after
install with logs like `can't open file 'C:\Job'`, this is the cause.

### Day-2 management

```powershell
nssm status   SageExporter
nssm restart  SageExporter
nssm stop     SageExporter
nssm edit     SageExporter   # GUI editor for changing settings
```

Logs: `instance\logs\stdout.log`, `stderr.log`, `service.log` (your
Python logger), `exporter.log` (your exporter logger).

### The service account

By default NSSM runs services as `LocalSystem`. Sage usually doesn't
care - LocalSystem can authenticate to the local Pervasive driver fine
- but writing to a network share (`\\pitsrv09\swap\...`) often fails
because LocalSystem has no network identity.

Two fixes:
- Run the service as a domain account (in `nssm edit -> Log on` tab)
  that has read on Sage and write on the share. This is the standard
  fix.
- OR change the output to a local path and copy from there with a
  separate scheduled task.

## Option 3: NSSM hosting Flask + APScheduler

Same install pattern, but `run_service.py` starts a Waitress server
serving a Flask app, with APScheduler triggering the export on a
schedule inside the same process. See `docs/05-add-flask-ui.md`.

## Verifying

After install, give it ~30 seconds and then check:

```powershell
nssm status SageExporter            # should print SERVICE_RUNNING
Get-Content instance\logs\service.log -Tail 30
Get-Content instance\logs\stderr.log -Tail 30
```

If `stderr.log` is non-empty, your Python script is crashing - see
[`06-troubleshooting.md`](06-troubleshooting.md).

---
Next: [`05-add-flask-ui.md`](05-add-flask-ui.md)
