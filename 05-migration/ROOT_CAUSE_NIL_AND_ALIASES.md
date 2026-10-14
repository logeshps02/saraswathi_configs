# Root cause — nil folders + alias companies

Do **not** copy or resync until CS confirms how `nil` files should land.

## Issue 1 — `nil` became top-level companies

They **are** in `BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx`, but **not** on **COMPANY WISE**.

They sit on **UPLOADED FORMS - COMPANY NAME** (several also on **LEI AND OTHERS**).  
`build_structured_copy_map.py` sets `dest_company = sanitize(COMPANY NAME)`.  
Disk **folder labels** were typed into that column, so the copy treated them as companies.

| dest (nil) | origin | (12) sheet / row | What actually happened |
|---|---|---|---|
| ARUNKUMAR CASES | REVIEW_TRUE | UF 4847, review 1293 | NOT FOUND → TRUE. Path is the **parent** `E:\NOT IN BACKUP\ARUNKUMAR CASES` (a case pile, not a company). Children already mapped to real companies (e.g. A.M.N. JEWELLERS). |
| CERTIFIED FORMS | FINAL | UF 4744 (+ LEI 6) | Folder name used as COMPANY NAME. FOUND. |
| CERTIFIED FORMS UPLOADED | FINAL | UF 4685 (+ LEI 5) | Same. |
| CFSS - NEOMAX | FINAL | UF 2309 (+ LEI 2) | Same. FOUND (year-only). |
| CFSS FORMS - OTHER COMPANIES | FINAL | UF 2310 (+ LEI 3) | Same. |
| CHINNIAIH CASES - KYC | FINAL | UF 3529 | Person/case pile as COMPANY NAME. |
| CLSS 2014 FOR 8 COMPANIES | FINAL | UF 465 (+ LEI 7) | Batch folder, not one company. |
| LIST PREPARED | FINAL | UF 2311 (+ LEI 4) | MULTIPLE MATCHES: CFSS `LIST PREPARED` **and** a KULUMAI shareholders backup path glued on the same row. |
| MAHARAJ SIR LIST | FINAL | UF 4353 | List folder as COMPANY NAME. |
| MAHARAJA SIR CLIENTS DIR-3 KYC AND WEB KY | FINAL | UF 1713 | KYC batch as COMPANY NAME. |
| SURRENDER OF DIN | FINAL | UF 562 (+ LEI 8) | Form type as COMPANY NAME. |

**Why “not in COMPANY WISE”:** COMPANY WISE is real registered names. These 11 never belonged there. The sort list was **unique dest_company from the copy map**, which included UF/LEI labels.

Re-pointing `nil` using (12) COMPANY NAME **repeats the bug** (that is the bad column).

## Issue 2 — 460 aliases (DIR-3 / spelling / person folders)

Same producer: `dest_company = sanitize(company)` with no “is this a registered company?” check.

Examples: `ANANTH DIN1` → should be PGI ASSET…; `AARVE …_DIR-3` → AARVE POLYMERS; `ADANAWIN AMMA FOODS` vs FOOD PRODUCTS.

Updated sheet: **851 keep, 460 remap, 11 nil**. All 460 remap names exist as dest companies today. **215** dest names look like DIR-3 / DIN / KYC.

## Do not yet

- Copy a new tree
- Delete Backup_data / Final on Nextcloud
- Resume the SAVEPOINT flood on the old pair
- Treat `nil_from_12` in STRUCTURED_COPY_MAP_REMAPPED.csv as correct for the 11 nils
