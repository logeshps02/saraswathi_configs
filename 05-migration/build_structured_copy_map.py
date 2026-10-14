"""Build a structured copy map from (12) + REVIEW TRUE ticks. Does not copy files."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re
import sys

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx"
REVIEW = ROOT / "NOT FOUND - REVIEW - ALL COMPLETED.xlsx"
OUT_XLSX = Path(__file__).resolve().parent / "STRUCTURED_COPY_MAP.xlsx"
OUT_CSV = Path(__file__).resolve().parent / "STRUCTURED_COPY_MAP.csv"

YEAR_RE = re.compile(r"(\d{4})-(\d{2,4})")
INVALID_STATUS = ("NOT FOUND", "NOT ON BACKUP", "SKIPPED")
TRUE_LIKE = {True, "TRUE", "True", "true", "X", "x", "Y", "y", "1", 1, 1.0}


def sanitize(name: object) -> str:
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return "(unknown)"
    s = str(name).strip()
    s = re.sub(r'[<>:"/\\|?*\r\n\t]', " ", s)
    s = re.sub(r"\s+", " ", s).strip().rstrip(". ")
    if len(s) > 180:
        s = s[:180].rstrip(". ")
    return s or "(unknown)"


def canonical_year(text: object) -> str | None:
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return None
    m = YEAR_RE.search(str(text).strip())
    if not m:
        return None
    start, end = m.group(1), m.group(2)
    if len(end) == 4:
        end = end[-2:]
    return f"{start}-{end}"


def year_from_combine(combine: object) -> str | None:
    if combine is None or (isinstance(combine, float) and pd.isna(combine)):
        return None
    parts = re.split(r"\s*>\s*", str(combine).strip())
    for p in parts:
        y = canonical_year(p)
        if y:
            return y
    return canonical_year(combine)


def year_from_path(path: str) -> str | None:
    # Prefer FY tokens like 2018-19 or 2018-2019 in the path
    m = re.search(r"(20\d{2})-(20\d{2}|\d{2})", path)
    if m:
        return canonical_year(m.group(0))
    return None


def split_paths(val: object) -> list[str]:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return []
    text = str(val).strip()
    if not text:
        return []
    parts = [p.strip() for p in text.split(" ; ") if p.strip()]
    if len(parts) == 1 and ";" in text:
        parts = [p.strip() for p in text.split(";") if p.strip()]
    return parts


def status_ok(status: object) -> bool:
    s = str(status or "").strip()
    if not s:
        return False
    return not any(s.upper().startswith(p) for p in INVALID_STATUS)


def is_true(val: object) -> bool:
    if val is True:
        return True
    if val is False or val is None:
        return False
    return str(val).strip() in TRUE_LIKE or str(val).strip().upper() in {"TRUE", "X", "Y", "1"}


def blank(val: object) -> bool:
    if val is None:
        return True
    if isinstance(val, float) and pd.isna(val):
        return True
    return str(val).strip() == ""


def company_key(name: object) -> str:
    if blank(name):
        return ""
    s = str(name).upper()
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace(" PRIVATE LIMITED", " PVT LTD")
    s = s.replace(" LIMITED", " LTD")
    return s


def folder_name(src: str) -> str:
    p = src.rstrip("\\/")
    name = p.split("\\")[-1] if "\\" in p else p.split("/")[-1]
    return sanitize(name)


def company_in_path(company: str, src: str) -> bool:
    ck = company_key(company)
    pk = company_key(src)
    if not ck or len(ck) < 8:
        return True
    tokens = [t for t in ck.split() if t not in {"PVT", "LTD", "PRIVATE", "LIMITED", "OPC", "AND", "THE"}]
    if not tokens:
        return True
    hit = sum(1 for t in tokens if t in pk)
    return hit >= max(1, min(3, len(tokens) // 2))


def add_row(rows: list[dict], **kw) -> None:
    rows.append(kw)


def collect_final() -> tuple[list[dict], dict]:
    rows: list[dict] = []
    nf_index: dict[tuple, dict] = {}
    xl = pd.ExcelFile(FINAL)

    # COMPANY WISE
    cw = pd.read_excel(FINAL, sheet_name="COMPANY WISE", dtype=object)
    cw["COMPANY_FF"] = cw["COMPANY NAME"].ffill()
    for i, r in cw.iterrows():
        excel_row = int(i) + 2
        company = r["COMPANY_FF"]
        combine = r["COMBINE"]
        status = r["STATUS"]
        year = year_from_combine(combine)
        rec = {
            "source_sheet": "COMPANY WISE",
            "excel_row": excel_row,
            "company": None if blank(company) else str(company).strip(),
            "combine": None if blank(combine) else str(combine).strip(),
            "year": year,
            "status": None if blank(status) else str(status).strip(),
        }
        if str(status or "").upper().startswith("NOT FOUND"):
            nf_index[("COMPANY WISE", excel_row)] = rec
            continue
        if not status_ok(status):
            continue
        for src in split_paths(r["MATCHED PATH"]):
            add_row(
                rows,
                origin="FINAL",
                source_sheet="COMPANY WISE",
                excel_row=excel_row,
                company=rec["company"],
                combine=rec["combine"],
                year=year or year_from_path(src),
                status=rec["status"],
                source_path=src,
                select_true=None,
                review_kind="final_mapped",
            )

    # UPLOADED FORMS
    uf = pd.read_excel(FINAL, sheet_name="UPLOADED FORMS - COMPANY NAME", dtype=object)
    for i, r in uf.iterrows():
        excel_row = int(i) + 2
        company = r["COMPANY NAME"]
        combine = r["COMBINE"]
        status = r["STATUS"]
        year = canonical_year(r.get("YEAR")) or year_from_combine(combine)
        rec = {
            "source_sheet": "UPLOADED FORMS - COMPANY NAME",
            "excel_row": excel_row,
            "company": None if blank(company) else str(company).strip(),
            "combine": None if blank(combine) else str(combine).strip(),
            "year": year,
            "status": None if blank(status) else str(status).strip(),
        }
        if str(status or "").upper().startswith("NOT FOUND"):
            nf_index[("UPLOADED FORMS - COMPANY NAME", excel_row)] = rec
            continue
        if not status_ok(status):
            continue
        for src in split_paths(r["MATCHED PATH"]):
            add_row(
                rows,
                origin="FINAL",
                source_sheet="UPLOADED FORMS - COMPANY NAME",
                excel_row=excel_row,
                company=rec["company"],
                combine=rec["combine"]
                or (
                    " > ".join(
                        str(x).strip()
                        for x in (r.get("YEAR"), r.get("MONTH"), r.get("FOLDER"))
                        if not blank(x)
                    )
                    or None
                ),
                year=year or year_from_path(src),
                status=rec["status"],
                source_path=src,
                select_true=None,
                review_kind="final_mapped",
            )

    # DIN FORMS (header on row 2)
    din = pd.read_excel(FINAL, sheet_name="DIN FORMS", header=1, dtype=object)
    for i, r in din.iterrows():
        excel_row = int(i) + 3
        if not status_ok(r.get("STATUS")):
            continue
        name = r.get("NAME")
        folder = r.get("FOLDER")
        year = year_from_combine(folder)
        for src in split_paths(r.get("MATCHED PATH")):
            add_row(
                rows,
                origin="FINAL",
                source_sheet="DIN FORMS",
                excel_row=excel_row,
                company=None if blank(name) else str(name).strip(),
                combine=None if blank(folder) else str(folder).strip(),
                year=year or year_from_path(src),
                status=str(r.get("STATUS")).strip(),
                source_path=src,
                select_true=None,
                review_kind="final_mapped",
            )

    # LEI AND OTHERS
    lei = pd.read_excel(FINAL, sheet_name="LEI AND OTHERS", dtype=object)
    for i, r in lei.iterrows():
        excel_row = int(i) + 2
        if not status_ok(r.get("STATUS")):
            continue
        name = r.get("NAME")
        folder = r.get("FOLDER")
        year = year_from_combine(folder)
        for src in split_paths(r.get("MATCHED PATH")):
            add_row(
                rows,
                origin="FINAL",
                source_sheet="LEI AND OTHERS",
                excel_row=excel_row,
                company=None if blank(name) else str(name).strip(),
                combine=None if blank(folder) else str(folder).strip(),
                year=year or year_from_path(src),
                status=str(r.get("STATUS")).strip(),
                source_path=src,
                select_true=None,
                review_kind="final_mapped",
            )

    return rows, nf_index


def stream_review() -> list[dict]:
    wb = load_workbook(REVIEW, read_only=True, data_only=True)
    ws = wb["REVIEW"]
    out = []
    empty_streak = 0
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if i == 1:
            continue
        vals = list(row[:8]) + [None] * 8
        sheet, main_row, company, combine, select, cand_name, cand_path, notes = vals[:8]
        content_empty = all(blank(v) for v in (sheet, main_row, company, combine, cand_name, cand_path, notes))
        if content_empty:
            empty_streak += 1
            if empty_streak >= 30 and i > 100:
                break
            continue
        empty_streak = 0
        out.append(
            {
                "review_row": i,
                "sheet": None if blank(sheet) else str(sheet).strip(),
                "main_row": None if blank(main_row) else int(float(main_row)),
                "company": None if blank(company) else str(company).strip(),
                "combine": None if blank(combine) else str(combine).strip(),
                "select": select,
                "candidate_name": None if blank(cand_name) else str(cand_name).strip(),
                "candidate_path": None if blank(cand_path) else str(cand_path).strip(),
                "notes": None if blank(notes) else str(notes).strip(),
            }
        )
    wb.close()
    return out


def collect_review(nf_index: dict) -> tuple[list[dict], list[dict], dict, list[dict]]:
    mapped: list[dict] = []
    unresolved_true: list[dict] = []
    true_by_nf: dict[tuple, int] = defaultdict(int)

    last = {
        "sheet": None,
        "main_row": None,
        "company": None,
        "combine": None,
    }

    review_rows = stream_review()
    for r in review_rows:
        if r["sheet"] and r["main_row"] is not None:
            last["sheet"] = r["sheet"]
            last["main_row"] = r["main_row"]
            if r["company"]:
                last["company"] = r["company"]
            if r["combine"]:
                last["combine"] = r["combine"]
        elif r["company"] and not r["sheet"]:
            # keep last sheet/main; company may be same
            if last["company"] and company_key(r["company"]) != company_key(last["company"]):
                # new company without sheet — still inherit last sheet/main if same group spacer
                pass
            if r["combine"]:
                last["combine"] = r["combine"]
            if r["company"]:
                last["company"] = r["company"]

        if not is_true(r["select"]):
            continue
        if not r["candidate_path"]:
            continue

        sheet = r["sheet"] or last["sheet"]
        main_row = r["main_row"] if r["main_row"] is not None else last["main_row"]
        company = r["company"] or last["company"]
        combine = r["combine"] or last["combine"]
        kind = "review_true_candidate" if r["sheet"] and r["main_row"] is not None else "review_true_manual"

        nf = nf_index.get((sheet, main_row)) if sheet and main_row is not None else None
        if nf:
            company = company or nf["company"]
            combine = combine or nf["combine"]
            year = nf["year"] or year_from_combine(combine) or year_from_path(r["candidate_path"])
            true_by_nf[(sheet, main_row)] += 1
        else:
            year = year_from_combine(combine) or year_from_path(r["candidate_path"])
            if kind == "review_true_manual" and sheet and main_row is not None:
                pass
            elif not nf and kind == "review_true_manual":
                # still usable if company+year exist
                pass

        rec = {
            "origin": "REVIEW_TRUE",
            "source_sheet": sheet or "REVIEW_MANUAL",
            "excel_row": main_row,
            "review_row": r["review_row"],
            "company": company,
            "combine": combine,
            "year": year,
            "status": "NOT FOUND -> TRUE",
            "source_path": r["candidate_path"],
            "select_true": True,
            "review_kind": kind,
            "candidate_name": r["candidate_name"],
        }
        if not company:
            unresolved_true.append(rec)
            continue
        mapped.append(rec)

    return mapped, unresolved_true, true_by_nf, review_rows


def build_dest(rows: list[dict]) -> list[dict]:
    used_dest: dict[str, str] = {}
    out = []
    for rec in rows:
        company = rec.get("company") or "(unknown)"
        year = rec.get("year") or "UNKNOWN-YEAR"
        src = rec["source_path"]
        dest_company = sanitize(company)
        dest_year = sanitize(year)
        base = folder_name(src)
        rel = f"{dest_company}\\{dest_year}\\{base}"
        key = rel.lower()
        if key in used_dest and used_dest[key].lower() != src.lower():
            n = 2
            while True:
                rel2 = f"{dest_company}\\{dest_year}\\{base} ({n})"
                if rel2.lower() not in used_dest or used_dest[rel2.lower()].lower() == src.lower():
                    rel = rel2
                    key = rel.lower()
                    break
                n += 1
            rec = dict(rec)
            rec["dest_collision"] = True
        else:
            rec = dict(rec)
            rec["dest_collision"] = rec.get("dest_collision", False)
        used_dest[key] = src
        rec["dest_company"] = dest_company
        rec["dest_year"] = dest_year
        rec["dest_folder"] = rel.split("\\")[-1]
        rec["dest_relative"] = rel
        warnings = []
        if not rec.get("year"):
            warnings.append("missing_year")
        if rec["dest_year"] == "UNKNOWN-YEAR":
            warnings.append("unknown_year")
        if not company_in_path(company, src):
            warnings.append("company_name_weak_in_source_path")
        if rec.get("dest_collision"):
            warnings.append("dest_name_collision_renamed")
        if rec.get("review_kind") == "review_true_manual":
            warnings.append("manual_typed_path")
        rec["warnings"] = "; ".join(warnings)
        out.append(rec)
    return out


def dedupe(rows: list[dict]) -> list[dict]:
    seen = {}
    out = []
    for rec in rows:
        key = (rec.get("company") or "").strip().upper(), (rec.get("year") or ""), rec["source_path"].strip().lower()
        if key in seen:
            seen[key]["duplicate_of"] = True
            continue
        rec = dict(rec)
        rec["duplicate_of"] = False
        seen[key] = rec
        out.append(rec)
    return out


def write_outputs(copy_rows: list[dict], nf_index: dict, true_by_nf: dict, unresolved_true: list[dict], extra_notes: list[str]) -> None:
    df = pd.DataFrame(copy_rows)
    cols = [
        "dest_relative",
        "dest_company",
        "dest_year",
        "dest_folder",
        "source_path",
        "origin",
        "review_kind",
        "source_sheet",
        "excel_row",
        "review_row",
        "company",
        "combine",
        "year",
        "status",
        "warnings",
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = None
    df = df[cols]
    df = df.sort_values(["dest_company", "dest_year", "dest_folder", "source_path"], kind="stable")

    unresolved = []
    for key, rec in nf_index.items():
        if true_by_nf.get(key, 0) == 0:
            unresolved.append(
                {
                    "source_sheet": rec["source_sheet"],
                    "excel_row": rec["excel_row"],
                    "company": rec["company"],
                    "combine": rec["combine"],
                    "year": rec["year"],
                    "status": rec["status"],
                    "true_ticks": 0,
                    "note": "NOT FOUND in final sheet and no TRUE path in review",
                }
            )
    nf_df = pd.DataFrame(unresolved)
    warn_df = df[df["warnings"].fillna("").str.len() > 0].copy()
    unresolved_true_df = pd.DataFrame(unresolved_true) if unresolved_true else pd.DataFrame()

    summary_rows = [
        ("final_workbook", str(FINAL.name)),
        ("review_workbook", str(REVIEW.name)),
        ("copy_rows_after_dedupe", len(df)),
        ("unique_companies", int(df["dest_company"].nunique())),
        ("unique_company_year", int(df.groupby(["dest_company", "dest_year"]).ngroups)),
        ("from_final", int((df["origin"] == "FINAL").sum())),
        ("from_review_true", int((df["origin"] == "REVIEW_TRUE").sum())),
        ("review_true_manual", int((df["review_kind"] == "review_true_manual").sum())),
        ("review_true_candidate", int((df["review_kind"] == "review_true_candidate").sum())),
        ("rows_with_warnings", int(len(warn_df))),
        ("nf_rows_still_unresolved", int(len(nf_df))),
        ("true_rows_missing_company", int(len(unresolved_true_df))),
        ("dest_layout", r"<COMPANY>\<YEAR>\<original-folder-name>"),
        ("note", "This file is a plan only. No files were copied."),
    ]
    for n in extra_notes:
        summary_rows.append(("note", n))
    sum_df = pd.DataFrame(summary_rows, columns=["metric", "value"])

    with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="COPY_MAP", index=False)
        sum_df.to_excel(writer, sheet_name="SUMMARY", index=False)
        warn_df.to_excel(writer, sheet_name="WARNINGS", index=False)
        if len(nf_df):
            nf_df.sort_values(["source_sheet", "company", "excel_row"]).to_excel(
                writer, sheet_name="UNRESOLVED_NOT_FOUND", index=False
            )
        if len(unresolved_true_df):
            unresolved_true_df.to_excel(writer, sheet_name="TRUE_UNLINKED", index=False)

        # tree sheet: company / year / folder
        tree = (
            df.groupby(["dest_company", "dest_year", "dest_folder", "source_path"], dropna=False)
            .size()
            .reset_index(name="n")
            .drop(columns=["n"])
        )
        tree.to_excel(writer, sheet_name="FOLDER_TREE", index=False)

        ws = writer.sheets["COPY_MAP"]
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        widths = {
            "A": 70,
            "B": 40,
            "C": 12,
            "D": 50,
            "E": 90,
            "F": 14,
            "G": 24,
            "H": 28,
            "K": 40,
            "L": 40,
            "O": 36,
        }
        for col, w in widths.items():
            ws.column_dimensions[col].width = w

    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    return df, nf_df, warn_df


def main() -> None:
    print("Reading final workbook ...", flush=True)
    final_rows, nf_index = collect_final()
    print(f"  final mapped path rows={len(final_rows)}  nf keys={len(nf_index)}", flush=True)

    print("Streaming REVIEW (stop on empty tail) ...", flush=True)
    review_mapped, unresolved_true, true_by_nf, review_rows = collect_review(nf_index)
    print(
        f"  review content rows={len(review_rows)}  TRUE mapped={len(review_mapped)}  TRUE unlinked={len(unresolved_true)}  nf with TRUE={len(true_by_nf)}",
        flush=True,
    )

    all_rows = final_rows + review_mapped
    all_rows = dedupe(all_rows)
    all_rows = build_dest(all_rows)

    extra = [
        "REVIEW TRUE rows with blank SHEET/MAIN_ROW inherit the previous NOT FOUND group (same company).",
        "MULTIPLE MATCHES: each semicolon-separated source folder is its own copy line under the same company\\year.",
        "NOT FOUND rows from the final sheet are included only if SELECT is TRUE in the review workbook.",
    ]
    df, nf_df, warn_df = write_outputs(all_rows, nf_index, true_by_nf, unresolved_true, extra)
    print(f"Wrote {OUT_XLSX}")
    print(f"Wrote {OUT_CSV}")
    print(
        f"copy_rows={len(df)} companies={df['dest_company'].nunique()} "
        f"unresolved_nf={len(nf_df)} warnings={len(warn_df)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
