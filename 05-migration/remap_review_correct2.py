"""Remap REVIEW TRUE ticks correctly.

Review layout:
  header row for each NOT FOUND (sheet + main_row + company + combine)
  candidate folders with paths (SELECT TRUE = this folder is the right one)
  extra row with TRUE + path when the right folder was not in the candidate list
    (often blank SHEET/MAIN_ROW; COMPANY filled)

Do NOT attach a TRUE path to the previous MAIN_ROW when COMPANY is a different firm.
Match those added TRUE rows to NOT FOUND rows by company (+ year/month when possible).
Optionally look up remaining names in the two file-list dumps.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx"
REVIEW = ROOT / "NOT FOUND - REVIEW - ALL COMPLETED.xlsx"
LISTINGS = [
    ROOT / "CHAT_EXPORT" / "source_lists" / "all_files_list (2).txt",
    ROOT / "CHAT_EXPORT" / "source_lists" / "all_files_list_2025_26.txt",
]
OUT = Path(__file__).resolve().parent / "REVIEW_RESOLVED_CORRECT.xlsx"

TRUE_LIKE = {True, "TRUE", "True", "true", "X", "x", "Y", "y", "1", 1, 1.0}
YEAR_RE = re.compile(r"(20\d{2})-(20\d{2}|\d{2})")
MONTHS3 = {"JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"}
DATE_RE = re.compile(r"(?:^|[^\d])(\d{1,2})[./-](\d{1,2})[./-]((?:20)?\d{2})")
CO_PREFIXES = ("E:\\BACK UP FOLDER", "E:\\2025-26\\co")
OS_PREFIXES = ("F:\\", "E:\\2025-26\\os")
STOP = {"PRIVATE", "LIMITED", "LTD", "PVT", "OPC", "AND", "THE", "OF", "INDIA"}


def blank(val) -> bool:
    if val is None:
        return True
    if isinstance(val, float) and pd.isna(val):
        return True
    return str(val).strip() == ""


def is_true(val) -> bool:
    if val is True:
        return True
    if val is False or val is None:
        return False
    return str(val).strip().upper() in {"TRUE", "X", "Y", "1"} or val in TRUE_LIKE


def company_key(name) -> str:
    if blank(name):
        return ""
    s = str(name).upper()
    s = s.replace("PRIVATELIMITED", "PRIVATE LIMITED")
    s = s.replace("PRIVATELTD", "PRIVATE LTD")
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace(" PRIVATE LIMITED", " PVT LTD")
    s = s.replace(" LIMITED", " LTD")
    for cut in (
        " ARUN KUMAR CASES",
        " ARUNKUMAR CASES",
        " OTHER COM DI KYC",
        " OTHER COM DI APPLY",
        " OTHER COM DI K YC",
    ):
        if s.endswith(cut):
            s = s[: -len(cut)].strip()
    return s


def tokens_norm(name) -> tuple[str, ...]:
    out = []
    for t in company_key(name).split():
        if t in {"PVT", "LTD", "OPC", "AND", "THE"}:
            continue
        t = t.replace("0", "O")
        if len(t) > 4 and t.endswith("S"):
            t = t[:-1]
        if t in {"CENTRE", "CENTER"}:
            t = "CENTER"
        if t in {"ADVANCE", "ADVANCED"}:
            t = "ADVANCE"
        if t in {"CORPORATION", "CORPORATED"}:
            t = "CORPORATION"
        if t in {"ENTERPRISE", "ENTERPRISES"}:
            t = "ENTERPRISE"
        if t in {"MOTOR", "MOTORS"}:
            t = "MOTOR"
        out.append(t)
    return tuple(out)


def canonical_year(text) -> str | None:
    if blank(text):
        return None
    m = YEAR_RE.search(str(text).strip())
    if not m:
        return None
    start, end = m.group(1), m.group(2)
    if len(end) == 4:
        end = end[-2:]
    return f"{start}-{end}"


def year_from_combine(combine) -> str | None:
    if blank(combine):
        return None
    for p in re.split(r"\s*>\s*", str(combine).strip()):
        y = canonical_year(p)
        if y:
            return y
    return canonical_year(combine)


def month_code(text) -> str | None:
    if blank(text):
        return None
    alpha = re.sub(r"[^A-Z]", "", str(text).upper())
    if len(alpha) >= 3 and alpha[:3] in MONTHS3:
        return alpha[:3]
    return None


def year_from_date_text(text) -> str | None:
    if blank(text):
        return None
    best = None
    for m in DATE_RE.finditer(str(text)):
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        month = b if b <= 12 else a
        year = y if y >= 100 else y + 2000
        if month >= 4:
            fy = f"{year}-{str(year + 1)[-2:]}"
        else:
            fy = f"{year - 1}-{str(year)[-2:]}"
        best = fy
    return best


def month_from_text(*texts) -> str | None:
    for t in texts:
        if blank(t):
            continue
        m = month_code(t)
        if m:
            return m
        for part in str(t).replace("/", "\\").split("\\"):
            m = month_code(part)
            if m:
                return m
    return None


def year_from_path_or_name(path, name) -> str | None:
    for src in (path, name):
        y = canonical_year(src)
        if y:
            return y
    for src in (path, name):
        y = year_from_date_text(src)
        if y:
            return y
    return None


def style_sheet(ws):
    ws.freeze_panes = "A2"
    if ws.max_row >= 1 and ws.max_column >= 1:
        ws.auto_filter.ref = ws.dimensions
    header = Font(bold=True, color="FFFFFF")
    fill = PatternFill("solid", fgColor="1F4E79")
    wrap = Alignment(wrap_text=True, vertical="center")
    for cell in ws[1]:
        cell.font = header
        cell.fill = fill
        cell.alignment = wrap
    for col in ws.columns:
        letter = get_column_letter(col[0].column)
        maxlen = 12
        for cell in col[:50]:
            if cell.value is None:
                continue
            maxlen = min(max(maxlen, len(str(cell.value))), 60)
        ws.column_dimensions[letter].width = maxlen


def load_review_rows() -> list[dict]:
    wb = load_workbook(REVIEW, read_only=True, data_only=True)
    ws = wb["REVIEW"]
    rows = []
    empty_streak = 0
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if i == 1:
            continue
        vals = list(row[:8]) + [None] * 8
        sheet, main_row, company, combine, select, cand_name, cand_path, notes = vals[:8]
        content_empty = all(
            blank(v) for v in (sheet, main_row, company, combine, cand_name, cand_path, notes)
        )
        if content_empty:
            empty_streak += 1
            if empty_streak >= 20 and i > 50:
                break
            continue
        empty_streak = 0
        main = None
        if not blank(main_row):
            try:
                main = int(float(main_row))
            except Exception:
                main = None
        rows.append(
            {
                "review_row": i,
                "sheet": None if blank(sheet) else str(sheet).strip(),
                "main_row": main,
                "company": None if blank(company) else str(company).strip(),
                "combine": None if blank(combine) else str(combine).strip(),
                "select": select,
                "select_true": is_true(select),
                "candidate_name": None if blank(cand_name) else str(cand_name).strip(),
                "candidate_path": None if blank(cand_path) else str(cand_path).strip(),
                "notes": None if blank(notes) else str(notes).strip(),
                "headerish": (not blank(notes) and "candidate" in str(notes).lower()),
            }
        )
    wb.close()
    return rows


def load_sheet1_notes() -> list[dict]:
    wb = load_workbook(REVIEW, read_only=True, data_only=True)
    if "Sheet1" not in wb.sheetnames:
        wb.close()
        return []
    ws = wb["Sheet1"]
    out = []
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        vals = list(row[:8])
        if all(blank(v) for v in vals):
            continue
        out.append(
            {
                "sheet1_row": i,
                "sheet": vals[0],
                "main_row": vals[1],
                "company_or_note": vals[2],
                "combine": vals[3],
                "select": vals[4],
                "name": vals[5],
                "path": vals[6],
                "notes": vals[7] if len(vals) > 7 else None,
            }
        )
    wb.close()
    return out


def load_not_found() -> list[dict]:
    nf = []

    cw = pd.read_excel(FINAL, sheet_name="COMPANY WISE", dtype=object)
    cw["COMPANY NAME"] = cw["COMPANY NAME"].ffill()
    for i, r in cw.iterrows():
        status = str(r.get("STATUS") or "").strip().upper()
        if not (status.startswith("NOT FOUND") or status.startswith("NOT ON BACKUP")):
            continue
        company = r.get("COMPANY NAME")
        combine = r.get("COMBINE")
        excel_row = int(i) + 2
        nf.append(
            {
                "source_sheet": "COMPANY WISE",
                "excel_row": excel_row,
                "company": None if blank(company) else str(company).strip(),
                "combine": None if blank(combine) else str(combine).strip(),
                "year": year_from_combine(combine),
                "month": month_from_text(combine),
                "orig": {str(c): r.get(c) for c in cw.columns},
            }
        )

    uf = pd.read_excel(FINAL, sheet_name="UPLOADED FORMS - COMPANY NAME", dtype=object)
    for i, r in uf.iterrows():
        status = str(r.get("STATUS") or "").strip().upper()
        if not (status.startswith("NOT FOUND") or status.startswith("NOT ON BACKUP")):
            continue
        company = r.get("COMPANY NAME")
        year_v = r.get("YEAR")
        mo = r.get("MONTH")
        ft = None
        for c in uf.columns:
            cu = str(c).strip().upper()
            if cu in {"FOLDER", "FOLDER TYPE", "TYPE"} and ft is None:
                ft = r.get(c)
            if cu in {"YEAR", "FY", "FINANCIAL YEAR"} and blank(year_v):
                year_v = r.get(c)
        combine_parts = [p for p in (year_v, mo, ft) if not blank(p)]
        combine = " > ".join(str(p).strip() for p in combine_parts) if combine_parts else None
        excel_row = int(i) + 2
        nf.append(
            {
                "source_sheet": "UPLOADED FORMS - COMPANY NAME",
                "excel_row": excel_row,
                "company": None if blank(company) else str(company).strip(),
                "combine": combine,
                "year": year_from_combine(combine) or canonical_year(year_v),
                "month": month_from_text(combine, mo),
                "orig": {str(c): r.get(c) for c in uf.columns},
            }
        )
    return nf


def significant_tokens(name: str) -> list[str]:
    return [t for t in company_key(name).split() if len(t) >= 3 and t not in STOP and not t.isdigit()]


def build_dir_index():
    dirs = set()
    for p in LISTINGS:
        if not p.is_file():
            continue
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("=====") or line.startswith("-----"):
                    continue
                if not (
                    line.startswith("E:\\BACK UP FOLDER\\")
                    or line.startswith("E:\\2025-26\\co\\")
                    or line.startswith("E:\\2025-26\\os\\")
                    or (
                        line.startswith("F:\\")
                        and not line.startswith("F:\\System Volume Information")
                        and not line.startswith("F:\\$RECYCLE.BIN")
                    )
                    or line.startswith("E:\\NOT IN BACKUP\\")
                ):
                    continue
                parts = line.split("\\")
                for i in range(2, len(parts)):
                    dirs.add("\\".join(parts[:i]))

    by_year_month = defaultdict(list)
    by_year = defaultdict(list)
    all_dirs = []
    seen_ym = defaultdict(set)
    seen_y = defaultdict(set)
    seen_all = set()
    for d in dirs:
        parts = d.split("\\")
        name = parts[-1]
        y = canonical_year(d)
        m3 = None
        for part in parts:
            m3 = month_code(part) or m3
        if d.lower() not in seen_all:
            seen_all.add(d.lower())
            all_dirs.append((d, name, y, m3))
        if y:
            if d.lower() not in seen_y[y]:
                seen_y[y].add(d.lower())
                by_year[y].append((d, name))
            if m3 and d.lower() not in seen_ym[(y, m3)]:
                seen_ym[(y, m3)].add(d.lower())
                by_year_month[(y, m3)].append((d, name))
    return by_year_month, by_year, all_dirs


def listing_matches(company, year, combine, by_ym, by_y, all_dirs, limit=12):
    toks = significant_tokens(company or "")
    if len(toks) < 1:
        return []
    want = tokens_norm(company)
    m3 = None
    ft = ""
    if combine:
        parts = [p.strip() for p in re.split(r"\s*>\s*", combine) if p.strip()]
        for p in parts:
            m3 = month_code(p) or m3
            if str(p).upper().startswith("CO") or str(p).upper().startswith("OS"):
                ft = str(p).upper()
    if year and m3 and (year, m3) in by_ym:
        pool = list(by_ym[(year, m3)])
    elif year and year in by_y:
        pool = list(by_y[year])
    else:
        pool = [(p, n) for p, n, y, m in all_dirs]

    if ft.startswith("CO"):
        pool = [(p, n) for p, n in pool if p.startswith(CO_PREFIXES)]
    elif ft.startswith("OS"):
        pool = [(p, n) for p, n in pool if p.startswith(OS_PREFIXES) or p.startswith("E:\\NOT IN BACKUP")]

    hits = []
    for path, name in pool:
        nt = tokens_norm(name)
        if want and all(t in nt for t in want):
            hits.append((path, name))
            if len(hits) >= limit:
                return hits
    if hits:
        return hits
    for path, name, y, m in all_dirs:
        if year and y and y != year:
            continue
        nt = tokens_norm(name)
        if want and all(t in nt for t in want):
            hits.append((path, name))
            if len(hits) >= limit:
                break
    return hits


def nf_for_company(name, year, month, nf_by_co, nf_by_tok):
    if not name:
        return []
    cands = list(nf_by_co.get(company_key(name), []))
    if not cands:
        cands = list(nf_by_tok.get(tokens_norm(name), []))
    if year:
        year_hits = [x for x in cands if x["year"] == year]
        if year_hits:
            cands = year_hits
    if month:
        month_hits = [x for x in cands if x.get("month") == month]
        if month_hits:
            cands = month_hits
    return cands


def main() -> None:
    review = load_review_rows()
    nf = load_not_found()
    sheet1 = load_sheet1_notes()

    nf_by_key = {(r["source_sheet"], r["excel_row"]): r for r in nf}
    nf_by_co = defaultdict(list)
    nf_by_tok = defaultdict(list)
    for r in nf:
        nf_by_co[company_key(r["company"])].append(r)
        nf_by_tok[tokens_norm(r["company"])].append(r)

    current = {"sheet": None, "main_row": None, "company": None, "combine": None}
    true_hits = []
    groups = defaultdict(lambda: {"rows": [], "true_on_listed": [], "true_added": []})

    for r in review:
        if r["sheet"] and r["main_row"] is not None:
            current = {
                "sheet": r["sheet"],
                "main_row": r["main_row"],
                "company": r["company"] or current["company"],
                "combine": r["combine"] or current["combine"],
            }
        gkey = (current["sheet"], current["main_row"])
        groups[gkey]["rows"].append(r)

        if not r["select_true"] or not r["candidate_path"]:
            continue
        if r["headerish"] and not r["candidate_path"]:
            continue

        ck = company_key(r["company"])
        cur_ck = company_key(current["company"])
        y = year_from_path_or_name(r["candidate_path"], r["candidate_name"]) or year_from_combine(
            r["combine"] or current["combine"]
        )
        mo = month_from_text(r["candidate_path"], r["candidate_name"], r["combine"] or current["combine"])

        same_group = False
        if r["sheet"] and r["main_row"] is not None:
            same_group = True
            how = "TRUE_ON_LISTED_CANDIDATE"
            target_company = r["company"] or current["company"]
        elif ck and cur_ck and ck == cur_ck:
            same_group = True
            how = "TRUE_ADDED_PATH_SAME_GROUP"
            target_company = r["company"] or current["company"]
        elif ck:
            how = "TRUE_ADDED_PATH_FOR_COMPANY"
            target_company = r["company"]
        else:
            how = "TRUE_ADDED_PATH_INHERIT_GROUP"
            same_group = True
            target_company = current["company"]

        rec = {
            "how": how,
            "review_row": r["review_row"],
            "company": target_company,
            "year": y,
            "month": mo,
            "name": r["candidate_name"],
            "path": r["candidate_path"],
            "notes": r["notes"],
            "review_sheet": r["sheet"] or current["sheet"],
            "review_main_row": r["main_row"] if r["main_row"] is not None else current["main_row"],
        }

        targets = []
        key = (current["sheet"], current["main_row"])
        if same_group and key in nf_by_key:
            targets.append(nf_by_key[key])

        extra = nf_for_company(target_company, y, mo, nf_by_co, nf_by_tok)
        seen_t = {(t["source_sheet"], t["excel_row"]) for t in targets}
        for t in extra:
            k = (t["source_sheet"], t["excel_row"])
            if k not in seen_t:
                targets.append(t)
                seen_t.add(k)

        rec["target_keys"] = [(t["source_sheet"], t["excel_row"]) for t in targets]
        true_hits.append(rec)
        if same_group:
            bucket = "true_on_listed" if how == "TRUE_ON_LISTED_CANDIDATE" else "true_added"
            groups[gkey][bucket].append(rec)

    resolved_paths = defaultdict(list)
    for rec in true_hits:
        for key in rec["target_keys"]:
            resolved_paths[key].append(rec)

    print("review_content_rows", len(review))
    print("nf_rows", len(nf))
    print("TRUE+path rows", len(true_hits))
    print("NF keys that got a TRUE path (correct remap)", len(resolved_paths))

    by_year_month, by_year, all_dirs = build_dir_index()
    print("dir_index year-month keys", len(by_year_month), "year keys", len(by_year), "all_dirs", len(all_dirs))

    out_rows = []
    still = []
    listing_only = []
    for item in nf:
        key = (item["source_sheet"], item["excel_row"])
        hits = resolved_paths.get(key, [])
        seen = set()
        uniq = []
        for h in hits:
            p = h["path"].strip().lower()
            if p in seen:
                continue
            seen.add(p)
            uniq.append(h)

        status = "STILL_NO_TRUE"
        if uniq:
            hows = {h["how"] for h in uniq}
            if "TRUE_ON_LISTED_CANDIDATE" in hows:
                status = "RESOLVED_TRUE_ON_LISTED_FOLDER"
            elif "TRUE_ADDED_PATH_SAME_GROUP" in hows:
                status = "RESOLVED_TRUE_ADDED_PATH"
            else:
                status = "RESOLVED_TRUE_ADDED_PATH_MATCHED_BY_COMPANY"

        listing_hits = []
        if status == "STILL_NO_TRUE":
            listing_hits = listing_matches(
                item["company"] or "",
                item["year"],
                item["combine"],
                by_year_month,
                by_year,
                all_dirs,
            )
            if listing_hits:
                status = "NO_TRUE_BUT_NAME_IN_FILE_LIST"

        row = {
            "status": status,
            "source_sheet": item["source_sheet"],
            "excel_row": item["excel_row"],
            "company": item["company"],
            "combine": item["combine"],
            "year": item["year"],
            "n_true_paths": len(uniq),
            "true_how": " | ".join(sorted({h["how"] for h in uniq})),
            "true_review_rows": ";".join(str(h["review_row"]) for h in uniq),
            "resolved_folder_name": " ; ".join(h["name"] or "" for h in uniq),
            "resolved_path": " ; ".join(h["path"] for h in uniq),
            "listing_name_hits": len(listing_hits),
            "listing_paths": " ; ".join(p for p, n in listing_hits),
        }
        for k, v in item["orig"].items():
            row[f"orig_{k}"] = v
        out_rows.append(row)
        if status.startswith("STILL") or status.startswith("NO_TRUE"):
            still.append(row)
        if status == "NO_TRUE_BUT_NAME_IN_FILE_LIST":
            listing_only.append(row)

    df = pd.DataFrame(out_rows)
    counts = df["status"].value_counts().to_dict()
    answers = pd.DataFrame(
        [
            ("final12_NOT_FOUND", len(nf)),
            ("review_content_rows_used", len(review)),
            ("TRUE_plus_path_rows_in_review", len(true_hits)),
            ("NF_resolved_TRUE_on_listed_folder", counts.get("RESOLVED_TRUE_ON_LISTED_FOLDER", 0)),
            ("NF_resolved_TRUE_added_path_same_group", counts.get("RESOLVED_TRUE_ADDED_PATH", 0)),
            ("NF_resolved_TRUE_added_path_by_company", counts.get("RESOLVED_TRUE_ADDED_PATH_MATCHED_BY_COMPANY", 0)),
            ("NF_resolved_total", int(df["status"].str.startswith("RESOLVED").sum())),
            ("NF_no_TRUE_but_folder_name_in_file_lists", counts.get("NO_TRUE_BUT_NAME_IN_FILE_LIST", 0)),
            ("NF_still_no_TRUE_and_no_list_hit", counts.get("STILL_NO_TRUE", 0)),
            ("old_wrong_count_was_98_no_TRUE_on_same_MAIN_ROW", 98),
        ],
        columns=["metric", "value"],
    )

    review_like = df[
        [
            "status",
            "source_sheet",
            "excel_row",
            "company",
            "combine",
            "year",
            "true_how",
            "resolved_folder_name",
            "resolved_path",
            "true_review_rows",
            "listing_name_hits",
            "listing_paths",
        ]
    ].copy()
    review_like.insert(
        0,
        "SELECT (X)",
        review_like["status"].str.startswith("RESOLVED").map({True: True, False: False}),
    )

    true_df = pd.DataFrame(true_hits)
    still_df = pd.DataFrame(still)
    list_df = pd.DataFrame(listing_only)
    s1 = pd.DataFrame(sheet1)

    out_path = OUT
    try:
        writer_cm = pd.ExcelWriter(out_path, engine="openpyxl")
        writer_cm.__enter__()
    except PermissionError:
        out_path = Path(__file__).resolve().parent / "REVIEW_RESOLVED_CORRECT2.xlsx"
        writer_cm = pd.ExcelWriter(out_path, engine="openpyxl")
        writer_cm.__enter__()

    writer = writer_cm
    answers.to_excel(writer, sheet_name="ANSWERS", index=False)
    review_like.to_excel(writer, sheet_name="REVIEW_STYLE_RESOLVED", index=False)
    df[df["status"].str.startswith("RESOLVED")].to_excel(writer, sheet_name="RESOLVED_FULL_ROWS", index=False)
    still_df.to_excel(writer, sheet_name="STILL_OPEN_FULL_ROWS", index=False)
    list_df.to_excel(writer, sheet_name="NO_TRUE_BUT_IN_FILE_LIST", index=False)
    true_df.to_excel(writer, sheet_name="ALL_TRUE_PATH_ROWS", index=False)
    s1.to_excel(writer, sheet_name="REVIEW_SHEET1_NOTES", index=False)
    pd.DataFrame(sorted(counts.items()), columns=["status", "n"]).to_excel(
        writer, sheet_name="COUNTS", index=False
    )
    for ws in writer.sheets.values():
        style_sheet(ws)
    writer.__exit__(None, None, None)

    print("wrote", out_path)
    print(answers.to_string(index=False))
    print("status_counts", counts)


if __name__ == "__main__":
    main()
