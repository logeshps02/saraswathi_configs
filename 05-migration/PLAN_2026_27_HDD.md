# 2026–27 HDD — same sort as before, then add to DATA1

**Date:** 2026-09-18 (scope locked: two Uploaded Forms trees only)  
**HDD this PC:** `D:` volume **LENOVO_USB_HDD**  
**Do not** recopy `F:\f` / existing `Backup_data/DATA1`. Do **not** `rclone sync`. Do **not** grow EBS / objectstore / Apply RDS OS. Do **not** desktop full sync.

Previous ingest (closed 2026-09-12): `F:\f` → `nextcloud:Backup_data/DATA1`, **167861** files, **0** differences. That stays.

---

## 1. In scope (locked 2026-09-18)

**Only these two folders.** Nothing else on the HDD (no LEI/MSME/Cancelled/photos/old years/rest of `2026-27`).

| # | Path | Months | Files | Folders | Size |
|---|---|---|---|---|---|
| A | `D:\OFFICE SARASWATHI\2026-27\UPLOADED FORMS` | Apr–Aug 2026 | **3061** | **736** | **2.994 GiB** |
| B | `D:\OFFICE SARASWATHI\CHENNAI OFFICE BACK UP\2026-2027\UPLOADED FORMS` | Apr–Sep 2026 | **3374** | **736** | **3.297 GiB** |
| | **Both (before de-dupe)** | | **6435** | | **~6.29 GiB** |

Same folder style as last year: `UPLOADED ON <date> <COMPANY> <form>`.

If the same company folder exists in **A and B**, keep **both** under `2026-27` with distinct original folder names (do not merge/delete). If dest_relative collides, suffix `_CHENNAI`.

**Out of scope:** rest of `D:\OFFICE SARASWATHI\2026-27` (LEI, MSME, IEC, Cancelled, Other works, View public docs, Register). Rest of Chennai backup except this Uploaded Forms tree. Whole HDD years 2009–26.

---

## 2. Same layout as last time

Local structured dest (then rclone into **existing** DATA1):

```
<LOCAL_DEST>\
  <COMPANY NAME>\
    2026-27\
      <original folder name>\
        (all files from that source folder)
  _UNSORTED\
    <original pile name>\
      2026-27\
        ...
```

Rules copied from the 6863-row safe map:

- A folder only gets a **real company** if the name matches an existing company (or staff names it).
- **Do not guess.** Unknown piles → `_UNSORTED`.
- `nil` is never a company.
- Do not delete HDD files.
- Do not merge into old unsorted leftovers on `F:\f` (that dest is on the **HP**, not this PC).

This PC has **C:** (~364 GB free) and the HDD. HP `F:\f` is **not** here.

**Local dest (this PC):** `C:\SARASWATHI_2026_27`  
Do **not** copy onto `D:\` (source HDD — unplug risk).

**Remote:** `nextcloud:Backup_data/DATA1`  
`rclone copy` adds `Company\2026-27\...` next to existing years. It does **not** delete 2025-26 and earlier.

---

## 3. Phases (do in order)

### Phase 0 — freeze and confirm (you)

1. Do not edit `D:\OFFICE SARASWATHI\2026-27` until copy+check finish.
2. Nextcloud desktop **Paused**.
3. Confirm with CS (reply here):

| Ask | Default if you say “same as before” |
|---|---|
| Only `2026-27`? | **Yes.** Not photos, not 2009–26, not whole HDD |
| Land in DATA1? | **Yes.** Not DATA2 / DATA! |
| New Excel map? | If none, we match folder names to the **868** companies already in the safe map |

### Phase 1 — file list (like `all_files_list_2025_26.txt`)

Save a listing under `CHAT_EXPORT/source_lists/all_files_list_2026_27.txt`.

### Phase 2 — map

Build `STRUCTURED_COPY_MAP_2026_27.csv`:

- Parse `UPLOADED ON … COMPANY …` folder names (same style as 2025-26 `E:\2025-26\co\UPLOADED FORMS\…`).
- Match to companies in `STRUCTURED_COPY_MAP_SAFE.csv` (spelling / PVT / LIMITED cleanup already used).
- Unmatched → `_UNSORTED\...\2026-27\...`
- Report: keep / remap / unsorted counts. **No row dropped.**

Staff can later name unsorted piles (same as Bhairavar / CFSS decisions). Do not invent.

### Phase 3 — dry-run copy on this PC

```bat
python 05-migration\copy_structured_folders.py --map 05-migration\STRUCTURED_COPY_MAP_2026_27.csv --dest C:\SARASWATHI_2026_27 --dry-run
```

Fix missing source paths before apply.

### Phase 4 — apply local copy

Same script without `--dry-run`. Resume-safe (robocopy skip existing). HDD stays the original.

### Phase 5 — rclone to DATA1 (copy only)

Same remote as before. PowerShell, single quotes, **transfers 2 / checkers 4** (CPU lesson).

```powershell
C:\rclone\rclone.exe copy 'C:\SARASWATHI_2026_27' 'nextcloud:Backup_data/DATA1' --transfers 2 --checkers 4 --exclude '~$*' --exclude 'Thumbs.db' --exclude 'desktop.ini' --exclude '*.tmp' --progress --verbose --stats 15s
```

If rclone is not on **this** PC, install to `C:\rclone` and reuse the existing `nextcloud` remote (app password — do not paste in chat).

### Phase 6 — check

```powershell
C:\rclone\rclone.exe check 'C:\SARASWATHI_2026_27' 'nextcloud:Backup_data/DATA1' --one-way --checkers 4
```

Expect **0 differences** for the **new** tree. Unchecked hashes (WebDAV) are not missing files. Do **not** check the whole old 167861 tree unless asked.

---

## 4. Hard stops

- No recopy of `F:\f` / `E:\` / 2009–26 on this HDD.
- No `rclone sync`.
- No Nextcloud desktop full Backup_data.
- No S3 console dump.
- No second rclone while one is running.
- CloudTrail S3 data events stay **off**.
- Do not stop EC2.

---

## 5. Cost / time (order of magnitude)

4.3 GiB / ~4k files is **much smaller** than 123 GiB / 167k. Same path, hours not days, if Wi-Fi is stable. Still use transfers **2**.

---

## Next action

Reply:

1. **Only 2026-27** — yes/no  
2. **DATA1** — yes/no  
3. Any **Excel / company list** for 2026-27, or match to last map  

Then we build the file list + map. Do not start rclone until the map dry-run is clean.

---

## Status 2026-09-18 (this PC)

**Map rebuilt** with final company list (`COMPANY_FOLDERS_IN_FINAL.csv` + `STRUCTURED_COPY_MAP_SAFE.csv`) and explicit discrepancy aliases.

| | |
|---|---|
| Rows | **220** (both Uploaded Forms trees) |
| Mapped companies | **147** |
| Unsorted | **1** left on purpose: `THIRUKONDA SUBRAMANIAN SIVAKUMAR DIR-3 KYC` (HDD Chennai Aug 2026). Staff will map later. |
| Dry-run | **220/220 sources exist** |
| Local dest | `C:\SARASWATHI_2026_27` — copy **ok=220**; 4 spelling dests then **moved** onto existing company folder names |
| rclone | **not started** — `rclone.exe` is **not** on this PC (`C:\rclone` missing). Need install + existing `nextcloud` remote before DATA1 copy. |

Discrepancies mapped to existing folders (not new misspelled companies):

- `AR A S APPLIANCES` → **AR A S APPLIANCE PRIVATE LIMITED**
- `SHIVANAYAHI SOLAR` → **SHIVANAYAHI SOLAR POWER DEVELOPER PRIVATE LIMITED**
- `MTURN TOURISM PRIVATE` → **MTURN TOURISM PRIVATE LIMITED**
- `PUNAM MULLICK / LAADLALADLI` → **LAADLALAADLI.INDIA PRIVATE LIMITED**
- RIO without city → **RIO CHILDREN'S HOSPITAL PRIVATE LIMITED**
- RIO Dindigul / Tanjore stay **separate** existing companies
- `SEL JEGAT PRINTERS` → **SEL JEGAT PRINTER PRIVATE LIMITED**
- `SEL JEGAT PRINT PACK` → **SEL JEGAT PRINT-PACK PRIVATE LIMITED**
- `VISIONARY IMPRESSION` → **VISIONARY IMPRESSIONS PRIVATE LIMITED**
- KB GRID / SPS TRUST / CHARLIE ENGG / AARAVERSE / BRILLYTICS year-tail cleaned
- `ADR PLASTICS` → **ADR PLASTIC PRIVATE LIMITED** (existing)
- `SOUTHFIELD CONSULTANTS` → **SOUTHFIELD CONSULTANT PRIVATE LIMITED** (existing)
- `ORIGINAL HOMOEO MEDICALS` → **ORIGINAL HOMEO MEDICALS PRIVATE LIMITED** (existing)
- `STATFIN GLOBAL SERVICES` → **STATFIN GLOABL SERVICES PRIVATE LIMITED** (existing spelling of that folder)

If a company **already exists**, 2026-27 folders **append** under that same company name (`Company\2026-27\...`). Do not create a second company folder for spelling (PLASTICS/CONSULTANTS/HOMOEO/GLOBAL).

**True new this year** (not on the prior company list) keep their own `Company\2026-27\` folders (AARAVERSE, VALENZA, SHUTUPPANDTRAVEL.COM, etc.).

Do **not** rclone until local copy log shows `ok=220 missing=0 failed=0`.
