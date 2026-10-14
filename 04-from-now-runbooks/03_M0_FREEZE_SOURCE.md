# M0 — Freeze the 132 GB source and pick storage

**Who:** you on the Windows PC that holds the data. No AWS changes. No upload.  
**When:** After T1 (T2 optional). **Must** finish before M1.

---

## 1. Identify the folder

1. In File Explorer open the **root** folder you want in Nextcloud (the one that is ~132 GB **including subfolders**).
2. Write the **full path** (example only: `D:\FIRM-DATA`). Do not paste secrets.
3. Right-click the folder → **Properties**.
4. Write:
   - **Size** (e.g. 132 GB)
   - **Size on disk**
   - **Contains:** X files, Y folders

If Properties hangs, wait. Do not start copy.

---

## 2. Optional PowerShell counts (same PC)

Open PowerShell. Replace `D:\FIRM-DATA` with your path.

```powershell
$root = 'D:\FIRM-DATA'
Get-Item $root | Select-Object FullName
(Get-ChildItem $root -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object).Count
```

Better split:

```powershell
$root = 'D:\FIRM-DATA'
$files = Get-ChildItem $root -Recurse -File -Force -ErrorAction SilentlyContinue
$dirs  = Get-ChildItem $root -Recurse -Directory -Force -ErrorAction SilentlyContinue
'files=' + $files.Count
'dirs=' + $dirs.Count
'bytes=' + ($files | Measure-Object Length -Sum).Sum
```

Record files, dirs, bytes. If Permission denied on some paths, note “errors yes”.

---

## 3. Exclusions (do not upload these)

Tick if present; leave them out of the client sync later:

- Office lock files starting with `~$`
- `Thumbs.db`, `desktop.ini`
- `.tmp` / `~WRL*.tmp`
- Recycle Bin
- Duplicate “COPY” trees if CS confirms they are junk

Do not delete source files. Only exclude in the **client** later.

---

## 4. Target in Nextcloud (decision)

Pick **one** landing folder (admin owns it today):

| Choice | Use when |
|---|---|
| `Firm/Archive/<year-or-name>` | Historical dump |
| `Firm/Clients/<name>` | One client tree |
| `Firm/Statutory/...` | MCA/statutory only |

Write the exact target path. Do **not** dump into `saraswathi.admin` home root.

---

## 5. Pick storage (required)

Read [../02-architecture/FROM_NOW_TO_END_PLAN.md](../02-architecture/FROM_NOW_TO_END_PLAN.md) section 4.

| Option | File next | Matches quotation? |
|---|---|---|
| **S-folder — External storage S3 as Backup_data** | [16_PLAN_S3_FOLDER_INDEX.md](16_PLAN_S3_FOLDER_INDEX.md) → 18 | **Yes — locked 2026-08-31** |
| **S — S3 objectstore** | [04_M1A_S3_OBJECTSTORE.md](04_M1A_S3_OBJECTSTORE.md) | Skip — hides existing Files |
| **E — Grow EBS ≥ 200 GiB** | [05_M1B_GROW_EBS.md](05_M1B_GROW_EBS.md) | **Cancelled** — blows $60 |

**Chosen:** S-folder. Do not grow disk. Do not objectstore.

Budget: $60/mo. 150 GB S3 (~₹320) + 30 GB disk. Do not add 200 GB EBS snapshots.

---

## 6. Network for later upload

- Prefer office broadband, not phone hotspot, for M3.
- Uploads into AWS are free; time is the limit (132 GB can take many hours).
- Do not plan M3 until Backup_data proof + M2 pilot are green.

---

## 7. Verify (M0 exit)

All of these must be written in RESULTS_SHEET:

- Source path
- Size / files / folders
- Target Nextcloud path
- **S or E**
- Exclusions noted

**Stop.** Do not open S3 upload. Do not drag the folder into the browser.

---

## Paste / record

```
M0 path: 
M0 size / size-on-disk: 
M0 files / folders: 
M0 target NC folder: Firm/...
M0 option: S / E
M0 exclusions noted: yes/no
```

Next: **04_M1A** if S, or **05_M1B** if E. Then always [06_M1C_CONFIRM_UPLOAD_LIMITS.md](06_M1C_CONFIRM_UPLOAD_LIMITS.md).
