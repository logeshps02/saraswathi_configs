# From Home — Next Step: Admin trash restore drill

Log classify is **done**. Eight errors are leftover/known. `SIGN_JOBS:0`. Do not vendor-patch Time Manager. Do not delete LibreSign Reminder/CRL jobs.

Next: prove trash restore with **one drill file** as `saraswathi.admin`. Do **not** delete production files. Do **not** create extra users. Do **not** restore EBS/RDS.

Sign in as `logesh.implementer` only if you need SSM. The drill itself is in the Nextcloud UI.

## 1. Browser (preferred)

1. Open `https://files.t-saraswathi.in` as **`saraswathi.admin`**.
2. In **Files** (home), **New file** named exactly `_restore-drill.txt`.
3. Type one line: `restore-drill` → Save.
4. Select `_restore-drill.txt` → **Delete**.
5. Open **Deleted files**.
6. Restore `_restore-drill.txt` only.
7. Confirm it is back in Files.

## 2. Paste back

- File created yes/no
- Deleted yes/no
- Restored yes/no
- File visible again yes/no

Do not delete any other file. After a green paste we can leave `_restore-drill.txt` in Files (or delete it again later).

### Confirmed (2026-08-26)

Operator: **restored**. Treat trash path as proven for `_restore-drill.txt` only.

| Step | Result |
|---|---|
| Created | yes (implied) |
| Deleted | yes (implied) |
| Restored | **yes** |
| Visible again | yes |

## Stop

Trash drill is complete. Do not delete production folders. Do not empty Deleted files. Do not restore AWS snapshots. Do not create users. Versions drill on the same file is the next guide.
