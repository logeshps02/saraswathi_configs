r"""
Second-pass fix: eliminates cross-contamination within groups like ARAS.

Two changes vs. the previous fix that produced (6):
1. Improved canonicalize() also collapses space-separated single-letter
   initials (AR A S -> ARAS) so both AR.A.S.-style and AR A S-style
   variants of a name normalise identically.
2. First-token fallback is DISABLED when a company has 2+ significant
   tokens. This stops the fallback from grabbing sister-company folders
   when the shared prefix (ARAS, SAVORIT, MONARCH etc.) matches too many
   things.

Input : BACKUP WORK - FINAL SHEET - WITH PATHS (6).xlsx
Output: BACKUP WORK - FINAL SHEET - WITH PATHS (7).xlsx
The CHANGE column is refreshed to compare (7) against (6).
"""

import openpyxl
import re
from collections import defaultdict

LISTINGS = [
    r"C:\Users\logsarav\Downloads\all_files_list (2).txt",
    r"C:\Users\logsarav\Downloads\all_files_list_2025_26.txt",
]
SRC = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET - WITH PATHS (6).xlsx"
DST = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET - WITH PATHS (7).xlsx"

MONTHS3 = {"JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL",
           "AUG", "SEP", "OCT", "NOV", "DEC"}
STOPWORDS = {"PRIVATE", "PVT", "LIMITED", "LTD", "COMPANY",
             "THE", "AND", "OF", "FOR", "AT", "IN", "ON", "TO", "BY",
             "OR", "AS", "IS", "IT", "ITS", "AN"}
GENERIC = {"JEWELLERS", "TEXTILES", "INDUSTRIES", "ENTERPRISES",
           "SERVICES", "TRADERS", "TRADE", "TRADES", "PHARMA",
           "CHEMICALS", "AGENCIES", "MOTORS", "HOSPITALS",
           "HOSPITAL", "MEDICALS", "MEDICAL", "SUPPLIES",
           "TRADING", "EXPORTS", "IMPORTS", "AUTOMOBILES",
           "CONSTRUCTIONS", "CONSTRUCTION", "GROUP", "GROUPS",
           "HOLDINGS", "HOLDING", "PROJECTS", "PROJECT",
           "SOLUTIONS", "SOLUTION", "TECHNOLOGIES", "TECHNOLOGY",
           "ASSOCIATES", "PRODUCTS", "PRODUCT", "MANUFACTURING",
           "CONSULTANTS", "CONSULTANT", "CONSULTANCY", "AGENCY"}
YEAR_RE = re.compile(r"^\d{4}-(\d{2}|\d{4})$")
CO_PREFIXES = ("E:\\BACK UP FOLDER", "E:\\2025-26\\co")
OS_PREFIXES = ("F:\\", "E:\\2025-26\\os")


# ---------------------------------------------------------------- helpers
def canonicalize(text):
    """Normalize: collapse dot- AND space-separated initials, uppercase, alphanumerize."""
    if not text:
        return ""
    up = str(text).upper()

    # 1) Collapse dot-separated initials.
    #    Pattern: 2+ chunks of letters followed by a dot.
    #    Insert spaces around the collapsed form so downstream words separate cleanly.
    up = re.sub(r"\b((?:[A-Z]+\.){2,})",
                lambda m: " " + m.group(1).replace(".", "") + " ",
                up)

    # 2) Collapse sequences of short (1-3 char) uppercase "words" that are
    #    space-separated — treat them as one abbreviated token.
    #    Example: "AR A S APPLIANCE" -> "ARAS APPLIANCE"
    up = re.sub(r"\b([A-Z]{1,3}(?:\s+[A-Z]{1,3}){1,})\b",
                lambda m: m.group(0).replace(" ", ""),
                up)

    # 3) Alphanumerize.
    up = re.sub(r"[^A-Z0-9]+", " ", up).strip()
    return up


def canonical_year(y):
    m = re.match(r"^(\d{4})-(\d{2,4})$", str(y or "").strip())
    if not m:
        return y
    start, end = m.group(1), m.group(2)
    if len(end) == 4:
        return f"{start}-{end[-2:]}"
    return y


def month_code(text):
    if not text:
        return None
    alpha = re.sub(r"[^A-Z]", "", str(text).upper())
    if len(alpha) >= 3 and alpha[:3] in MONTHS3:
        return alpha[:3]
    return None


def company_tokens(name):
    if not name:
        return []
    canon = canonicalize(name)
    return [t for t in canon.split() if t not in STOPWORDS and len(t) >= 2]


def stem(token):
    for suffix in ("IES", "ES", "S", "ING", "ED"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[: -len(suffix)]
    return token


def token_matches(token, folder_canon):
    if len(token) <= 3:
        return token in folder_canon.split()
    # substring match
    if token in folder_canon:
        return True
    # plural/singular stem match
    st = stem(token)
    if st != token and st in folder_canon:
        return True
    # NOTE: the earlier prefix-of-4-chars match was removed.  It caused
    # "MOTORI" to match "MOTORS" and "ARASPVPV" to match "ARAS" — both
    # wrong.  Substring + stem is sufficient for legitimate plural/singular
    # differences without triggering these false positives.
    return False


def match_all_tokens(candidates, company):
    tokens = company_tokens(company)
    if not tokens:
        return []
    hits = []
    for path, name in candidates:
        canon = canonicalize(name)
        if all(token_matches(t, canon) for t in tokens):
            hits.append(path)
    return hits


def match_first_token(candidates, company):
    """First-token fallback — ONLY if:
       - company has exactly 1 significant token (else return [])
       - that token is NOT generic
    """
    tokens = company_tokens(company)
    if len(tokens) != 1:
        return []  # 2+ tokens → strict-only, no fallback
    first = tokens[0]
    if first in GENERIC:
        return []
    hits = []
    for path, name in candidates:
        canon = canonicalize(name)
        if token_matches(first, canon):
            hits.append(path)
    return hits


def parse_combine(combine):
    if not combine:
        return None
    parts = re.split(r"\s*>\s*", str(combine).strip())
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return None
    if not YEAR_RE.match(parts[0]) and not re.match(r"^(\d{4})-(\d{2})$", parts[0]):
        return None
    year = canonical_year(parts[0])
    month_raw = parts[1] if len(parts) > 1 else ""
    folder_type = parts[2] if len(parts) > 2 else ""
    return year, month_raw, folder_type


def rank_matches(matches, folder_type):
    if not matches:
        return matches
    ft = (folder_type or "").upper()
    if ft.startswith("CO"):
        pref = [m for m in matches if m.startswith(CO_PREFIXES)]
    elif ft.startswith("OS"):
        pref = [m for m in matches if m.startswith(OS_PREFIXES)]
    else:
        pref = []
    other = [m for m in matches if m not in pref]
    return pref + other


def company_name_variants(name):
    if not name:
        return []
    s = str(name).strip()
    out = [s]
    if " - " in s:
        head = s.split(" - ", 1)[0].strip()
        if head and head not in out:
            out.append(head)
    if "_" in s:
        head = s.split("_", 1)[0].strip()
        if head and head not in out:
            out.append(head)
    return out


# ---------------------------------------------------------------- listing
def is_valid_data_line(line):
    line = line.strip()
    if not line or line.startswith("=====") or line.startswith("-----"):
        return False
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
        print(f"  {p}  ->  +{len(dirs)-n0:,} dirs", flush=True)

    month_children = defaultdict(list)
    year_children = defaultdict(list)

    for d in dirs:
        parts = d.split("\\")
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

    for tbl in (month_children, year_children):
        for k in list(tbl):
            seen, out = set(), []
            for p, n in tbl[k]:
                if p not in seen:
                    seen.add(p); out.append((p, n))
            tbl[k] = out
    return month_children, year_children


# ---------------------------------------------------------------- match
def match(company, combine, month_children, year_children):
    parsed = parse_combine(combine)
    if not parsed:
        return "", "SKIPPED (no COMBINE)"
    year, month_raw, folder_type = parsed
    m3 = month_code(month_raw)

    if not m3:
        if not company:
            return "", "SKIPPED (no company, non-month folder)"
        for variant in company_name_variants(company):
            hits = match_all_tokens(year_children.get(year, []), variant)
            hits = sorted(set(hits))
            hits = rank_matches(hits, folder_type)
            if hits:
                if len(hits) == 1:
                    return hits[0], "FOUND (year-only)"
                return " ; ".join(hits[:5]), f"MULTIPLE MATCHES (year-only) ({len(hits)})"
        for variant in company_name_variants(company):
            hits = match_first_token(year_children.get(year, []), variant)
            hits = sorted(set(hits))
            hits = rank_matches(hits, folder_type)
            if hits:
                if len(hits) == 1:
                    return hits[0], "FOUND (first-token year-only)"
                return " ; ".join(hits[:5]), f"MULTIPLE FIRST-TOKEN (year-only) ({len(hits)})"
        return "", "NOT FOUND"

    candidates = month_children.get((year, m3), [])
    if not candidates:
        return "", f"NOT FOUND (no {m3} folder in {year})"

    for variant in company_name_variants(company):
        hits = match_all_tokens(candidates, variant)
        hits = sorted(set(hits))
        hits = rank_matches(hits, folder_type)
        if hits:
            if len(hits) == 1:
                return hits[0], "FOUND"
            return " ; ".join(hits[:5]), f"MULTIPLE MATCHES ({len(hits)})"

    for variant in company_name_variants(company):
        hits = match_first_token(candidates, variant)
        hits = sorted(set(hits))
        hits = rank_matches(hits, folder_type)
        if hits:
            if len(hits) == 1:
                return hits[0], "FOUND (first-token)"
            return " ; ".join(hits[:5]), f"MULTIPLE FIRST-TOKEN MATCHES ({len(hits)})"

    return "", "NOT FOUND"


# ---------------------------------------------------------------- main
def process_sheet(ws, path_col, status_col, header_row, sname,
                  month_children, year_children, change_col):
    current_company = None
    changes = defaultdict(int)
    ws.cell(row=header_row, column=change_col, value="CHANGE (vs 6)")

    total = ws.max_row - header_row
    progress_every = max(200, total // 20)

    for r in range(header_row + 1, ws.max_row + 1):
        if (r - header_row) % progress_every == 0:
            print(f"    ... row {r - header_row}/{total}", flush=True)

        if sname == "COMPANY WISE":
            v = ws.cell(row=r, column=2).value
            if v:
                current_company = v
            company = current_company
            combine = ws.cell(row=r, column=3).value
        elif sname == "UPLOADED FORMS - COMPANY NAME":
            company = ws.cell(row=r, column=2).value
            year_v = ws.cell(row=r, column=3).value
            mo = ws.cell(row=r, column=4).value
            ft = ws.cell(row=r, column=5).value
            if year_v:
                combine = f"{str(year_v).strip()} > {str(mo or '').strip()} > {str(ft or '').strip()}"
            else:
                combine = None
        else:
            company = ws.cell(row=r, column=2).value
            combine = ws.cell(row=r, column=3).value

        old_path = str(ws.cell(row=r, column=path_col).value or "").strip()
        new_path, new_status = match(company, combine, month_children, year_children)

        old_set = set(p.strip() for p in old_path.split(" ; ") if p.strip())
        new_set = set(p.strip() for p in (new_path or "").split(" ; ") if p.strip())

        if old_set == new_set:
            flag = "SAME"
        elif old_set and not new_set:
            flag = "CLEARED (all paths were wrong)"
        elif not old_set and new_set:
            flag = "NEW MATCH"
        elif new_set.issubset(old_set):
            flag = f"NARROWED (removed {len(old_set - new_set)} sister-company path(s))"
        elif old_set.issubset(new_set):
            flag = f"EXPANDED (added {len(new_set - old_set)})"
        else:
            common = old_set & new_set
            if common:
                flag = f"CORRECTED (dropped {len(old_set - common)}, kept {len(common)}, added {len(new_set - common)})"
            else:
                flag = "REPLACED (entirely different match)"

        ws.cell(row=r, column=path_col, value=new_path)
        ws.cell(row=r, column=status_col, value=new_status)
        ws.cell(row=r, column=change_col, value=flag)
        changes[flag.split(" ")[0]] += 1
    return changes


def main():
    month_children, year_children = build_index(LISTINGS)
    print(f"  years indexed         : {len(year_children)}")
    print(f"  (year, month) buckets : {len(month_children)}")

    print(f"Loading workbook: {SRC}")
    wb = openpyxl.load_workbook(SRC)

    overall = defaultdict(int)
    sheets_config = [
        ("UPLOADED FORMS - COMPANY NAME", 1),
        ("COMPANY WISE", 1),
        ("DIN FORMS", 2),
        ("LEI AND OTHERS", 1),
    ]

    for sname, header_row in sheets_config:
        if sname not in wb.sheetnames:
            continue
        ws = wb[sname]
        status_col = ws.max_column - 1   # the second-to-last col is STATUS
        path_col = status_col - 1        # third-to-last is MATCHED PATH
        change_col = ws.max_column       # last col is CHANGE (from previous run)
        print(f"Processing '{sname}' ({ws.max_row - header_row} rows) ...", flush=True)
        ch = process_sheet(ws, path_col, status_col, header_row, sname,
                           month_children, year_children, change_col)
        print(f"  changes: {dict(ch)}")
        for k, v in ch.items():
            overall[(sname, k)] += v

    print("Saving ...")
    wb.save(DST)
    print("Saved:", DST)

    print()
    print("=" * 70)
    print("SUMMARY OF CHANGES vs. (6) workbook")
    print("=" * 70)
    for k, v in sorted(overall.items()):
        print(f"  {k[0]:<32} {k[1]:<40} {v}")


if __name__ == "__main__":
    main()
