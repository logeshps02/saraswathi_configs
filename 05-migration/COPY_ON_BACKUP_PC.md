# Copy mapped folders on the backup PC

Yes — the final map already combines **both** files you shared:

| Original file | What was taken | Rows in final map |
|---|---|---|
| `BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx` | Found / multiple-match folders | **6402** (`origin=FINAL`) |
| `NOT FOUND - REVIEW - ALL COMPLETED.xlsx` | Rows with **SELECT = TRUE** | **461** (`origin=REVIEW_TRUE`) |

After spelling + LTD/LIMITED + P/PVT→PRIVATE cleanup: **6863** copy lines, **1322** companies.

Layout on dest:

```
<DEST>\
  <COMPANY NAME>\
    <YEAR>\
      <original folder name>\
        (all files and subfolders from the source path)
```

## What to copy to that PC

Put these two files in the same folder:

1. `STRUCTURED_COPY_MAP_FINAL.csv`
2. `copy_structured_folders.py`

Python 3 is enough (no pandas). Windows `robocopy` is used for large folders.

## Test first (no copy)

```bat
python copy_structured_folders.py --dest D:\SARASWATHI_DOCS --dry-run --limit 10
```

This checks whether the first 10 source paths exist on that PC (`F:\`, `E:\BACK UP FOLDER`, etc.).

## Real copy with progress

```bat
python copy_structured_folders.py --dest D:\SARASWATHI_DOCS
```

You will see:

```
[120/6863  1.7%  eta 4h 12m] COMPANY NAME\2018-19\Uploaded on ...
```

Logs written under dest:

- `_COPY_LOG.csv` — each folder ok/fail
- `_COPY_MISSING.csv` — source path not found on that PC

## Resume if it stops

Skip the first 500 rows (1-based):

```bat
python copy_structured_folders.py --dest D:\SARASWATHI_DOCS --start 501
```

Already-copied files of the same size/date are skipped (`robocopy /XO`).

## Notes

- Dest drive must have enough free space for the full backup set.
- Do not copy while Excel has the CSV open.
- `(2)` folder names are kept on purpose.
- 99 unresolved NOT FOUND rows were never in this map (no TRUE tick / no path).
