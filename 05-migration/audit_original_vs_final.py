"""Compare the two original workbooks against STRUCTURED_COPY_MAP_FINAL."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re
import sys

import pandas as pd
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx"
REVIEW = ROOT / "NOT FOUND - REVIEW - ALL COMPLETED.xlsx"
MAP = Path(__file__).resolve().parent / "STRUCTURED_COPY_MAP_FINAL.csv"
OUT = Path(__file__).resolve().parent / "COVERAGE_AUDIT.xlsx"

TRUE_LIKE = {True, "TRUE", "True", "true", "X", "x", "Y", "y", "1", 1, 1.0}
INVALID_STATUS = ("NOT FOUND", "NOT ON BACKUP", "SKIPPED")


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
    return str(val).strip() in TRUE_LIKE or str(val).strip().upper() in {"TRUE", "X", "Y", "1"}


def split_paths(val) -> list[str]:
    if blank(val):
        return []
    text = str(val).strip()
    parts = [p.strip() for p in text.split(" ; ") if p.strip()]
    if len(parts) == 1 and ";" in text:
        parts = [p.strip() for p in text.split(";") if p.strip()]
    return parts


def status_bucket(status) -> str:
    s = str(status or "").strip().upper()
    if not s:
        return "BLANK"
    if s.startswith("NOT FOUND") or s.startswith("NOT ON BACKUP"):
        return "NOT_FOUND"
    if s.startswith("SKIPPED"):
        return "SKIPPED"
    if s.startswith("FOUND") or s.startswith("MULTIPLE") or "FUZZY" in s or "YEAR" in s:
        return "MAPPED"
    return "OTHER"


def norm_path(p: str) -> str:
    return str(p or "").strip().lower()


def main() -> None:
    if not FINAL.is_file() or not REVIEW.is_file() or not MAP.is_file():
        raise SystemExit("Need FINAL xlsx, REVIEW xlsx, and STRUCTURED_COPY_MAP_FINAL.csv")

    cmap = pd.read_csv(MAP, dtype=object)
    mapped_keys = set()
    mapped_by_sheet_row = defaultdict(int)
    for _, r in cmap.iterrows():
        sheet = str(r.get("source_sheet") or "")
        excel_row = r.get("excel_row")
        src = norm_path(r.get("source_path"))
        mapped_keys.add((sheet, str(excel_row) if not blank(excel_row) else "", src))
        if not blank(excel_row):
            mapped_by_sheet_row[(sheet, int(float(excel_row)))] += 1

    # --- FINAL sheets ---
    xl = pd.ExcelFile(FINAL)
    print("FINAL sheets:", xl.sheet_names)

    final_rows = []

    def add_final(sheet, excel_row, company, combine, status, paths):
        bucket = status_bucket(status)
        rec = {
            "source_sheet": sheet,
            "excel_row": excel_row,
            "company": None if blank(company) else str(company).strip(),
            "combine": None if blank(combine) else str(combine).strip(),
            "status": None if blank(status) else str(status).strip(),
            "bucket": bucket,
            "n_paths": len(paths),
            "paths": paths,
        }
        final_rows.append(rec)

    cw = pd.read_excel(FINAL, sheet_name="COMPANY WISE", dtype=object)
    cw["COMPANY_FF"] = cw["COMPANY NAME"].ffill()
    for i, r in cw.iterrows():
        add_final(
            "COMPANY WISE",
            int(i) + 2,
            r["COMPANY_FF"],
            r.get("COMBINE"),
            r.get("STATUS"),
            split_paths(r.get("MATCHED PATH")),
        )

    uf = pd.read_excel(FINAL, sheet_name="UPLOADED FORMS - COMPANY NAME", dtype=object)
    for i, r in uf.iterrows():
        add_final(
            "UPLOADED FORMS - COMPANY NAME",
            int(i) + 2,
            r.get("COMPANY NAME"),
            r.get("COMBINE"),
            r.get("STATUS"),
            split_paths(r.get("MATCHED PATH")),
        )

    din = pd.read_excel(FINAL, sheet_name="DIN FORMS", header=1, dtype=object)
    for i, r in din.iterrows():
        if blank(r.get("STATUS")) and blank(r.get("NAME")) and blank(r.get("MATCHED PATH")):
            continue
        add_final("DIN FORMS", int(i) + 3, r.get("NAME"), r.get("FOLDER"), r.get("STATUS"), split_paths(r.get("MATCHED PATH")))

    lei = pd.read_excel(FINAL, sheet_name="LEI AND OTHERS", dtype=object)
    for i, r in lei.iterrows():
        if blank(r.get("STATUS")) and blank(r.get("NAME")) and blank(r.get("MATCHED PATH")):
            continue
        add_final("LEI AND OTHERS", int(i) + 2, r.get("NAME"), r.get("FOLDER"), r.get("STATUS"), split_paths(r.get("MATCHED PATH")))

    # --- REVIEW TRUE stream ---
    wb = load_workbook(REVIEW, read_only=True, data_only=True)
    ws = wb["REVIEW"]
    review = []
    empty_streak = 0
    last = {"sheet": None, "main_row": None, "company": None, "combine": None}
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
        rec = {
            "review_row": i,
            "sheet": None if blank(sheet) else str(sheet).strip(),
            "main_row": None if blank(main_row) else int(float(main_row)),
            "company": None if blank(company) else str(company).strip(),
            "combine": None if blank(combine) else str(combine).strip(),
            "select": select,
            "select_true": is_true(select),
            "candidate_name": None if blank(cand_name) else str(cand_name).strip(),
            "candidate_path": None if blank(cand_path) else str(cand_path).strip(),
            "notes": None if blank(notes) else str(notes).strip(),
        }
        if rec["sheet"] and rec["main_row"] is not None:
            last["sheet"] = rec["sheet"]
            last["main_row"] = rec["main_row"]
            if rec["company"]:
                last["company"] = rec["company"]
            if rec["combine"]:
                last["combine"] = rec["combine"]
        elif rec["company"] and not rec["sheet"]:
            if rec["combine"]:
                last["combine"] = rec["combine"]
            if rec["company"]:
                last["company"] = rec["company"]
        rec["inh_sheet"] = rec["sheet"] or last["sheet"]
        rec["inh_main_row"] = rec["main_row"] if rec["main_row"] is not None else last["main_row"]
        rec["inh_company"] = rec["company"] or last["company"]
        review.append(rec)
    wb.close()

    true_rows = [r for r in review if r["select_true"]]
    true_with_path = [r for r in true_rows if r["candidate_path"]]
    true_no_path = [r for r in true_rows if not r["candidate_path"]]

    true_by_nf = defaultdict(list)
    for r in true_with_path:
        if r["inh_sheet"] and r["inh_main_row"] is not None:
            true_by_nf[(r["inh_sheet"], r["inh_main_row"])].append(r)

    cmap_review_paths = {norm_path(p) for p in cmap.loc[cmap["origin"] == "REVIEW_TRUE", "source_path"]}
    cmap_final_paths = {norm_path(p) for p in cmap.loc[cmap["origin"] == "FINAL", "source_path"]}
    cmap_all_paths = {norm_path(p) for p in cmap["source_path"]}

    # FINAL mapped rows: each path should be in final map unless dropped as dest+source dup
    mapped_missing = []
    mapped_ok = 0
    mapped_path_count = 0
    for rec in final_rows:
        if rec["bucket"] != "MAPPED":
            continue
        if rec["n_paths"] == 0:
            mapped_missing.append({**{k: rec[k] for k in ("source_sheet", "excel_row", "company", "combine", "status")}, "reason": "MAPPED_BUT_NO_PATH"})
            continue
        for src in rec["paths"]:
            mapped_path_count += 1
            key = (rec["source_sheet"], str(rec["excel_row"]), norm_path(src))
            if key in mapped_keys or norm_path(src) in cmap_all_paths:
                mapped_ok += 1
            else:
                mapped_missing.append(
                    {
                        "source_sheet": rec["source_sheet"],
                        "excel_row": rec["excel_row"],
                        "company": rec["company"],
                        "combine": rec["combine"],
                        "status": rec["status"],
                        "source_path": src,
                        "reason": "MAPPED_PATH_NOT_IN_FINAL_MAP",
                    }
                )

    nf_rows = [r for r in final_rows if r["bucket"] == "NOT_FOUND"]
    nf_resolved = []
    nf_unresolved = []
    for rec in nf_rows:
        hits = true_by_nf.get((rec["source_sheet"], rec["excel_row"]), [])
        if hits:
            nf_resolved.append(rec)
        else:
            nf_unresolved.append(rec)

    skipped = [r for r in final_rows if r["bucket"] == "SKIPPED"]
    other = [r for r in final_rows if r["bucket"] == "OTHER"]
    blank_st = [r for r in final_rows if r["bucket"] == "BLANK"]

    true_path_missing = []
    true_path_ok = 0
    for r in true_with_path:
        if norm_path(r["candidate_path"]) in cmap_all_paths:
            true_path_ok += 1
        else:
            true_path_missing.append(
                {
                    "review_row": r["review_row"],
                    "sheet": r["inh_sheet"],
                    "excel_row": r["inh_main_row"],
                    "company": r["inh_company"],
                    "candidate_path": r["candidate_path"],
                    "reason": "TRUE_PATH_NOT_IN_FINAL_MAP",
                }
            )

    # header-like TRUE ticks (review_row small / no company)
    true_no_path_detail = [
        {
            "review_row": r["review_row"],
            "sheet": r["inh_sheet"],
            "excel_row": r["inh_main_row"],
            "company": r["inh_company"],
            "notes": r["notes"],
            "reason": "TRUE_BUT_NO_CANDIDATE_PATH",
        }
        for r in true_no_path
    ]

    counts = [
        ("final_company_wise_rows", sum(1 for r in final_rows if r["source_sheet"] == "COMPANY WISE")),
        ("final_uploaded_forms_rows", sum(1 for r in final_rows if r["source_sheet"] == "UPLOADED FORMS - COMPANY NAME")),
        ("final_din_forms_rows", sum(1 for r in final_rows if r["source_sheet"] == "DIN FORMS")),
        ("final_lei_rows", sum(1 for r in final_rows if r["source_sheet"] == "LEI AND OTHERS")),
        ("final_total_data_rows", len(final_rows)),
        ("final_MAPPED_rows", sum(1 for r in final_rows if r["bucket"] == "MAPPED")),
        ("final_MAPPED_paths", mapped_path_count),
        ("final_MAPPED_paths_in_copy_map", mapped_ok),
        ("final_MAPPED_paths_missing_from_copy_map", len([x for x in mapped_missing if x.get("reason") == "MAPPED_PATH_NOT_IN_FINAL_MAP"])),
        ("final_MAPPED_rows_with_no_path", len([x for x in mapped_missing if x.get("reason") == "MAPPED_BUT_NO_PATH"])),
        ("final_NOT_FOUND_rows", len(nf_rows)),
        ("final_NOT_FOUND_resolved_by_REVIEW_TRUE", len(nf_resolved)),
        ("final_NOT_FOUND_still_unresolved", len(nf_unresolved)),
        ("final_SKIPPED_rows", len(skipped)),
        ("final_OTHER_status_rows", len(other)),
        ("final_BLANK_status_rows", len(blank_st)),
        ("review_content_rows", len(review)),
        ("review_SELECT_TRUE", len(true_rows)),
        ("review_TRUE_with_path", len(true_with_path)),
        ("review_TRUE_with_path_in_copy_map", true_path_ok),
        ("review_TRUE_with_path_missing_from_copy_map", len(true_path_missing)),
        ("review_TRUE_without_path", len(true_no_path)),
        ("copy_map_rows", len(cmap)),
        ("copy_map_FINAL", int((cmap["origin"] == "FINAL").sum())),
        ("copy_map_REVIEW_TRUE", int((cmap["origin"] == "REVIEW_TRUE").sum())),
    ]

    nf_unres_df = pd.DataFrame(
        [
            {
                "source_sheet": r["source_sheet"],
                "excel_row": r["excel_row"],
                "company": r["company"],
                "combine": r["combine"],
                "status": r["status"],
            }
            for r in nf_unresolved
        ]
    )
    skipped_df = pd.DataFrame(
        [
            {
                "source_sheet": r["source_sheet"],
                "excel_row": r["excel_row"],
                "company": r["company"],
                "combine": r["combine"],
                "status": r["status"],
            }
            for r in skipped
        ]
    )
    other_df = pd.DataFrame(
        [
            {
                "source_sheet": r["source_sheet"],
                "excel_row": r["excel_row"],
                "company": r["company"],
                "combine": r["combine"],
                "status": r["status"],
            }
            for r in other
        ]
    )

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        pd.DataFrame(counts, columns=["metric", "value"]).to_excel(writer, sheet_name="SUMMARY", index=False)
        pd.DataFrame(mapped_missing).to_excel(writer, sheet_name="MAPPED_MISSING", index=False)
        nf_unres_df.to_excel(writer, sheet_name="NF_UNRESOLVED", index=False)
        pd.DataFrame(true_path_missing).to_excel(writer, sheet_name="TRUE_PATH_MISSING", index=False)
        pd.DataFrame(true_no_path_detail).to_excel(writer, sheet_name="TRUE_NO_PATH", index=False)
        skipped_df.to_excel(writer, sheet_name="SKIPPED", index=False)
        other_df.to_excel(writer, sheet_name="OTHER_STATUS", index=False)

    print("wrote", OUT)
    for k, v in counts:
        print(f"{k}={v}")


if __name__ == "__main__":
    main()
