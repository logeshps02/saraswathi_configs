r"""
Fuzzy second-pass: re-run only the NOT-FOUND rows from the (2) workbook with
looser matching rules (plural/singular tolerance, stem-prefix match, and a
first-token fallback).  Skips 2025-26 rows because the user confirmed the
files for that FY are not on the backup yet.  Writes result to (3) workbook.
"""

import openpyxl
import re
from collections import defaultdict

LISTING = r"C:\Users\logsarav\Downloads\all_files_list (2).txt"
SRC     = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET - WITH PATHS (2).xlsx"
DST     = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET - WITH PATHS (3).xlsx"

MONTHS3 = {"JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL",
           "AUG", "SEP", "OCT", "NOV", "DEC"}
STOPWORDS = {"PRIVATE", "PVT", "LIMITED", "LTD", "COMPANY",
             "THE", "AND", "OF", "FOR"}
YEAR_RE = re.compile(r"^\d{4}-(\d{2}|\d{4})$")

# FY the user said is legitimately not on the backup yet
SKIP_YEARS = {"2025-26"}


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
    toks = [t for t in up.split() if t not in STOPWORDS and len(t) >= 3]
    return toks


# ---------------------------------------------------------------- fuzzy matching
def stem(token):
    """Simple English stem: drop plural / -ing endings, keep >= 4 chars."""
    for suffix in ("IES", "ES", "S", "ING", "ED"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[: -len(suffix)]
    return token


def token_matches(token, folder_norm):
    """Fuzzy check: token or its stem must be a substring of the normalized
    folder name, OR some folder word must start with the token's first 4 chars.
    """
    if token in folder_norm:
        return True
    st = stem(token)
    if st != token and st in folder_norm:
        return True
    # prefix stem match against folder words
    words = folder_norm.split()
    p4 = token[:4]
    if len(p4) < 4:
        return False
    for w in words:
        if w.startswith(p4):
            return True
        # also allow token to be a prefix of folder word (short-form matches)
        if len(token) >= 4 and w.startswith(token[:4]) and len(w) >= 4:
            return True
    return False


def match_folders_fuzzy(candidates, company, mode="strict"):
    """
    mode='strict'  : all significant tokens must match (using fuzzy token_matches)
    mode='first'   : only the FIRST significant token must match (looser)
    """
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
    if not parts:
        return None
    if not YEAR_RE.match(parts[0]):
        m = re.match(r"^(\d{4})-(\d{2})$", parts[0])
        if not m:
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
        preferred = [m for m in matches if m.startswith("E:\\BACK UP FOLDER")]
    elif ft == "OS":
        preferred = [m for m in matches if m.startswith("F:\\")]
    else:
        preferred = []
    other = [m for m in matches if m not in preferred]
    return preferred + other


# ---------------------------------------------------------------- listing
def is_valid_data_line(line):
    line = line.strip()
    if not line or line.startswith("=====") or line.startswith("-----"):
        return False
    return line.startswith("E:\\BACK UP FOLDER\\") or (
        line.startswith("F:\\")
        and not line.startswith("F:\\System Volume Information")
        and not line.startswith("F:\\$RECYCLE.BIN")
    )


def build_index(listing_path):
    print("Reading listing ...")
    dirs = set()
    with open(listing_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if not is_valid_data_line(line):
                continue
            parts = line.strip().split("\\")
            for i in range(2, len(parts)):
                dirs.add("\\".join(parts[:i]))
    print(f"  unique directories: {len(dirs):,}")

    month_children = defaultdict(list)
    year_children  = defaultdict(list)

    for d in dirs:
        parts = d.split("\\")
        year_idx = None
        for i in range(1, min(5, len(parts))):
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
    for k in list(month_children):
        seen, out = set(), []
        for p, n in month_children[k]:
            if p not in seen:
                seen.add(p); out.append((p, n))
        month_children[k] = out
    for k in list(year_children):
        seen, out = set(), []
        for p, n in year_children[k]:
            if p not in seen:
                seen.add(p); out.append((p, n))
        year_children[k] = out
    return month_children, year_children


# ---------------------------------------------------------------- retry logic
def retry_not_found(company, combine, month_children, year_children):
    """Return (matched_path_string, new_status) or (None, None) to leave alone."""
    parsed = parse_combine(combine)
    if not parsed:
        return None, None
    year, month_raw, folder_type = parsed

    if year in SKIP_YEARS:
        return "", "NOT ON BACKUP (FY 2025-26 not backed up yet)"

    m3 = month_code(month_raw)
    if not m3 or not company:
        return None, None

    candidates = month_children.get((year, m3), [])
    if not candidates:
        return None, None

    # pass 1: fuzzy (stem + plural + prefix) strict-all-tokens
    hits = match_folders_fuzzy(candidates, company, mode="strict")
    hits = sorted(set(hits))
    hits = rank_matches(hits, folder_type)
    if hits:
        if len(hits) == 1:
            return hits[0], "FOUND (fuzzy)"
        return " ; ".join(hits[:5]), f"MULTIPLE FUZZY MATCHES ({len(hits)})"

    # pass 2: first-token only (looser)
    hits = match_folders_fuzzy(candidates, company, mode="first")
    hits = sorted(set(hits))
    hits = rank_matches(hits, folder_type)
    if hits:
        if len(hits) == 1:
            return hits[0], "FUZZY MATCH (first-token)"
        return " ; ".join(hits[:5]), f"MULTIPLE FUZZY (first-token) MATCHES ({len(hits)})"

    return None, None   # leave existing NOT FOUND alone


# ---------------------------------------------------------------- main
def build_combine(sheet_name, ws, r):
    """Return (company, combine) tuple for a row."""
    if sheet_name == "UPLOADED FORMS - COMPANY NAME":
        company = ws.cell(row=r, column=2).value
        year    = ws.cell(row=r, column=3).value
        month   = ws.cell(row=r, column=4).value
        ftype   = ws.cell(row=r, column=5).value
        combine = None
        if year:
            combine = f"{str(year).strip()} > {str(month or '').strip()} > {str(ftype or '').strip()}"
        return company, combine
    if sheet_name == "COMPANY WISE":
        # company from col B may be blank; caller must track it
        return ws.cell(row=r, column=2).value, ws.cell(row=r, column=3).value
    # DIN FORMS / LEI AND OTHERS
    return ws.cell(row=r, column=2).value, ws.cell(row=r, column=3).value


def main():
    month_children, year_children = build_index(LISTING)
    print(f"  years indexed        : {len(year_children)}")
    print(f"  (year, month) buckets: {len(month_children)}")

    print("Loading workbook ...")
    wb = openpyxl.load_workbook(SRC)

    changed = defaultdict(int)
    for sname in ["UPLOADED FORMS - COMPANY NAME", "COMPANY WISE",
                  "DIN FORMS", "LEI AND OTHERS"]:
        ws = wb[sname]
        # last two columns are MATCHED PATH and STATUS from previous run
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
            else:
                company_for_row, combine = build_combine(sname, ws, r)

            st = ws.cell(row=r, column=status_col).value or ""
            if not str(st).startswith("NOT FOUND"):
                continue
            new_path, new_status = retry_not_found(
                company_for_row, combine, month_children, year_children
            )
            if new_status is None:
                continue
            ws.cell(row=r, column=path_col,   value=new_path)
            ws.cell(row=r, column=status_col, value=new_status)
            changed[(sname, new_status.split(" ")[0] + " " + new_status.split(" ")[1] if " " in new_status else new_status)] += 1

    print("Saving ...")
    wb.save(DST)
    print("Saved:", DST)

    print()
    print("=== ROWS UPDATED (previously NOT FOUND) ===")
    for k, v in sorted(changed.items()):
        print(f"  {k[0]:<32} {k[1]:<45} {v}")


if __name__ == "__main__":
    main()
