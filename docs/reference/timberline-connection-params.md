# Reference: Timberline ODBC Connection-String Parameters

Every parameter we've encountered in a Sage 300 CRE / Timberline
ODBC connection string, and what it does.

## Required-ish (you'll always set these)

| Param | Example | Notes |
|---|---|---|
| `DSN` | `ISD The Scalo Group of-103285019` | Name from the **32-bit** ODBC manager (`SysWOW64\odbcad32.exe`). Case-sensitive. |
| `UID` | `reportuser` | Sage SQL user, NOT a Windows user. Set up via Sage's "ODBC Security" admin. |
| `PWD` | `s3cr3t` | The corresponding password. |

## The "magic four" - usually required

| Param | Recommended | What happens if wrong/missing |
|---|---|---|
| `DatabaseType` | `1` | Often the difference between Accounting vs Construction data folders. Some installs need `2`. |
| `DBQ` | `\\Server\TIMBERLINE OFFICE\Data\<Company>\` | Explicit data folder path. **Trailing backslash required.** Without this, the DSN's default folder is used, which may be a different company. |
| `DictionaryMode` | `0` | When non-zero, the driver uses Sage's data dictionary to alias columns. Many module tables disappear in dictionary mode. Keep at `0` unless you specifically want aliasing. |
| `StandardMode` | `0` | Toggles "ODBC standard" behavior. With `1`, some Timberline-specific extensions (like joining across data folders) stop working. We've never wanted `1`. |

## Useful extras

| Param | Recommended | Notes |
|---|---|---|
| `ShortenNames` | `0` | If `1`, column and table names are truncated to a shorter length for old apps. Always `0` for Python. |
| `MaxColSupport` | `255` | Maximum columns the driver will return per query. Some Timberline tables genuinely have >250 columns; `255` is the safe ceiling. |
| `BurstMode` | `1` | Performance hint. Default is fine; rarely needed. |
| `CacheSize` | `4096` | Local row cache, in rows. Bigger = faster scans, more memory. |

## Where the canonical "good" values come from

These came from inspecting a working Microsoft Access linked-table
connection string against a production Sage company. See
[`extracting-conn-from-access.md`](extracting-conn-from-access.md).

## How to assemble the string in Python

`template/app/connection.py` does this for you. The output is roughly:

```
DSN=ISD The Scalo Group of-103285019;UID=reportuser;PWD=s3cr3t;DatabaseType=1;DBQ=\\PITSRV08\TIMBERLINE OFFICE\Data\Scalo\;DictionaryMode=0;MaxColSupport=255;ShortenNames=0;StandardMode=0
```

Note the **single semicolons** and the **literal `\\` and `\` in the
DBQ value** (no extra escaping in the string itself - the value the
driver wants is just the raw UNC path).

## What we tried and abandoned

- **A `.mdb` middleman with linked tables**, queried via the Access
  ODBC driver. Works, but adds two extra moving parts (Access driver
  + the .mdb file) for no benefit over going direct.
- **The 64-bit Pervasive driver.** It exists for some Sage versions
  but is unstable in our experience and doesn't ship with the
  standard client install.
- **`Trusted_Connection=Yes`.** Sage SQL auth is its own thing,
  separate from Windows auth. There is no working SSO option for
  the tsODBC driver.
