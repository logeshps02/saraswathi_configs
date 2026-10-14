# Dry-run 17 missing (2026-09-02)

`ok=6846 missing=17 failed=0` — remap is not the cause. Same 17 as the previous copy.

**Copy the 6846 now.** These 17 stay in `_COPY_MISSING.csv`. Do not invent a company. Do not skip the rest.

| # | Why missing | Count | What to do |
|---|---|---|---|
| A | `H:\OFFICE SARASWATHI\...` — that drive is not on this PC | 4 | Plug in / map H: then recopy only those 4 |
| B | Excel split a **form name** (`ADT-1`, `MGT-7`, `STK-2`, `SH-7`, `AOC-4`) as if it were a folder | 5 | Not real paths. Files live **inside** the sibling 2017-18 folder if that folder exists |
| C | Mapped `F:\2017-18\...` folder not found (incl. misspelt `AUGUEST-17`) | 7 | Search F: / E: for the folder name |
| D | Review TRUE with **folder name only** (no drive) | 1 | Search for `GREEN WEALTH AGRO INDIA LIMITED_MGT-7` |

## A — need H: (4)

1. `H:\OFFICE SARASWATHI\2024-25\SEARCH AND STATUS REPORT\ADR PLASTICS PRIVATE LIMITED-03.06.2024`
2. `H:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\MARCH-18\Uploaded on 28 & 29.03.2018 CONCRETIA ROCK PRODUCTS PRIVATE LIMITED- MGT-14 & SH-7`  
   Duplicate of dest `(2)`. Other Concretia path `E:\NOT IN BACKUP\Uploaded on 28 & 29.03.2018...` was **OK** in dry-run — that copy still happens.
3. `H:\...\RESOLUTIONS\1.BANK ACCOUNT OPENING RESOLUTIONS\MYSTEVA SOLAR GREEN ENERGY PRIVATE LIMITED`
4. `H:\...\RESOLUTIONS\2.GST RESOLUTIONS\MYSTEVA SOLAR GREEN ENERGY PRIVATE LIMITED-GST RESOLUTION`  
   Mysteva **uploaded forms on F:/E: were OK**.

On the backup PC:

```bat
dir H:\
```

If H: appears, recopy later with the same map (robocopy `/XO` skips already-copied).

## B — not folders (5) + C sibling F: path (7)

Excel stored `path;ADT-1;MGT-7`. The builder made extra rows whose `source_path` is only `ADT-1`. Those 5 will always fail until dropped.

The **real** 2017-18 folders (also in your 17) were missing on disk too:

| Company | Mapped path (not found) | Combined forms that should be inside it |
|---|---|---|
| GEOMEO | `F:\2017-18\UPLOADED FORMS\OCTOBER-17\Uploaded on 10.10.17 GEOMEO INFORMATICS PRIVATE LIMITED-AOC-4` | AOC-4 + MGT-7 + ADT-1 |
| ONDEOS | `F:\2017-18\UPLOADED FORMS\SEPTEMBER-17\Uploaded on 04.09.2017 ONDEOS TECHNOLOGIES PRIVATE LIMITED-MGT-14` | MGT-14 + STK-2 |
| QUADRATIC | `F:\2017-18\UPLOADED FORMS\AUGUEST-17\Uploaded on 24.08.2017QUADRATIC STRUCTURE INDIA PRIVATE LIMITED-MGT-14` | MGT-14 + SH-7 (`AUGUEST` spelling) |
| SKYWING | `...\SEPTEMBER-17\Uploaded on 01.09.2017 SKYWING HOLIDAYS PRIVATE LIMITED-AOC-4` | AOC-4 + MGT-7 |
| SKYWING | `...\AUGUEST-17\Uploaded on 18.08.2017 SKYWING HOLIDAYS PRIVATE LIMITED AOC-4` | AOC-4 + MGT-7 |
| YANNARKAY | `...\OCTOBER-17\Uploaded on 06.10.17&07.10.17 SRI YANNARKAY SERVICERS LTD-MGT-7` | MGT-7 + AOC-4 |

Hunt (PowerShell on backup PC):

```powershell
$names = @(
  'Uploaded on 10.10.17 GEOMEO INFORMATICS PRIVATE LIMITED-AOC-4',
  'Uploaded on 04.09.2017 ONDEOS TECHNOLOGIES PRIVATE LIMITED-MGT-14',
  'Uploaded on 24.08.2017QUADRATIC STRUCTURE INDIA PRIVATE LIMITED-MGT-14',
  'Uploaded on 01.09.2017 SKYWING HOLIDAYS PRIVATE LIMITED-AOC-4',
  'Uploaded on 18.08.2017 SKYWING HOLIDAYS PRIVATE LIMITED AOC-4',
  'Uploaded on 06.10.17&07.10.17 SRI YANNARKAY SERVICERS LTD-MGT-7',
  'UPLOADED ON 03.11.2022-GREEN WEALTH AGRO INDIA LIMITED_MGT-7_19-20, 20-21',
  'ADR PLASTICS PRIVATE LIMITED-03.06.2024'
)
foreach ($n in $names) {
  Write-Host "=== $n ==="
  Get-ChildItem F:\,E:\ -Directory -Recurse -Filter $n -ErrorAction SilentlyContinue |
    Select-Object -First 5 FullName
}
```

If found under another letter/spelling, tell Copilot the **full path**. Do not guess a company.

## D — Green Wealth (1)

`source_path` is only the folder name (review TRUE, `manual_typed_path`). Search as above. Other Green Wealth years on F: were OK.

## Copy command (6846)

Same as plan. Empty dest only:

```bat
python copy_structured_folders.py --map STRUCTURED_COPY_MAP_SAFE.csv --dest D:\SARASWATHI_DOCS_V2
```

Expect log: ok ~6846, missing 17, failed 0. Then Phase E sample counts. Do not sync until that copy finishes.
