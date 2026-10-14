# Local safe remap copy + Nextcloud sync

**Goal:** every mapped folder is copied once. No guessed company. Nothing deleted from `F:\` / `E:\`. Cloud is **new folder**, not overwrite of current `Backup_data`.

Do this on the **backup PC** that has `F:\` and `E:\`. This VS Code folder is only maps and scripts.

---

## What this plan does / does not

| Does | Does not |
|---|---|
| Apply staff **460 remaps** only | Guess a company for `nil` |
| Keep **851** names as-is | Drop any of the **6863** map rows |
| Put **11 nil** folders under `_UNSORTED\<old name>\year\folder` | Copy into the old `D:\SARASWATHI_DOCS` / existing `Backup_data` |
| Copy **into a new empty dest** | Delete source files |
| Sync **that new dest** to a **new** Nextcloud folder | Resume the SAVEPOINT flood on old `Data` |
| Prove copy with logs + file counts | Remove the old Nextcloud pair |

**Zero-miss rule:** every `source_path` in the used map must exist on disk **or** be listed in `_COPY_MISSING.csv`. Missing = disk/path problem, not remap. Fix those before calling copy done.

**No-mismatch rule:** a folder only changes company if the updated CSV named a real company. `nil` is never a company.

---

## Tree after copy

```
<NEW_DEST>\
  <real company>\
    <year>\
      <original folder>\
        (all files from source)
  _UNSORTED\
    CERTIFIED FORMS\
      2023-24\
        CERTIFIED FORMS\
    ...
    ARUNKUMAR CASES\
      ...
    LIST PREPARED\
      2021-22\
        LIST PREPARED
        PREPARED DOCS FOR List of Shareholders   ← KULUMAI path, still copied, not guessed
```

`robocopy /E` copies **every file and subfolder** inside each mapped source folder.

---

## Hard stops

- Do **not** resume aborted `D:\f` (that run used the pre-chain map). Rename/delete it or use a new empty dest.
- Do **not** copy onto the previous structured dest (wrong companies already there).
- Do **not** delete `Backup_data` in the browser.
- Do **not** Remove the old Nextcloud pair.
- Do **not** resume full `Data` sync (RDS SAVEPOINT).
- Do **not** grow EBS / Apply RDS OS / paste passwords.
- Do **not** run copy until `SAFE_REMAP_REPORT.txt` shows `input_rows = output_rows`.
- Freeze `F:\` / `E:\` edits until copy+verify finish.

---

## Phase A — build the safe map (already scripted)

On this machine (Logesh files workspace):

```bat
python 05-migration\build_safe_remap_map.py
```

**Already run on this workspace (2026-09-02).** Report: [SAFE_REMAP_REPORT.txt](SAFE_REMAP_REPORT.txt)

| Check | Result |
|---|---|
| input = output | **6863 = 6863** (no row dropped) |
| keep | 5811 (includes identity remaps DIN FORMS / SWAMIYARMADAM HOSIPITAL) |
| remap_alias (staff named company) | 1030 rows |
| remap_alias_chain (2+ hops) | **10** rows → final spelling |
| nil_unsorted | **12** rows (11 names; LIST PREPARED ×2) |
| companies after | **868** |
| leftover remap-source dest (non-identity) | **0** |
| guessed company (`nil_from_12`) | **0** |
| dest collisions, **same** source listed twice | 592 — copy twice, robocopy `/XO` skips, **not a miss** |
| dest collisions, **different** source paths | **11** — same company + same folder name on two disks (usually `E:\2025-26\co\...` vs `E:\BACK UP FOLDER\2025-2026\...`). Copy **merges** both into one dest. Extra files from both stay. Same relative filename: later robocopy can overwrite. These are duplicate backups of the same filing, **not** a wrong company. |
| nested parent/child sources | 81 — child files also sit inside a parent row. Copy both = **duplicate**, not a miss. Do not drop the child. |

Spot-check 10 remaps in Excel (alias → named company). Spot-check all 11 `_UNSORTED` names.

The 11 merge dests (keep as merge unless you ask to suffix `(co)` / `(backup)`):

- BERNICE FASHION LLP — ARUL DEVADOSS DIR-3; NINCY DIR-3  
- CLOUDTERMINAL CONSULTANCY — DIR-12 and DIR-12 (2)  
- DIGININEFIN TECHNOLOGIES — ADT-1  
- EOX SECURE SOLUTIONS — YASIN DIR-3  
- MARK ELITE PROPERTIES — AF-24-25; MGT-14  

If you want **both disk copies as separate folders**, say so before Phase D. Default: merge (nothing deleted from source).

---

## Phase B — backup PC setup

Copy these into one folder on the PC that has `F:\` and `E:\`:

1. `STRUCTURED_COPY_MAP_SAFE.csv`
2. `copy_structured_folders.py`

Need:

- Python 3
- Empty dest, e.g. `D:\SARASWATHI_DOCS_V2` (NTFS, **not** the old dest)
- Free space **> source used size** (previous set ~132 GB; keep 20% extra)
- Dest path **not** inside `F:\` or `E:\` source trees

Confirm drives:

```bat
dir F:\
dir E:\
```

---

## Phase C — dry-run (no copy)

```bat
python copy_structured_folders.py --map STRUCTURED_COPY_MAP_SAFE.csv --dest D:\SARASWATHI_DOCS_V2 --dry-run
```

Expect ~6863 folder checks. Then:

- Open `05-migration\COPY_DRY_RUN_MISSING.csv` (script writes next to the `.py` on dry-run)
- **0 missing** = all mapped folders exist → Phase D
- Any missing = **do not copy yet**. Re-attach the disk / fix letter / note the path. Those files stay on source until the path works.

Optional 10-folder test:

```bat
python copy_structured_folders.py --map STRUCTURED_COPY_MAP_SAFE.csv --dest D:\SARASWATHI_DOCS_V2 --dry-run --limit 10
```

---

## Phase D — real copy (new empty dest only)

```bat
python copy_structured_folders.py --map STRUCTURED_COPY_MAP_SAFE.csv --dest D:\SARASWATHI_DOCS_V2
```

Leave PC on. Resume if stopped (`--start N` is 1-based row; already-copied same-size files skip via `/XO`):

```bat
python copy_structured_folders.py --map STRUCTURED_COPY_MAP_SAFE.csv --dest D:\SARASWATHI_DOCS_V2 --start 501
```

Logs on dest:

- `_COPY_LOG.csv` — each folder ok/fail
- `_COPY_MISSING.csv` — source not found

---

## Phase E — prove nothing missed (required before sync)

1. Log rows = 6863 (or start-offset remainder + previous log).
2. `ok=1` for every row that existed on dry-run.
3. `_COPY_MISSING.csv` empty **or** every line explained (disk offline).
4. No `failed` except robocopy extra-file codes 0–7 (script already treats 0–7 as OK).
5. Dest top-level: real companies + `_UNSORTED` only. **No** `ANANTH DIN1`, **no** `CERTIFIED FORMS` as a company.
6. File-count sample (PowerShell), pick 5 large companies + `_UNSORTED`:

```powershell
$src = 'F:\....mapped folder....'
$dst = 'D:\SARASWATHI_DOCS_V2\COMPANY\YEAR\folder'
(Get-ChildItem $src -Recurse -File -Force | Measure-Object).Count
(Get-ChildItem $dst -Recurse -File -Force | Measure-Object).Count
```

Counts must match. If dest **greater**, nested parent also copied those files — check report nested list; files are not missing.

7. Optional whole-tree compare (slow, run overnight after copy):

```powershell
# count files in dest excluding _COPY_*.csv
(Get-ChildItem D:\SARASWATHI_DOCS_V2 -Recurse -File -Force |
  Where-Object { $_.Name -notlike '_COPY_*' } |
  Measure-Object).Count
```

Compare to sum of unique source folders (nested parents inflate dest count). Prefer **per-row** counts from the map, not one global number.

**Do not sync until Phase E is green.**

---

## Phase F — Nextcloud (new remote folder only)

Old pair stays **Paused**. Do not Remove. Do not delete S3.

1. Browser as `saraswathi.admin` → **Backup_data** → New folder e.g. `Final_v2` (empty).
2. Client → **Add folder sync connection**:
   - Local = `D:\SARASWATHI_DOCS_V2`
   - Remote = `/Backup_data/Final_v2`
   - Full files for this pair only
   - Exclude `~$*`, `Thumbs.db`, `desktop.ini`, `*.tmp`, `_COPY_LOG.csv`, `_COPY_MISSING.csv`
3. Start. Watch disk alarm. If `SAVEPOINT DOCTRINE_2`: **Pause** (do not Remove). Then one company folder at a time or slow the client. Do not grow EBS.
4. After client idle + 0 errors: browser open a few companies + `_UNSORTED`. Confirm files.

When `Final_v2` is complete and staff sign off, **then** decide whether to hide/unshare old `Backup_data` tree. Not this week.

---

## The 11 unsorted folders (copied, not mapped)

`ARUNKUMAR CASES`, `CERTIFIED FORMS`, `CERTIFIED FORMS UPLOADED`, `CFSS - NEOMAX`, `CFSS FORMS - OTHER COMPANIES`, `CHINNIAIH CASES - KYC`, `CLSS 2014 FOR 8 COMPANIES`, `LIST PREPARED` (2 paths), `MAHARAJ SIR LIST`, `MAHARAJA SIR CLIENTS DIR-3 KYC AND WEB KY`, `SURRENDER OF DIN`.

Staff can later split `_UNSORTED` into real companies. Until then files live there so they are **not lost** and **not wrongly filed**.

KULUMAI’s own company rows stay under **KULUMAI MILK PRODUCER COMPANY LIMITED**. The extra LIST PREPARED path that pointed at a KULUMAI subfolder is also copied under `_UNSORTED\LIST PREPARED` (duplicate, not a miss).

---

## Order (do not skip)

1. Run `build_safe_remap_map.py` — 6863 in = 6863 out  
2. Read `SAFE_REMAP_REPORT.txt` — collisions / nested  
3. Dry-run on backup PC — 0 missing  
4. Copy to **new** dest  
5. Verify logs + sample file counts  
6. Sync **only** that dest → `/Backup_data/Final_v2`  
7. Keep old pair paused  

Say **go** after you have read the report if you want the map built here first. Copy still has to run on the PC with `F:\` `E:\`.
