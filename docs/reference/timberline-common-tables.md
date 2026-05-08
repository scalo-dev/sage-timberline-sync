# Reference: Common Timberline Tables

Module-by-module list of the tables most often useful for reporting.
This is **not** exhaustive - any given installation has hundreds. Use
`discover.py --tables <name>` to confirm a table exists and to list
its actual columns.

Naming convention: `MASTER_<MODULE>_<ENTITY>[_<N>]`. The `_1`, `_2`,
etc. suffixes split a logical record across multiple physical tables -
e.g. `MASTER_JCM_JOB_1` is the record header, `_2` is financial
totals.

## PJM - Project Management

| Table | Holds |
|---|---|
| `MASTER_PJM_JOB` | One row per job: number, name, address, status, PM/estimator, dates. **47 columns**, includes Address_1, City, State, Postal_Code. |
| `MASTER_PJM_CONTRACT` | Contracts attached to jobs |
| `MASTER_PJM_RFI` | RFIs |
| `MASTER_PJM_TRANSMITTAL` | Transmittals |

## JCM - Job Cost

| Table | Holds |
|---|---|
| `MASTER_JCM_JOB_1` | Job header (parallel to PJM_JOB but cost-side) |
| `MASTER_JCM_JOB_2` | Job financial totals (contract amount, cost-to-date, etc.) |
| `MASTER_JCM_COST_CODE` | Cost code dictionary |
| `MASTER_JCM_CATEGORY` | Cost categories (labor, material, sub, etc.) |
| `CURRENT_JCM_TRANSACTION` | Posted cost transactions |

## GLM - General Ledger

| Table | Holds |
|---|---|
| `MASTER_GLM_ACCOUNT` | Chart of accounts |
| `MASTER_GLM_DIVISION_1` | Division dictionary |
| `MASTER_GLM_PREFIX` | GL account prefixes |
| `CURRENT_GLM_TRANSACTION` | Posted journal entries |

## APM - Accounts Payable

| Table | Holds |
|---|---|
| `MASTER_APM_VENDOR` | Vendor master |
| `CURRENT_APM_INVOICE` | Posted vendor invoices |
| `CURRENT_APM_PAYMENT` | AP payments |

## ARM - Accounts Receivable

| Table | Holds |
|---|---|
| `MASTER_ARM_CUSTOMER` | Customer master |
| `CURRENT_ARM_INVOICE` | AR invoices |
| `CURRENT_ARM_RECEIPT` | Receipts |

## PRM - Payroll

| Table | Holds |
|---|---|
| `MASTER_PRM_EMPLOYEE` | Employee master |
| `MASTER_PRM_PAY` | Pay dictionary |
| `MASTER_PRM_DEDUCT` | Deduction dictionary |
| `CURRENT_PRM_TIME` | Time entries |
| `CURRENT_PRM_CHECK` | Paychecks |

## ESM - Estimating

| Table | Holds |
|---|---|
| `MASTER_ESM_ESTIMATE` | Estimates |
| `MASTER_ESM_ASSEMBLY` | Assemblies |

## CURRENT vs MASTER vs HISTORY

- `MASTER_*` - reference / definitional data (jobs, vendors, COA).
  Generally what you want for an "active list" report.
- `CURRENT_*` - transactional data for the current fiscal period.
- `HISTORY_*` - transactional data for prior periods, archived.

To get **all** transactions across periods, you typically UNION
`CURRENT_*` and `HISTORY_*`. Don't try this in Sage SQL - pull each
separately and concat in Python.

## Status fields

Many MASTER tables have a `Status` column. Common values:
- `In Progress`
- `Unstarted`
- `Closed`
- `Hold`
- `Pending`

These are stored as strings, with the leading-cap formatting shown.
Be defensive in your filters - some installations use slightly
different values.

## Custom fields

Sage installations frequently add custom fields. They appear as extra
columns on the master tables (named like `Custom_Job_Field_1`). Run
`discover.py` to see what's actually present on your install.
