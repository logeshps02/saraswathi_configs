r"""
Second pass: rebuild the augmented Excel using the new dual-root listing
(E:\BACK UP FOLDER for CO, F:\ for OS).  Handles both 2-digit (2018-19) and
4-digit (2023-2024) year folder names.
"""

import openpyxl
import re
from collections import defaultdict

LISTING = r"C:\Users\logsarav\Downloads\all_files_list (2).txt"
SRC     = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET.xlsx"
DST     = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET - WITH PATHS (2).xlsx"

# Drive roots that the listing was generated from.  Any path that starts
# with one of these is considered a valid candidate for matching.
ROOTS = [
    r"E:\BACK UP FOLDER",   # CO files
    r"F:",                  # OS files (F:\)
]

MONTHS3 = {"JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL",
           "AUG", "SEP", "OCT", "NOV", "DEC"}

STOPWORDS = {"PRIVATE", "PVT", "LIMITED", "LTD", "COMPANY",
             "THE", "AND", "OF", "FOR"}

# Year folder may be YYYY-YY (2018-19) or YYYY-YYYY (2023-2024)
YEAR_RE = re.compile(r"^\d{4}-(\d{2}|\d{4})$")


# ---------------------------------------------------------------- helpers
def canonical_year(y):
    """2023-2024 -> 2023-24 ; 2018-19 -> 2018-19."""
    m = re.match(r"^(\d{4})-(\d{2,4})$", y)
    if not m:
        return y
    start, end = m.group(1), m.group(2)
    if len(end) == 4:
        return f"{start}-{end[-2:]}"
    return y


def month_code(text):
    if not text:
        return None
    alpha = re.sub(r"[^A-Z]", "", text.upper())
    if len(alpha) >= 3 and alpha[:3] in MONTHS3:
        return alpha[:3]
    return None


def normalize_name(text):
    if not text:
        return ""
    up = re.sub(r"[^A-Z0-9]+", " ", str(text).upper()).strip()
    toks = [t for t in up.split() if t not in STOPWORDS]
    return " ".join(toks)


def company_tokens(name):
    up = re.sub(r"[^A-Z0-9]+", " ", str(name).upper()).strip()
    toks = [t for t in up.split() if t not in STOPWORDS and len(t) >= 3]
    return toks


def path_starts_with_root(path):
    for r in ROOTS:
        if path.startswith(r + "\\") or path == r or path.startswith(r + " ") is False and path.startswith(r):
            if path.startswith(r):
                return True
    return False


def is_valid_data_line(line):
    line = line.strip()
    if not line:
        return False
    # anything after a section header should still be a real path
    if line.startswith("=====") or line.startswith("-----"):
        return False
    # top-level roots we care about
    return line.startswith("E:\\BACK UP FOLDER\\") or (
        line.startswith("F:\\") and not line.startswith("F:\\System Volume Information")
        and not line.startswith("F:\\$RECYCLE.BIN")
    )


# ---------------------------------------------------------------- listing
def build_index(listing_path):
    """Read listing txt and produce:
       dirs           : set of all directory paths
       month_children : dict[(canonical_year, MONTH3)] -> list[(dir_path, name)]
       year_children  : dict[canonical_year] -> list[(dir_path, name)]
    """
    print("Reading listing ...")
    dirs = set()
    with open(listing_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if not is_valid_data_line(line):
                continue
            line = line.strip()
            parts = line.split("\\")
            # every prefix (except drive root) is a directory
            for i in range(2, len(parts)):
                dirs.add("\\".join(parts[:i]))
    print(f"  unique directories: {len(dirs):,}")

    month_children = defaultdict(list)
    year_children  = defaultdict(list)

    for d in dirs:
        parts = d.split("\\")
        # find the first year-shaped part (top-level year folder)
        year_idx = None
        for i in range(1, min(5, len(parts))):
            if YEAR_RE.match(parts[i]):
                year_idx = i
                break
        if year_idx is None:
            continue
        year = canonical_year(parts[year_idx])

        # any directory under a year is a candidate for year-only fallback
        year_children[year].append((d, parts[-1]))

        # find a month folder anywhere after the year part
        for j in range(year_idx + 1, len(parts) - 1):
            m = month_code(parts[j])
            if m:
                child_path = "\\".join(parts[: j + 2])
                child_name = parts[j + 1]
                month_children[(year, m)].append((child_path, child_name))
                break

    # dedup by path within each bucket
    for k in list(month_children):
        seen, out = set(), []
        for p, n in month_children[k]:
            if p not in seen:
                seen.add(p)
                out.append((p, n))
        month_children[k] = out
    for k in list(year_children):
        seen, out = set(), []
        for p, n in year_children[k]:
            if p not in seen:
                seen.add(p)
                out.append((p, n))
        year_children[k] = out

    return dirs, month_children, year_children


# ---------------------------------------------------------------- matching
def match_company_folders(candidates, company):
    tokens = company_tokens(company)
    if not tokens:
        return []
    matches = []
    for path, name in candidates:
        norm = normalize_name(name)
        if all(t in norm for t in tokens):
            matches.append(path)
    return matches


def parse_combine(combine):
    if not combine:
        return None
    parts = re.split(r"\s*>\s*", str(combine).strip())
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return None
    if not YEAR_RE.match(parts[0]):
        # accept 2-digit-2 like "2023-24"
        m = re.match(r"^(\d{4})-(\d{2})$", parts[0])
        if not m:
            return None
    year = canonical_year(parts[0])
    month_raw = parts[1] if len(parts) > 1 else ""
    folder_type = parts[2] if len(parts) > 2 else ""
    extra = parts[3:]
    return year, month_raw, folder_type, extra


def rank_matches(matches, folder_type):
    """Prefer matches on the drive that matches OS/CO hint from Excel."""
    if not matches:
        return matches
    ft = (folder_type or "").upper()
    if ft == "CO":
        preferred = [m for m in matches if m.startswith("E:\\BACK UP FOLDER")]
    elif ft == "OS":
        preferred = [m for m in matches if m.startswith("F:\\")]
    else:
        preferred = []
    other = [m for m in matches if m not in preferred]
    return preferred + other


def find_paths_for(company, combine, month_children, year_children):
    parsed = parse_combine(combine)
    if not parsed:
        return "", "SKIPPED (no COMBINE)"
    year, month_raw, folder_type, extra = parsed

    m3 = month_code(month_raw)

    if not m3:
        # no standard month -> year-only search
        if not company:
            return "", "SKIPPED (no company, non-month folder)"
        matches = match_company_folders(year_children.get(year, []), company)
        matches = sorted(set(matches))
        matches = rank_matches(matches, folder_type)
        if not matches:
            return "", "NOT FOUND"
        if len(matches) > 1:
            return " ; ".join(matches[:5]), f"MULTIPLE MATCHES ({len(matches)})"
        return matches[0], "FOUND (year-only)"

    candidates = month_children.get((year, m3), [])
    if not candidates:
        return "", f"NOT FOUND (no {m3} folder in {year})"

    if not company:
        month_dirs = sorted({("\\".join(p.split("\\")[:-1])) for p, _ in candidates})
        if len(month_dirs) == 1:
            return month_dirs[0], "FOUND (month folder only, no company)"
        return " ; ".join(month_dirs), "MULTIPLE MONTH FOLDERS"

    matches = match_company_folders(candidates, company)
    matches = sorted(set(matches))
    matches = rank_matches(matches, folder_type)
    if not matches:
        # soft: concatenated key substring match
        key = "".join(company_tokens(company))
        soft = [p for p, n in candidates
                if key and key in re.sub(r"[^A-Z0-9]", "", n.upper())]
        soft = sorted(set(soft))
        soft = rank_matches(soft, folder_type)
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
    print(f"  years indexed        : {len(year_children)}")
    print(f"  (year, month) buckets: {len(month_children)}")

    print("Loading workbook ...")
    wb = openpyxl.load_workbook(SRC)
    stats = defaultdict(int)

    # ---- Sheet 1: UPLOADED FORMS - COMPANY NAME
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

    # ---- Sheet 2: COMPANY WISE
    ws = wb["COMPANY WISE"]
    print(f"Processing '{ws.title}' ({ws.max_row} rows) ...")
    hcols = ws.max_column + 1
    ws.cell(row=1, column=hcols,     value="MATCHED PATH")
    ws.cell(row=1, column=hcols + 1, value="STATUS")
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

    # ---- Sheet 3: DIN FORMS
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

    # ---- Sheet 4: LEI AND OTHERS
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
