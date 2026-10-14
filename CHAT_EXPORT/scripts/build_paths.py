r"""
Build the augmented Excel workbook.

For each row in the Excel with a folder/combine reference, try to find the actual
directory on the E:\OFFICE SARASWATHI\ backup (as captured in all_files_list.txt)
that matches the (YEAR, MONTH, COMPANY NAME) tuple. Append two new columns:
  - MATCHED PATH  : full folder path found on the backup drive (or blank).
  - STATUS        : FOUND / NOT FOUND / MULTIPLE MATCHES / NOT IN LISTING /
                    NEEDS MANUAL / SKIPPED.
"""

import openpyxl
import re
from collections import defaultdict
from copy import copy

LISTING = r"C:\Users\logsarav\Downloads\all_files_list.txt"
SRC     = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET.xlsx"
DST     = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET - WITH PATHS.xlsx"

MONTHS3 = {"JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL",
           "AUG", "SEP", "OCT", "NOV", "DEC"}

STOPWORDS = {"PRIVATE", "PVT", "LIMITED", "LTD", "COMPANY",
             "THE", "AND", "OF", "FOR"}

YEAR_RE = re.compile(r"^\d{4}-\d{2,4}$")

# ---------------------------------------------------------------- helpers
def month_code(text):
    """Return the 3-letter month code found at the start of text (or None)."""
    if not text:
        return None
    alpha = re.sub(r"[^A-Z]", "", text.upper())
    if len(alpha) >= 3 and alpha[:3] in MONTHS3:
        return alpha[:3]
    return None


def normalize_name(text):
    """Uppercase, keep alphanumerics + spaces, strip stopwords."""
    if not text:
        return ""
    up = re.sub(r"[^A-Z0-9]+", " ", str(text).upper()).strip()
    toks = [t for t in up.split() if t not in STOPWORDS]
    return " ".join(toks)


def company_tokens(name):
    """Significant tokens for a company name (used for matching)."""
    up = re.sub(r"[^A-Z0-9]+", " ", str(name).upper()).strip()
    toks = [t for t in up.split() if t not in STOPWORDS and len(t) >= 3]
    return toks


# ---------------------------------------------------------------- listing
def build_index(listing_path):
    """Return:
        dirs           : set of all directory paths seen (uppercase-agnostic).
        month_children : dict[(YEAR, MONTH3)] -> list[(dir_path, folder_name)]
                         where dir_path is the child directory whose parent is
                         a month-named folder inside year YEAR.
    """
    print("Reading listing ...")
    dirs = set()
    with open(listing_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("E:\\OFFICE SARASWATHI\\"):
                continue
            # every ancestor of the file path is a directory
            parts = line.split("\\")
            for i in range(3, len(parts)):        # skip 'E:' and root and its child
                dirs.add("\\".join(parts[:i]))

    print(f"  unique directories: {len(dirs):,}")

    # month_children keyed by (YEAR string, MONTH3)
    month_children = defaultdict(list)
    year_children  = defaultdict(list)   # dict[YEAR] -> list of (dir_path, name)

    for d in dirs:
        parts = d.split("\\")
        # parts[0]=E:, parts[1]=OFFICE SARASWATHI, parts[2]=YEAR (or top-level thing)
        if len(parts) < 4:
            continue
        year = parts[2]
        if not YEAR_RE.match(year):
            continue

        # locate a month-folder in the ancestor chain: parts[j] such that
        # parts[j] starts with a 3-letter month code AND j >= 3
        for j in range(3, len(parts) - 1):
            m = month_code(parts[j])
            if m:
                # parts[:j+2] is the child of the month folder
                child_path = "\\".join(parts[: j + 2])
                child_name = parts[j + 1]
                month_children[(year, m)].append((child_path, child_name))
                break  # only record the first month-anchor per dir

        year_children[year].append((d, parts[-1]))

    # dedup lists
    for k in list(month_children):
        month_children[k] = list({p: n for p, n in month_children[k]}.items())
    for k in list(year_children):
        year_children[k] = list({p: n for p, n in year_children[k]}.items())

    return dirs, month_children, year_children


# ---------------------------------------------------------------- matching
def match_company_folders(candidates, company):
    """Return list of dir paths where folder name matches the company."""
    tokens = company_tokens(company)
    if not tokens:
        return []
    matches = []
    for path, name in candidates:
        norm = normalize_name(name)
        # each significant token must appear as a whole word or substring
        if all(t in norm for t in tokens):
            matches.append(path)
    return matches


def parse_combine(combine):
    """Return (year, month_raw, folder_type, extra_parts) or None."""
    if not combine:
        return None
    parts = re.split(r"\s*>\s*", str(combine).strip())
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return None
    year = parts[0] if YEAR_RE.match(parts[0]) else None
    if not year:
        return None
    month_raw = parts[1] if len(parts) > 1 else ""
    folder_type = parts[2] if len(parts) > 2 else ""
    extra = parts[3:]
    return year, month_raw, folder_type, extra


# ---------------------------------------------------------------- year covered
# Years fully walked in the backup listing (their UPLOADED FORMS subtree exists):
LISTING_YEARS = {"2009-10", "2010-11", "2011-12", "2012-13", "2013-14",
                 "2014-15", "2015-16", "2016-17", "2017-18", "2018-19",
                 "2019-20"}
# Years present in the listing but whose UPLOADED FORMS branch was not walked
# (i.e. the listing script hit an error before finishing).  Rows for these years
# get a clearer status than plain "NOT FOUND".
PARTIAL_LISTING_YEARS = {"2020-21"}


def find_paths_for(company, combine, month_children, year_children):
    """Return (matched_paths_semicolon_joined, status)."""
    parsed = parse_combine(combine)
    if not parsed:
        return "", "SKIPPED (no COMBINE)"
    year, month_raw, folder_type, extra = parsed

    if year in PARTIAL_LISTING_YEARS:
        return "", "NOT IN LISTING (year folder walk incomplete)"
    if year not in LISTING_YEARS:
        return "", "NOT IN LISTING (year not backed up)"

    m3 = month_code(month_raw)
    if not m3:
        # No standard month, e.g. 'CFSS' etc.  Search across whole year.
        if not company:
            return "", "SKIPPED (no company, non-month folder)"
        matches = match_company_folders(year_children.get(year, []), company)
        matches = sorted(set(matches))
        if not matches:
            return "", "NOT FOUND"
        if len(matches) > 1:
            return " ; ".join(matches[:5]), f"MULTIPLE MATCHES ({len(matches)})"
        return matches[0], "FOUND (year-only)"

    candidates = month_children.get((year, m3), [])
    if not candidates:
        return "", f"NOT FOUND (no {m3} folder in {year})"

    if not company:
        # No company name - return the parent month folder path
        month_dirs = sorted({("\\".join(p.split("\\")[:-1])) for p, _ in candidates})
        if len(month_dirs) == 1:
            return month_dirs[0], "FOUND (month folder only, no company)"
        return " ; ".join(month_dirs), "MULTIPLE MONTH FOLDERS"

    matches = match_company_folders(candidates, company)
    matches = sorted(set(matches))
    if not matches:
        # fallback: try substring of joined key
        key = "".join(company_tokens(company))
        soft = [p for p, n in candidates
                if key and key in re.sub(r"[^A-Z0-9]", "", n.upper())]
        soft = sorted(set(soft))
        if soft:
            if len(soft) == 1:
                return soft[0], "FOUND (soft match)"
            return " ; ".join(soft[:5]), f"MULTIPLE SOFT MATCHES ({len(soft)})"
        return "", "NOT FOUND"
    if len(matches) > 1:
        return " ; ".join(matches[:5]), f"MULTIPLE MATCHES ({len(matches)})"
    return matches[0], "FOUND"


# ---------------------------------------------------------------- main
def main():
    dirs, month_children, year_children = build_index(LISTING)

    print("Loading workbook (this may take a bit) ...")
    wb = openpyxl.load_workbook(SRC)

    stats = defaultdict(int)

    # -- Sheet 1: UPLOADED FORMS - COMPANY NAME
    # COMBINE column (F) is a formula; build the combine string from the
    # individual YEAR/MONTH/FOLDER columns (C/D/E) instead.
    ws = wb["UPLOADED FORMS - COMPANY NAME"]
    print(f"Processing '{ws.title}' ({ws.max_row} rows) ...")
    hcols = ws.max_column + 1
    ws.cell(row=1, column=hcols,     value="MATCHED PATH")
    ws.cell(row=1, column=hcols + 1, value="STATUS")
    for r in range(2, ws.max_row + 1):
        company = ws.cell(row=r, column=2).value
        year    = ws.cell(row=r, column=3).value
        month   = ws.cell(row=r, column=4).value
        ftype   = ws.cell(row=r, column=5).value
        combine = None
        if year:
            combine = f"{str(year).strip()} > {str(month or '').strip()} > {str(ftype or '').strip()}"
        path, status = find_paths_for(company, combine, month_children, year_children)
        ws.cell(row=r, column=hcols,     value=path)
        ws.cell(row=r, column=hcols + 1, value=status)
        stats[("UPLOADED", status.split(" ")[0])] += 1

    # -- Sheet 2: COMPANY WISE
    ws = wb["COMPANY WISE"]
    print(f"Processing '{ws.title}' ({ws.max_row} rows) ...")
    hcols = ws.max_column + 1
    ws.cell(row=1, column=hcols,     value="MATCHED PATH")
    ws.cell(row=1, column=hcols + 1, value="STATUS")

    # In COMPANY WISE, company name is only in column B for the first row of a
    # company; subsequent rows are for the same company (col A/B blank).
    current_company = None
    for r in range(2, ws.max_row + 1):
        cname = ws.cell(row=r, column=2).value
        if cname:
            current_company = cname
        combine = ws.cell(row=r, column=3).value
        path, status = find_paths_for(current_company, combine,
                                       month_children, year_children)
        ws.cell(row=r, column=hcols,     value=path)
        ws.cell(row=r, column=hcols + 1, value=status)
        stats[("COMPANY_WISE", status.split(" ")[0])] += 1

    # -- Sheet 3: DIN FORMS (Column B = name, Column C = folder)
    ws = wb["DIN FORMS"]
    print(f"Processing '{ws.title}' ({ws.max_row} rows) ...")
    hcols = ws.max_column + 1
    ws.cell(row=2, column=hcols,     value="MATCHED PATH")
    ws.cell(row=2, column=hcols + 1, value="STATUS")
    for r in range(3, ws.max_row + 1):
        name = ws.cell(row=r, column=2).value
        combine = ws.cell(row=r, column=3).value
        path, status = find_paths_for(name, combine, month_children, year_children)
        ws.cell(row=r, column=hcols,     value=path)
        ws.cell(row=r, column=hcols + 1, value=status)
        stats[("DIN", status.split(" ")[0])] += 1

    # -- Sheet 4: LEI AND OTHERS  (Column B = name, Column C = folder)
    ws = wb["LEI AND OTHERS"]
    print(f"Processing '{ws.title}' ({ws.max_row} rows) ...")
    hcols = ws.max_column + 1
    ws.cell(row=1, column=hcols,     value="MATCHED PATH")
    ws.cell(row=1, column=hcols + 1, value="STATUS")
    for r in range(2, ws.max_row + 1):
        name = ws.cell(row=r, column=2).value
        combine = ws.cell(row=r, column=3).value
        if not (name or combine):
            continue
        path, status = find_paths_for(name, combine, month_children, year_children)
        ws.cell(row=r, column=hcols,     value=path)
        ws.cell(row=r, column=hcols + 1, value=status)
        stats[("LEI", status.split(" ")[0])] += 1

    print("Saving ...")
    wb.save(DST)
    print("Saved:", DST)

    print("\n=== SUMMARY ===")
    for k, v in sorted(stats.items()):
        print(f"  {k[0]:<15} {k[1]:<25} {v}")


if __name__ == "__main__":
    main()
