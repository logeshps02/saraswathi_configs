r"""
Fifth-pass fix: manually re-check every NOT FOUND row against ONLY the files
inside its own specific folder (year > month > CO/OS), tolerating typos
and different forms (LLP, PRIVATELIMITED, spelling errors, glued words).

Bugs discovered from the client's examples:

    DB PLUS LLP -> 2024-25 > JANUARY > OS
        The folder is literally "DB plus form 8", but the previous matcher
        required the token "LLP" to appear (LLP was not in the stopword
        list).  So a legitimate folder got marked NOT FOUND.

    ARUVEE DAIRY AND FOODS PRIVATE LIMITED -> 2020-21 > AUGUST > CO
        The folder is spelled "ARUVEE DIARY..." (typo: I<->A swap).
        Substring match "DAIRY in DIARY" fails.  Need typo tolerance.

    VISUAL SCULPTORS DESIGN SERVICES PRIVATELIMITED
        Company has PRIVATELIMITED glued together as one token.
        Need to split known suffixes (PRIVATELIMITED -> PRIVATE LIMITED).

Fixes applied here:

    1. Expanded stopwords (LLP, LLC, PARTNERS, PARTNERSHIP, GROUP, INC, CORP).
    2. Compound-token splitter (PRIVATELIMITED, PVTLTD, INDIAPRIVATE).
    3. Fuzzy Levenshtein tolerance on token match (allows I<->A swap etc).
    4. STRICT: search ONLY inside the exact month folder for that row.

Only NOT FOUND rows are touched.  Rows that stay NOT FOUND keep their
original status.  A new column "RECHECK (vs 9)" is added:
    SAME       - was NF, still NF
    RECOVERED  - was NF, now FOUND (fuzzy tolerance recovered it)
    RECOVERED (MULTIPLE) - was NF, now multiple candidates found
    RECOVERED (FUZZY)    - matched via Levenshtein tolerance
    RECOVERED (COMPOUND) - matched after splitting compound token

Input : (9).xlsx    Output: (10).xlsx
"""

import openpyxl
import re
from collections import defaultdict

LISTINGS = [
    r"C:\Users\logsarav\Downloads\all_files_list (2).txt",
    r"C:\Users\logsarav\Downloads\all_files_list_2025_26.txt",
]
SRC = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET - WITH PATHS (9).xlsx"
DST = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx"

MONTHS3 = {"JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL",
           "AUG", "SEP", "OCT", "NOV", "DEC"}

# Expanded stopwords — companies commonly append these suffixes.
STOPWORDS = {
    "PRIVATE", "PVT", "LIMITED", "LTD", "COMPANY",
    "THE", "AND", "OF", "FOR", "AT", "IN", "ON", "TO", "BY",
    "OR", "AS", "IS", "IT", "ITS", "AN",
    # NEW:
    "LLP", "LLC", "PARTNERS", "PARTNERSHIP",
    "INC", "CORP", "CORPORATION", "COMPANIES", "CO",
    "INDIA", "INDIAN",  # very generic geographic suffix
    "P", "L",  # shorthand for LTD/LLP e.g. "P LTD"
    "YOU", "U", "UR", "UR",  # casual English shortenings occasionally in folder names
}

# Compound suffixes commonly written without a space.
COMPOUND_SPLITS = [
    ("PRIVATELIMITED", "PRIVATE LIMITED"),
    ("PVTLIMITED",     "PVT LIMITED"),
    ("PVTLTD",         "PVT LTD"),
    ("PVTLIMTED",      "PVT LIMITED"),
    ("PRIVATELTD",     "PRIVATE LTD"),
    ("INDIAPRIVATE",   "INDIA PRIVATE"),
    ("INDIAPVT",       "INDIA PVT"),
    ("INDIALIMITED",   "INDIA LIMITED"),
    ("INDIALTD",       "INDIA LTD"),
    ("PLTD",           "P LTD"),
    ("PLIMITED",       "P LIMITED"),
]

COMMON_EXTRAS = {"OTHER", "OTHERS", "WORKS", "WORK", "FORMS", "EFORMS",
                 "DOCS", "FILES", "DOCUMENTS", "DOCUMENT", "PAPERS",
                 "RECORDS", "DIVISION", "DEPARTMENT", "GROUP", "TYPE",
                 "KIND", "SIR", "MAM", "MADAM", "MR", "MRS", "MISS",
                 "CS", "MISC", "GENERAL", "CASES", "CASE",
                 "NOTE", "NOTES", "COPY", "UPDATE", "REGISTRATION",
                 "STATUS", "REPORT", "MASTER",
                 "WORS",  # observed typo of WORKS
                 }

YEAR_RE = re.compile(r"^\d{4}-(\d{2}|\d{4})$")
CO_PREFIXES = ("E:\\BACK UP FOLDER", "E:\\2025-26\\co")
OS_PREFIXES = ("F:\\", "E:\\2025-26\\os")


# ---------------------------------------------------------------- helpers
def canonicalize(text):
    if not text:
        return ""
    up = str(text).upper()
    # collapse dot-separated initials like A.M.N. -> AMN
    up = re.sub(r"\b((?:[A-Z]+\.){2,})",
                lambda m: " " + m.group(1).replace(".", "") + " ",
                up)
    # collapse space-separated initials (1-2 letter tokens only) like "A M N" or "AR A S"
    # NOTE: length capped at 2 chars to avoid gluing 3-letter English words like
    # AND / YOU / LLP / LTD together into meaningless blobs.
    up = re.sub(r"\b([A-Z]{1,2}(?:\s+[A-Z]{1,2}){1,})\b",
                lambda m: m.group(0).replace(" ", ""),
                up)
    # strip non-alnum
    up = re.sub(r"[^A-Z0-9]+", " ", up).strip()
    # split known compound suffixes
    for glued, split in COMPOUND_SPLITS:
        up = re.sub(r"\b" + glued + r"\b", split, up)
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


def company_sig_tokens(name):
    """Significant tokens (skip stopwords and 1-char tokens)."""
    if not name:
        return []
    canon = canonicalize(name)
    return [t for t in canon.split() if t not in STOPWORDS and len(t) >= 2]


def levenshtein(a, b):
    """Damerau-Levenshtein distance (counts adjacent transpositions as 1 edit).

    Needed to catch typos like DAIRY <-> DIARY (I/A swap), which is a
    distance-2 in plain Levenshtein but distance-1 with Damerau.
    """
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if abs(la - lb) > 3:
        return abs(la - lb)
    # DP table
    INF = la + lb
    d = [[0] * (lb + 2) for _ in range(la + 2)]
    d[0][0] = INF
    for i in range(la + 1):
        d[i + 1][0] = INF
        d[i + 1][1] = i
    for j in range(lb + 1):
        d[0][j + 1] = INF
        d[1][j + 1] = j
    da = {}
    for i in range(1, la + 1):
        db = 0
        for j in range(1, lb + 1):
            k = da.get(b[j - 1], 0)
            l = db
            cost = 0 if a[i - 1] == b[j - 1] else 1
            if cost == 0:
                db = j
            d[i + 1][j + 1] = min(
                d[i][j] + cost,           # substitute
                d[i + 1][j] + 1,          # insert
                d[i][j + 1] + 1,          # delete
                d[k][l] + (i - k - 1) + 1 + (j - l - 1),  # transpose
            )
        da[a[i - 1]] = i
    return d[la + 1][lb + 1]


def fuzzy_tolerance(tok_len):
    """Levenshtein budget by token length."""
    if tok_len <= 3:
        return 0
    if tok_len <= 6:
        return 1
    return 2


def token_matches_strict(tok, canon):
    """Original substring-based match (no fuzzy)."""
    if len(tok) <= 3:
        return tok in canon.split()
    return tok in canon


def token_matches_fuzzy(tok, canon):
    """Fuzzy match: substring OR Levenshtein-close word."""
    if token_matches_strict(tok, canon):
        return True
    tol = fuzzy_tolerance(len(tok))
    if tol == 0:
        return False
    # only consider words within +/-tol of tok length
    for w in canon.split():
        if abs(len(w) - len(tok)) > tol:
            continue
        if levenshtein(tok, w) <= tol:
            return True
    return False


def significant_extras_tokens(extras_parts):
    toks = []
    for e in extras_parts:
        canon = canonicalize(e)
        for t in canon.split():
            if len(t) < 3:
                continue
            if t in STOPWORDS or t in COMMON_EXTRAS:
                continue
            if t not in toks:
                toks.append(t)
    return toks


def path_matches_extras(path, extras_toks):
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
        month_raw = second
        folder_type = parts[2] if len(parts) > 2 else ""
        extras = parts[3:] if len(parts) > 3 else []
    else:
        month_raw = ""
        folder_type = second
        extras = parts[2:] if len(parts) > 2 else []
    if " - " in folder_type:
        head, tail = folder_type.split(" - ", 1)
        extras.insert(0, tail.strip())
        folder_type = head.strip()
    return year, month_raw, folder_type, extras


def filter_by_drive(matches, folder_type):
    if not matches:
        return matches
    ft = (folder_type or "").strip().upper()
    if ft.startswith("CO"):
        return [m for m in matches if m.startswith(CO_PREFIXES)]
    if ft.startswith("OS"):
        return [m for m in matches if m.startswith(OS_PREFIXES)]
    return matches


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

    month_children = defaultdict(list)   # (year, m3) -> [(path, name), ...]
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
def match_fuzzy(candidates, company):
    """Fuzzy: require ALL significant tokens matched (with Levenshtein tolerance)."""
    tokens = company_sig_tokens(company)
    if not tokens:
        return [], "no-sig-tokens"

    hits_strict = []
    hits_fuzzy = []
    for path, name in candidates:
        canon = canonicalize(name)
        if all(token_matches_strict(t, canon) for t in tokens):
            hits_strict.append(path)
        elif all(token_matches_fuzzy(t, canon) for t in tokens):
            hits_fuzzy.append(path)
    return hits_strict, hits_fuzzy


def recheck(company, combine, month_children, year_children):
    """
    Returns (path_str, status, hint) where hint describes HOW it matched:
        'STRICT'    - matched via original substring
        'FUZZY'     - matched via Levenshtein tolerance (typo)
        'COMPOUND'  - matched only after splitting compound token
        'NONE'      - still not found
    """
    parsed = parse_combine(combine)
    if not parsed:
        return "", "NOT FOUND", "NONE"
    year, month_raw, folder_type, extras = parsed
    extras_toks = significant_extras_tokens(extras)
    m3 = month_code(month_raw)

    def refine(hits):
        if extras_toks:
            hits = [h for h in hits if path_matches_extras(h, extras_toks)]
        hits = filter_by_drive(hits, folder_type)
        return sorted(set(hits))

    if m3:
        candidates = month_children.get((year, m3), [])
        scope = f"{year}/{m3}"
    else:
        candidates = year_children.get(year, [])
        scope = f"{year}(year-only)"

    if not candidates:
        return "", f"NOT FOUND (no folder for {scope})", "NONE"

    for variant in company_name_variants(company):
        strict, fuzzy = match_fuzzy(candidates, variant)
        strict = refine(strict)
        fuzzy = refine(fuzzy)
        if strict:
            if len(strict) == 1:
                return strict[0], "FOUND" + ("" if m3 else " (YEAR-ONLY)"), "STRICT"
            return " ; ".join(strict[:5]), f"MULTIPLE MATCHES ({len(strict)})", "STRICT"
        if fuzzy:
            if len(fuzzy) == 1:
                return fuzzy[0], "FOUND (fuzzy)" + ("" if m3 else " (YEAR-ONLY)"), "FUZZY"
            return " ; ".join(fuzzy[:5]), f"MULTIPLE MATCHES (fuzzy) ({len(fuzzy)})", "FUZZY"

    return "", "NOT FOUND", "NONE"


# ---------------------------------------------------------------- main
def process_sheet(ws, path_col, status_col, header_row, sname,
                  month_children, year_children, recheck_col):
    current_company = None
    stats = defaultdict(int)
    ws.cell(row=header_row, column=recheck_col, value="RECHECK (vs 9)")

    for r in range(header_row + 1, ws.max_row + 1):
        # forward-fill for COMPANY WISE
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

        status = str(ws.cell(row=r, column=status_col).value or "").strip()
        if not status.upper().startswith("NOT FOUND"):
            ws.cell(row=r, column=recheck_col, value="")  # untouched
            stats["untouched"] += 1
            continue

        new_path, new_status, hint = recheck(company, combine, month_children, year_children)

        if new_path:
            ws.cell(row=r, column=path_col, value=new_path)
            ws.cell(row=r, column=status_col, value=new_status)
            if hint == "STRICT":
                flag = "RECOVERED (missed by prev pass)"
                stats["recovered_strict"] += 1
            elif hint == "FUZZY":
                flag = "RECOVERED (fuzzy — typo tolerance)"
                stats["recovered_fuzzy"] += 1
            else:
                flag = f"RECOVERED ({hint})"
                stats["recovered_other"] += 1
            if "MULTIPLE" in new_status:
                flag += " [MULTIPLE]"
            ws.cell(row=r, column=recheck_col, value=flag)
        else:
            ws.cell(row=r, column=recheck_col, value="STILL NOT FOUND")
            stats["still_nf"] += 1

    return stats


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
        ("LEI AND OTHERS", 1),
    ]

    for sname, header_row in sheets_config:
        if sname not in wb.sheetnames:
            continue
        ws = wb[sname]
        # in (9): last col = CHANGE (vs 8), 2nd-last = STATUS, 3rd-last = PATH
        # append new column at max_column+1 for RECHECK (vs 9)
        change_col = ws.max_column          # CHANGE (vs 8)
        status_col = change_col - 1         # STATUS
        path_col   = status_col - 1         # MATCHED PATH
        recheck_col = change_col + 1        # NEW column

        print(f"Processing '{sname}' ({ws.max_row - header_row} rows) ...", flush=True)
        st = process_sheet(ws, path_col, status_col, header_row, sname,
                           month_children, year_children, recheck_col)
        print(f"  stats: {dict(st)}")
        for k, v in st.items():
            overall[(sname, k)] += v

    print("Saving ...")
    wb.save(DST)
    print("Saved:", DST)

    print()
    print("=" * 70)
    print("SUMMARY: NOT FOUND recheck vs. (9) workbook")
    print("=" * 70)
    for k, v in sorted(overall.items()):
        print(f"  {k[0]:<32} {k[1]:<40} {v}")


if __name__ == "__main__":
    main()
