r"""
Third-pass fix: use the "deep path" info in the COMBINE column
(OTHER WORKS > CERTIFIED FORMS > ARUNKUMAR SIR etc.) to filter candidate
paths so each row returns only folders in the right sub-tree.

Bug fixed in this pass:
For a row like  '2025-26>CO>OTHER WORKS>CERTIFIED FORMS>ARUNKUMAR SIR'  the
matcher was previously doing a plain year-only search and returning EVERY
folder for that company in 2025-26 (including UPLOADED FORMS\MAY, DEMAT\ISIN
etc.), even though the row is explicitly pointing at the CERTIFIED FORMS
sub-tree.

Now the extra ">" parts are parsed as sub-tree constraints:
   extras = [OTHER WORKS, CERTIFIED FORMS, ARUNKUMAR SIR]
The distinctive tokens (CERTIFIED, ARUNKUMAR) become required substrings
in every candidate path.  Generic words (OTHER, WORKS, FORMS, SIR, CS, EFORMS)
are ignored so we don't over-constrain.

Also fixed:
- Combines like  '2023-24 > AUGUST > CO - ARUN KUMAR'  now split the
  descriptor from the folder-type (CO) and use "ARUN KUMAR" as an
  extra filter.
- Combines like  '2025-26>CO>...'  where the second part is a folder-type
  (CO/OS) instead of a month are properly parsed.

Input : (7).xlsx    Output: (8).xlsx
"""

import openpyxl
import re
from collections import defaultdict

LISTINGS = [
    r"C:\Users\logsarav\Downloads\all_files_list (2).txt",
    r"C:\Users\logsarav\Downloads\all_files_list_2025_26.txt",
]
SRC = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET - WITH PATHS (7).xlsx"
DST = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET - WITH PATHS (8).xlsx"

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

# Common words that appear in EXTRAS but aren't distinctive enough
# to constrain path matching by themselves.
COMMON_EXTRAS = {"OTHER", "OTHERS", "WORKS", "WORK", "FORMS", "EFORMS",
                 "DOCS", "FILES", "DOCUMENTS", "DOCUMENT", "PAPERS",
                 "RECORDS", "DIVISION", "DEPARTMENT", "GROUP", "TYPE",
                 "KIND", "SIR", "MAM", "MADAM", "MR", "MRS", "MISS",
                 "CS", "MISC", "GENERAL", "CASES", "CASE",
                 "NOTE", "NOTES", "COPY", "UPDATE", "REGISTRATION",
                 "STATUS", "REPORT", "MASTER"}

YEAR_RE = re.compile(r"^\d{4}-(\d{2}|\d{4})$")
CO_PREFIXES = ("E:\\BACK UP FOLDER", "E:\\2025-26\\co")
OS_PREFIXES = ("F:\\", "E:\\2025-26\\os")


# ---------------------------------------------------------------- helpers
def canonicalize(text):
    if not text:
        return ""
    up = str(text).upper()
    up = re.sub(r"\b((?:[A-Z]+\.){2,})",
                lambda m: " " + m.group(1).replace(".", "") + " ",
                up)
    up = re.sub(r"\b([A-Z]{1,3}(?:\s+[A-Z]{1,3}){1,})\b",
                lambda m: m.group(0).replace(" ", ""),
                up)
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
    if token in folder_canon:
        return True
    st = stem(token)
    if st != token and st in folder_canon:
        return True
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
    tokens = company_tokens(company)
    if len(tokens) != 1:
        return []
    first = tokens[0]
    if first in GENERIC:
        return []
    hits = []
    for path, name in candidates:
        canon = canonicalize(name)
        if token_matches(first, canon):
            hits.append(path)
    return hits


# ---------------------------------------------------------------- extras
def significant_extras_tokens(extras_parts):
    """Extract distinctive tokens from the extras list.
    Skips STOPWORDS, GENERIC and COMMON_EXTRAS."""
    toks = []
    for e in extras_parts:
        canon = canonicalize(e)
        for t in canon.split():
            if len(t) < 3:
                continue
            if t in STOPWORDS:
                continue
            if t in COMMON_EXTRAS:
                continue
            if t in GENERIC:
                continue
            if t not in toks:
                toks.append(t)
    return toks


def path_matches_extras(path, extras_toks):
    """True if every distinctive extras token appears in the candidate path
    (substring, whole word, or prefix-of-first-4 for compound tokens)."""
    if not extras_toks:
        return True
    canon = canonicalize(path)
    words = canon.split()
    for tok in extras_toks:
        if tok in canon:
            continue
        if len(tok) >= 6:
            p4 = tok[:4]
            if any(w.startswith(p4) for w in words):
                continue
        return False
    return True


def parse_combine(combine):
    """Parse the COMBINE cell.  Returns (year, month_raw, folder_type, extras)."""
    if not combine:
        return None
    parts = re.split(r"\s*>\s*", str(combine).strip())
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return None
    if not YEAR_RE.match(parts[0]) and not re.match(r"^(\d{4})-(\d{2})$", parts[0]):
        return None
    year = canonical_year(parts[0])

    second = parts[1] if len(parts) > 1 else ""
    m3 = month_code(second)
    if m3:
        # standard:  year > MONTH > TYPE > [extras...]
        month_raw = second
        folder_type = parts[2] if len(parts) > 2 else ""
        extras = parts[3:] if len(parts) > 3 else []
    else:
        # deep-path:  year > TYPE > extras...
        # (e.g. 2025-26>CO>OTHER WORKS>CERTIFIED FORMS>ARUNKUMAR SIR)
        month_raw = ""
        folder_type = second
        extras = parts[2:] if len(parts) > 2 else []

    # "CO - ARUN KUMAR" style descriptors on the folder-type -> move the
    # descriptor into extras.
    if " - " in folder_type:
        head, tail = folder_type.split(" - ", 1)
        extras.insert(0, tail.strip())
        folder_type = head.strip()

    return year, month_raw, folder_type, extras


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
    print("Reading listings ...", flush=True)
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
    year, month_raw, folder_type, extras = parsed
    extras_toks = significant_extras_tokens(extras)
    m3 = month_code(month_raw)

    def apply_extras_filter(hits):
        if not extras_toks:
            return hits
        return [h for h in hits if path_matches_extras(h, extras_toks)]

    if not m3:
        if not company:
            return "", "SKIPPED (no company, non-month folder)"
        for variant in company_name_variants(company):
            hits = match_all_tokens(year_children.get(year, []), variant)
            hits = apply_extras_filter(hits)
            hits = sorted(set(hits))
            hits = rank_matches(hits, folder_type)
            if hits:
                if len(hits) == 1:
                    return hits[0], "FOUND (year-only)"
                return " ; ".join(hits[:5]), f"MULTIPLE MATCHES (year-only) ({len(hits)})"
        for variant in company_name_variants(company):
            hits = match_first_token(year_children.get(year, []), variant)
            hits = apply_extras_filter(hits)
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
        hits = apply_extras_filter(hits)
        hits = sorted(set(hits))
        hits = rank_matches(hits, folder_type)
        if hits:
            if len(hits) == 1:
                return hits[0], "FOUND"
            return " ; ".join(hits[:5]), f"MULTIPLE MATCHES ({len(hits)})"

    for variant in company_name_variants(company):
        hits = match_first_token(candidates, variant)
        hits = apply_extras_filter(hits)
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
    ws.cell(row=header_row, column=change_col, value="CHANGE (vs 7)")

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
            flag = "CLEARED (extras filter removed all)"
        elif not old_set and new_set:
            flag = "NEW MATCH"
        elif new_set.issubset(old_set):
            flag = f"NARROWED (kept {len(new_set)}, dropped {len(old_set - new_set)} out-of-scope path(s))"
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
        # the last col is CHANGE (from previous run), overwrite it
        status_col = ws.max_column - 1
        path_col = status_col - 1
        change_col = ws.max_column
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
    print("SUMMARY OF CHANGES vs. (7) workbook")
    print("=" * 70)
    for k, v in sorted(overall.items()):
        print(f"  {k[0]:<32} {k[1]:<40} {v}")


if __name__ == "__main__":
    main()
