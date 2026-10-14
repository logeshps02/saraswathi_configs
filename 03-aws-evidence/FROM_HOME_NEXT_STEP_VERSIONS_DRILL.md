# From Home — Next Step: Admin versions restore drill

Trash restore is **done** on `_restore-drill.txt`. Do not delete other files. Do not empty Deleted files.

Next: prove **file versions** on that same file. Do **not** create extra users. Do **not** restore AWS snapshots.

Browser as **`saraswathi.admin`** at `https://files.t-saraswathi.in`.

## 1. Create a second version

1. Open `_restore-drill.txt` (must be back in Files).
2. Change the text to `restore-drill-v2` → Save / close.
3. Open **Details** / sidebar for `_restore-drill.txt` → **Versions**.
4. Confirm at least one older version is listed.
5. Restore the older version (`restore-drill`).
6. Re-open the file and confirm the text is `restore-drill` again (not v2).

If Versions is empty: wait a few seconds, refresh, try once more. Do not create a second drill file.

## 2. Paste back

- Second save yes/no
- Older version listed yes/no
- Restored older version yes/no
- File text after restore (`restore-drill` or still `v2`)

### Confirmed (2026-08-26)

Operator: **it is working**. Treat versions restore as proven on `_restore-drill.txt`.

## Stop

Versions drill is complete. Do not delete production files. Do not restore EBS/RDS. Do not create users. Remaining Phase 6 UI/audit checks are batched in `FROM_HOME_NEXT_STEP_PHASE6_BATCH.md`.
