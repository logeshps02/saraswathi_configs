r"""
Merge the newly-generated 2025-26 listing into the previous match results.

Inputs
------
  all_files_list (2).txt          — the earlier full listing (CO + OS)
  all_files_list_2025_26.txt      — the freshly generated 2025-26 listing
                                    (E:\2025-26\co  and  E:\2025-26\os)
  BACKUP WORK - FINAL SHEET - WITH PATHS (3).xlsx
                                    — the current best matches

Output
------
  BACKUP WORK - FINAL SHEET - WITH PATHS (4).xlsx
      – rows that were previously "NOT ON BACKUP (FY 2025-26 …)" or plain
        "NOT FOUND …" are retried against the combined listing and updated
        in place.  All other rows are left as-is.
"""

import openpyxl
import re
from collections import defaultdict

LISTINGS = [
    r"C:\Users\logsarav\Downloads\all_files_list (2).txt",
    r"C:\Users\logsarav\Downloads\all_files_list_2025_26.txt",
]
SRC = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET - WITH PATHS (3).xlsx"
DST = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET - WITH PATHS (5).xlsx"

MONTHS3 = {"JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL",
           "AUG", "SEP", "OCT", "NOV", "DEC"}
STOPWORDS = {"PRIVATE", "PVT", "LIMITED", "LTD", "COMPANY",
             "THE", "AND", "OF", "FOR"}
YEAR_RE = re.compile(r"^\d{4}-(\d{2}|\d{4})$")

# CO/OS drive-prefix map used to rank matches per the Excel FOLDER hint.
CO_PREFIXES = ("E:\\BACK UP FOLDER", "E:\\2025-26\\co")
OS_PREFIXES = ("F:\\",              "E:\\2025-26\\os")


# ---------------------------------------------------------------- helpers
def canonical_year(y):
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
    return [t for t in up.split() if t not in STOPWORDS and len(t) >= 3]


def stem(token):
    for suffix in ("IES", "ES", "S", "ING", "ED"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[: -len(suffix)]
    return token


def token_matches(token, folder_norm):
    if token in folder_norm:
        return True
    st = stem(token)
    if st != token and st in folder_norm:
        return True
    words = folder_norm.split()
    p4 = token[:4]
    if len(p4) < 4:
        return False
    for w in words:
        if w.startswith(p4):
            return True
    return False


def match_folders(candidates, company, mode="strict"):
    tokens = company_tokens(company)
    if not tokens:
        return []
    if mode == "first":
        tokens = tokens[:1]
    hits = []
    for path, name in candidates:
        norm = normalize_name(name)
        if all(token_matches(t, norm) for t in tokens):
            hits.append(path)
    return hits


def parse_combine(combine):
    if not combine:
        return None
    parts = re.split(r"\s*>\s*", str(combine).strip())
    parts = [p.strip() for p in parts if p.strip()]
    if not parts or not YEAR_RE.match(parts[0]) \
            and not re.match(r"^(\d{4})-(\d{2})$", parts[0]):
        return None
    year = canonical_year(parts[0])
    month_raw = parts[1] if len(parts) > 1 else ""
    folder_type = parts[2] if len(parts) > 2 else ""
    return year, month_raw, folder_type


def rank_matches(matches, folder_type):
    if not matches:
        return matches
    ft = (folder_type or "").upper()
    if ft == "CO":
        pref = [m for m in matches if m.startswith(CO_PREFIXES)]
    elif ft == "OS":
        pref = [m for m in matches if m.startswith(OS_PREFIXES)]
    else:
        pref = []
    other = [m for m in matches if m not in pref]
    return pref + other


# ---------------------------------------------------------------- listing
def is_valid_data_line(line):
    line = line.strip()
    if not line or line.startswith("=====") or line.startswith("-----"):
        return False
    # accept anything under our four roots
    if line.startswith("E:\\BACK UP FOLDER\\"):
        return True
    if line.startswith("E:\\2025-26\\co\\") or line.startswith("E:\\2025-26\\os\\"):
        return True
    if line.startswith("F:\\") and not line.startswith("F:\\System Volume Information") \
            and not line.startswith("F:\\$RECYCLE.BIN"):
        return True
    return False


def build_index(paths):
    print("Reading listings ...")
    dirs = set()
    for p in paths:
        n0 = len(dirs)
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if not is_valid_data_line(line):
                    continue
                parts = line.strip().split("\\")
                for i in range(2, len(parts)):
                    dirs.add("\\".join(parts[:i]))
        print(f"  {p}  ->  +{len(dirs)-n0:,} dirs")

    month_children = defaultdict(list)
    year_children  = defaultdict(list)

    for d in dirs:
        parts = d.split("\\")
        # find year part.  On the 2025-26 tree the year is at position 1
        # (E:, 2025-26, ...). On the older trees it's usually at position 2.
        year_idx = None
        for i in range(1, min(6, len(parts))):
            if YEAR_RE.match(parts[i]):
                year_idx = i
                break
        if year_idx is None:
            continue
        year = canonical_year(parts[year_idx])
        year_children[year].append((d, parts[-1]))
        for j in range(year_idx + 1, len(parts) - 1):
            m = month_code(parts[j])
            if m:
                child_path = "\\".join(parts[: j + 2])
                child_name = parts[j + 1]
                month_children[(year, m)].append((child_path, child_name))
                break

    # dedup
    for tbl in (month_children, year_children):
        for k in list(tbl):
            seen, out = set(), []
            for p, n in tbl[k]:
                if p not in seen:
                    seen.add(p); out.append((p, n))
            tbl[k] = out
    return month_children, year_children


# ---------------------------------------------------------------- retry
def company_variants(name):
    """Return list of company-name variants to try when matching.

    Handles Excel rows like  'CHAKRA CHAINS JEWELLERY PRIVATE LIMITED - ARUN KUMAR CASES'
    by also trying the part before ' - '.
    """
    if not name:
        return []
    s = str(name).strip()
    variants = [s]
    # everything before the first ' - '
    if " - " in s:
        head = s.split(" - ", 1)[0].strip()
        if head and head not in variants:
            variants.append(head)
    # everything before an underscore-separated qualifier
    if "_" in s:
        head = s.split("_", 1)[0].strip()
        if head and head not in variants:
            variants.append(head)
    return variants


def retry(company, combine, month_children, year_children):
    parsed = parse_combine(combine)
    if not parsed:
        return None, None
    year, month_raw, folder_type = parsed
    m3 = month_code(month_raw)
    if not m3 or not company:
        # month-less rows: fall back to year search across all variants
        if not company:
            return None, None
        for variant in company_variants(company):
            hits = match_folders(year_children.get(year, []), variant, "strict")
            hits = sorted(set(hits))
            hits = rank_matches(hits, folder_type)
            if hits:
                if len(hits) == 1:
                    return hits[0], "FOUND (year-only, 2025-26 pass)"
                return " ; ".join(hits[:5]), f"MULTIPLE (year-only, 2025-26 pass) ({len(hits)})"
        # last resort: first-token year-only
        for variant in company_variants(company):
            hits = match_folders(year_children.get(year, []), variant, "first")
            hits = sorted(set(hits))
            hits = rank_matches(hits, folder_type)
            if hits:
                if len(hits) == 1:
                    return hits[0], "FUZZY MATCH (first-token, year-only, 2025-26 pass)"
                return " ; ".join(hits[:5]), f"MULTIPLE FUZZY (first-token, year-only, 2025-26 pass) ({len(hits)})"
        return None, None

    candidates = month_children.get((year, m3), [])
    if not candidates:
        return None, None

    # 1) strict-fuzzy, all variants
    for variant in company_variants(company):
        hits = match_folders(candidates, variant, "strict")
        hits = sorted(set(hits))
        hits = rank_matches(hits, folder_type)
        if hits:
            if len(hits) == 1:
                return hits[0], "FOUND (2025-26 pass)"
            return " ; ".join(hits[:5]), f"MULTIPLE MATCHES (2025-26 pass) ({len(hits)})"

    # 2) first-token, all variants
    for variant in company_variants(company):
        hits = match_folders(candidates, variant, "first")
        hits = sorted(set(hits))
        hits = rank_matches(hits, folder_type)
        if hits:
            if len(hits) == 1:
                return hits[0], "FUZZY MATCH (first-token, 2025-26 pass)"
            return " ; ".join(hits[:5]), f"MULTIPLE FUZZY (first-token, 2025-26 pass) ({len(hits)})"

    return "", "NOT FOUND (still)"


# ---------------------------------------------------------------- main
def main():
    month_children, year_children = build_index(LISTINGS)
    print(f"  years indexed         : {len(year_children)}")
    print(f"  (year, month) buckets : {len(month_children)}")

    print("Loading workbook ...")
    wb = openpyxl.load_workbook(SRC)

    changed = defaultdict(int)

    def is_retry_candidate(status):
        s = str(status or "")
        return (s.startswith("NOT ON BACKUP")
                or s.startswith("NOT FOUND")
                or s == "")

    for sname in ["UPLOADED FORMS - COMPANY NAME", "COMPANY WISE",
                  "DIN FORMS", "LEI AND OTHERS"]:
        ws = wb[sname]
        status_col = ws.max_column
        path_col   = status_col - 1
        header_row = 2 if sname == "DIN FORMS" else 1
        current_company = None
        print(f"Processing '{sname}' ...")

        for r in range(header_row + 1, ws.max_row + 1):
            if sname == "COMPANY WISE":
                v = ws.cell(row=r, column=2).value
                if v:
                    current_company = v
                company_for_row = current_company
                combine = ws.cell(row=r, column=3).value
            elif sname == "UPLOADED FORMS - COMPANY NAME":
                company_for_row = ws.cell(row=r, column=2).value
                year  = ws.cell(row=r, column=3).value
                month = ws.cell(row=r, column=4).value
                ftype = ws.cell(row=r, column=5).value
                combine = f"{str(year).strip()} > {str(month or '').strip()} > {str(ftype or '').strip()}" if year else None
            else:
                company_for_row = ws.cell(row=r, column=2).value
                combine = ws.cell(row=r, column=3).value

            st = ws.cell(row=r, column=status_col).value
            if not is_retry_candidate(st):
                continue

            new_path, new_status = retry(company_for_row, combine,
                                         month_children, year_children)
            if new_status is None:
                continue
            ws.cell(row=r, column=path_col,   value=new_path)
            ws.cell(row=r, column=status_col, value=new_status)
            changed[(sname, new_status.split(" (")[0].strip())] += 1

    print("Saving ...")
    wb.save(DST)
    print("Saved:", DST)

    print("\n=== Rows updated by the 2025-26 pass ===")
    for k, v in sorted(changed.items()):
        print(f"  {k[0]:<32} {k[1]:<45} {v}")


if __name__ == "__main__":
    main()
