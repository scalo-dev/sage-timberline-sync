# Reference: Extracting a Working Connection String from Access

If anyone in your organization has ever set up Microsoft Access
"Linked Tables" against the Sage company you want to query, they have
already discovered the magic connection-string parameters. You can
just steal them.

This is the single fastest way to find the right
`SAGE_EXTRA_PARAMS` for your install.

## Steps

1. Open the existing `.mdb` or `.accdb` file in Microsoft Access.
2. **External Data** ribbon -> **Linked Table Manager**.
3. Find any linked table whose name starts with `MASTER_` or
   `CURRENT_`. Click the row to select it.
4. Click **Edit** (or the pencil icon, depending on Access version).
5. The "Edit Link" dialog shows the full connection string in a
   text field. It will look like:

   ```
   ODBC;DSN=SCALO COMPANIES;UID=reportuser;PWD=hidden;
   DatabaseType=1;DBQ=\\PITSRV08\TIMBERLINE OFFICE\Data\Scalo\;
   DictionaryMode=0;MaxColSupport=255;ShortenNames=0;StandardMode=0;
   TABLE=Scalo.MASTER_PJM_JOB
   ```

6. Copy each `key=value` pair (everything after `ODBC;` and before
   `;TABLE=`) into your `app/config.py`:

   - `DSN=...` -> `ODBC_DSN`
   - `DBQ=...` -> `SAGE_DATA_FOLDER`
   - `DatabaseType=...` -> `SAGE_DATABASE_TYPE`
   - Everything else -> `SAGE_EXTRA_PARAMS`

   You don't need `UID`/`PWD` from Access (those go in
   `instance/sage_credentials.ini` instead) and you don't need the
   `TABLE=` part (your code names tables explicitly).

## Important caveats

### DSN names will likely differ

The DSN name in Access points at how the linked table was created on
**that user's machine**. If you're deploying on the server, the server
likely has the same Sage data folder exposed under a different DSN
name. Use the server's actual DSN (from `SysWOW64\odbcad32.exe`),
**not** the one from Access.

The other parameters (`DatabaseType`, `DBQ`, `DictionaryMode`, etc.)
are properties of the data, not the DSN, so they should transfer
verbatim.

### If the password is shown as `***`

Some Access versions hide the password in the dialog. You can either:
- Get the password from your Sage admin
- Use VBA to extract the saved connection string:
  ```vba
  ?CurrentDb.TableDefs("MASTER_PJM_JOB").Connect
  ```
  in the Access Immediate Window, which shows the full string
  including PWD.

### If multiple linked tables have different connection strings

That means they were linked at different times to different Sage
companies. Pick the one that targets the company you actually want
to report on (the company name will be in the `DBQ` path).

## Why this works

When you create a linked table in Access, Access calls the ODBC
driver's connection-string editor, which knows the right defaults
for the Pervasive driver. The result is a full connection string
that has been validated by an actual Microsoft product to make
**all** the tables visible. That's why "what does Access do" is the
gold standard.
