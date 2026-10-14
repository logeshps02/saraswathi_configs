# End-to-end map verification (chained SAFE map)

Checked **every row** of [STRUCTURED_COPY_MAP_SAFE.csv](STRUCTURED_COPY_MAP_SAFE.csv) vs [STRUCTURED_COPY_MAP_FINAL_used.csv](../STRUCTURED_COPY_MAP_FINAL_used.csv) and [UPDATED COMPANY_FOLDERS_IN_FINAL_csv.csv](../UPDATED COMPANY_FOLDERS_IN_FINAL_csv.csv).

This is map audit only. Disk proof is `_COPY_LOG.csv` after a **new** copy with this CSV.

Aborted `D:\f` used the **pre-chain** map. Do **not** resume it.

## Passed (all 6863)

| Check | Result |
|---|---|
| Row count used = safe | **6863 = 6863** (none dropped) |
| Staff sheet | 1322 names: 851 keep, 460 remap, 11 nil |
| Every used dest name is on staff sheet | **0 extra / 0 missing** |
| `source_path` same as used, same order | **0 drift** |
| `old_dest_company` = used `dest_company` | **0 mismatch** |
| `dest_relative` = `dest_company\year\folder` | **0 mismatch** |
| Empty `source_path` | **0** |
| Keep rows | dest unchanged, action `keep` |
| Remap rows | **460/460 names used**; dest = staff target **after alias hops** |
| Chain remaps (2+ hops) | **10** → final spelling (`remap_alias_chain`) |
| Identity staff remaps (`DIN FORMS`, `SWAMIYARMADAM … HOSIPITAL`) | dest unchanged, action `keep` |
| Nil | **12 rows / 11 names** → `_UNSORTED\<old>\year\folder` only. **No** `nil_from_12` |
| DIR-3 / DIN / KYC as top-level company after remap | **0** |
| Remap source still a dest company (non-identity) | **0** |
| Guessed company | **0** |

Actions: keep **5811**, remap_alias **1030**, remap_alias_chain **10**, nil_unsorted **12**.

Companies after remap: **868** (was 873 before chain hops).

## Chain 10 (now final dest)

| From | To |
|---|---|
| KRISHNAMMA RAJA DIR-3 KYC NRK INFRA SYSTEM | NRK INFRA SYSTEM PRIVATE LIMITED |
| KRISHNASAMI-DIR-3 | TAMILNADU STATE TRANSPORT CORPORATION (KUMBAKONAM) LIMITED |
| SARASWATHI THANGADURAI (+ WEB KYC) | TAMILNADU STATE TRANSPORT CORPORATION (KUMBAKONAM) LIMITED |
| MOOKAMBIGAI and THAI LAKSHMI | MOOKAMBIGAI PROPERTIES & HOLDINGS PRIVATE LIMITED |
| RAJENDRAN ALEXMICHAEL DIN1 | CROWN INTERNATIONAL QUALITY CERTIFICATIONS PRIVATE LIMITED |
| SHANMUGAM ARUMUGAM / SHANMUGAM SARAVANAN | SRI SARAVANA TEX EXPORTS INDIA PRIVATE LIMITED |

No leftover `CORPORATED`, `N.R.K INFRA…` as dest, `CERTFICATION`, or `SRI SARAVANAA EXPORTS`.

## Not a miss — duplicates / known holes

- **598** dests: same source listed twice (copy twice, `/XO` skips).
- **12** dests: two disks, same folder name (merge).
- Nested parent/child sources still copied both (duplicate, not miss).
- **4** `H:\OFFICE SARASWATHI\...` — drive not on backup PC.
- **6** form-name-only paths (`ADT-1` `MGT-7` `STK-2` `SH-7` `AOC-4` plus extra token) — Excel split, not folders.
- **7** real 2017-18 `F:\` folders + Green Wealth name-only — dry-run missing (17 total missing). Do **not** invent companies.

## Informational only — same source → two companies

**91 paths** listed in the verifier (40 shown in [E2E_MAP_VERIFY_FAILURES.csv](E2E_MAP_VERIFY_FAILURES.csv)). This is in the **original used map** (COMPANY WISE + UPLOADED FORMS, or two COMPANY WISE names). Safe remap did not invent it.

Copy **duplicates** that folder into **both** dest companies. Nothing omitted. Do **not** drop either dest.

## Recopy (backup PC)

Use **this** CSV only: [STRUCTURED_COPY_MAP_SAFE.csv](STRUCTURED_COPY_MAP_SAFE.csv) in `05-migration` (not root `STRUCTURED_COPY_MAP_SAFE (1).csv`).

Prefer empty dest: rename/delete partial `D:\f` **or** use `D:\SARASWATHI_DOCS_V2`.

```bat
python copy_structured_folders.py --map STRUCTURED_COPY_MAP_SAFE.csv --dest D:\SARASWATHI_DOCS_V2
```

Expect `ok` ≈ 6846, `missing` = 17, `failed` = 0.

Do not sync Nextcloud until `_COPY_LOG.csv` is green. Old pair stays Paused.

Machine-readable: [E2E_MAP_VERIFY_REPORT.txt](E2E_MAP_VERIFY_REPORT.txt), [E2E_MAP_VERIFY_FAILURES.csv](E2E_MAP_VERIFY_FAILURES.csv), [SAFE_REMAP_REPORT.txt](SAFE_REMAP_REPORT.txt).
