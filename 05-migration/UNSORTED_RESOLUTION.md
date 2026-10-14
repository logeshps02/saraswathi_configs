# Unsorted / nil resolution

**Do not recopy from E:/F:.** Work on the already-copied dest (`F:\f` or `D:\f`) only.

This PC does not have `F:\f` or `D:\f`. Run the dest script on the laptop that has the copy.

## User decisions (2026-09-03)

| pile | decision |
|---|---|
| Bhairavar Oct 2019 | Move 2 files under **BHAIRAVAR FARMS AND FOODS PRIVATE LIMITED** \ 2019-20 |
| CFSS-NEOMAX 36 folders | Move each subfolder to that company \ 2021-22. Skip if dest already has it |
| CFSS OTHER 62 folders | Same for 2021-22 |
| CLSS 2014 | **Delete** unsorted dest (do not split) |
| CERTIFIED FORMS UPLOADED | **Delete** |
| SURRENDER OF DIN | **Delete** |
| LIST PREPARED (CFSS + Kulumai sub) | **Delete** |
| CERTIFIED FORMS / ARUNKUMAR / other named subfolders | Use company name in subfolder + year; skip if already under that company |
| Chinniaih / Maharaj List | Delete unsorted dest (already under companies) |

## Run on the copy laptop (no recopy)

```
python 05-migration\reorg_unsorted_dest.py --dest F:\f --dry-run
python 05-migration\reorg_unsorted_dest.py --dest F:\f --apply
```

Use `D:\f` if that is the dest. Dry-run first.

Plan: [UNSORTED_DEST_REORG_PLAN.csv](UNSORTED_DEST_REORG_PLAN.csv)  
99 dest moves, 7 full unsorted deletes, 10 duplicate-child deletes.

Leftover that cannot be auto-named: `MEENAKSHISUNDARAM RAMAKRISHNAN-KYC` (person, not a company) and `DIRECTORS LIST.DOCX` under Maharaja Clients.

Do **not** remap nils using UF `COMPANY NAME`.  
Source drives are on the other laptop. Proof here is the two all-files lists + `_COPY_LOG.csv`.

## Local evidence used

| file | what it is |
|---|---|
| [CHAT_EXPORT/source_lists/all_files_list (2).txt](CHAT_EXPORT/source_lists/all_files_list%20(2).txt) | CO `E:\BACK UP FOLDER` + OS `F:\` — 279308 paths |
| [CHAT_EXPORT/source_lists/all_files_list_2025_26.txt](CHAT_EXPORT/source_lists/all_files_list_2025_26.txt) | `E:\2025-26\co` + `E:\2025-26\os` — 40768 paths |
| [_COPY_LOG.csv](_COPY_LOG.csv) | latest copy; all 12 unsorted parents `ok=1` / `robocopy:1`; none in `_COPY_MISSING.csv` |

Script: [compare_unsorted_vs_lists.py](compare_unsorted_vs_lists.py)  
Report: [UNSORTED_VS_LISTS_AND_COPY_LOG.txt](UNSORTED_VS_LISTS_AND_COPY_LOG.txt)

`E:\NOT IN BACKUP\` is **not** in either list (ARUNKUMAR parent).

## How this is resolved

1. Keep unique UF batch folders in `_UNSORTED` until office names companies.
2. Stop recopying dests whose files already landed under a real company (skip list).
3. Do not invent company mappings from leftover folder names.
4. Leave Bhairavar Oct 2019 in unsorted until Review marks that child TRUE.

## Proven leftover=0 — skip recopy (duplicate dest)

| dest | listing | already under |
|---|---|---|
| `_UNSORTED\MAHARAJ SIR LIST\2020-21\MAHARAJ SIR LIST` | 65 files, **8/8 children mapped**, leftover empty | Dharmarathina same source + 8 DIR-3 children. Copy log both dests ok. |

## Skip recopy — same source already copied under a company (leftover files are inside that company dest)

| dest | listing leftover | why skip is still safe |
|---|---|---|
| `_UNSORTED\CHINNIAIH CASES - KYC\...` | 53 hits. `KYC` mapped. Leftover = parent-level master-charge docs + `DIRECTOR & MASTER DETAILS` + `CS_WORK FINAL (3).xlsx` | Whole parent also copied to **Chess Gaja** (`ok=1`). Those leftovers are in Chess Gaja dest. |
| `_UNSORTED\LIST PREPARED\...\PREPARED DOCS FOR List of Shareholders` | 4 files | Nested under already-copied **KULUMAI** Dec 2021 parent. |

Skip file: [UNSORTED_SKIP_DEST.csv](UNSORTED_SKIP_DEST.csv) (wired in `copy_structured_folders.py`).  
SAFE map still 6863 rows. Dest on the other laptop is **not** deleted from here.

## Keep in `_UNSORTED` (unique files; no company-child map rows)

All parent copy-log `ok=1`.

| dest | listing leftover |
|---|---|
| CERTIFIED FORMS | `MEENAKSHISUNDARAM RAMAKRISHNAN-KYC` (7 files) |
| CERTIFIED FORMS UPLOADED | ARUNKUMAR (22), MUTHUSUBRAMANIAN (66), VCVR ASSOCIATES (121) |
| CFSS - NEOMAX | 36 company subfolders, 188 files |
| CFSS FORMS - OTHER COMPANIES | 62 company subfolders, 337 files |
| CLSS 2014 FOR 8 COMPANIES | 24 files (CLSS PDFs + immunity certificates) |
| LIST PREPARED (CFSS folder) | 36 files (scheme xlsx/pdf + NEOMAX receipts) |
| SURRENDER OF DIN | 13 files (procedure / DIR-5 / word docs) |

## Keep — leftover not fully under companies

| dest | fact |
|---|---|
| ARUNKUMAR CASES | Not in either all-files list (`E:\NOT IN BACKUP`). Copy log parent + 3 children (AMN, Everest, Balagopalan) all ok. Unknown extra files. |
| MAHARAJA SIR CLIENTS Oct 2019 | 46 hits. 7 children mapped. **Leftover: `BHAIRAVAR FARMS AND FOODS PRIVATE LIMITED` (2 files) + `DIRECTORS LIST.DOCX`**. Bhairavar has only June 2019 in map. |

## Bhairavar gap (now proven from the OS list)

Listing has `...\MAHARAJA SIR CLIENTS...\BHAIRAVAR FARMS AND FOODS PRIVATE LIMITED` (2 files).  
Review never TRUEd that child. Do not invent mapping. Office must TRUE it, or leave in unsorted.
