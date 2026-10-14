"""Full FINAL (12) rows that are still missing or unresolved, plus REVIEW coverage."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx"
REVIEW = ROOT / "NOT FOUND - REVIEW - ALL COMPLETED.xlsx"
MAP = Path(__file__).resolve().parent / "STRUCTURED_COPY_MAP_FINAL.csv"
OUT = Path(__file__).resolve().parent / "MISSING_AND_ISSUES_FULL_ROWS.xlsx"

TRUE_LIKE = {True, "TRUE", "True", "true", "X", "x", "Y", "y", "1", 1, 1.0}


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


def status_kind(status) -> str:
    s = str(status or "").strip().upper()
    if not s:
        return "BLANK"
    if s.startswith("NOT FOUND") or s.startswith("NOT ON BACKUP"):
        return "NOT_FOUND"
    if s.startswith("SKIPPED"):
        return "SKIPPED"
    return "MAPPED_OR_OTHER"


def load_review():
    wb = load_workbook(REVIEW, read_only=True, data_only=True)
    ws = wb["REVIEW"]
    rows = []
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
        rows.append(rec)
    wb.close()
    return rows


def style_sheet(ws):
    ws.freeze_panes = "A2"
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
        for cell in col[:40]:
            if cell.value is None:
                continue
            maxlen = min(max(maxlen, len(str(cell.value))), 55)
        ws.column_dimensions[letter].width = maxlen


def main() -> None:
    cmap = pd.read_csv(MAP, dtype=object)
    cmap_paths = {str(p).strip().lower() for p in cmap["source_path"] if not blank(p)}

    review = load_review()
    by_nf: dict[tuple, list] = defaultdict(list)
    review_keys = set()
    for r in review:
        if r["inh_sheet"] and r["inh_main_row"] is not None:
            key = (r["inh_sheet"], r["inh_main_row"])
            by_nf[key].append(r)
            review_keys.add(key)

    def review_summary(sheet: str, excel_row: int) -> dict:
        hits = by_nf.get((sheet, excel_row), [])
        trues = [h for h in hits if h["select_true"]]
        true_paths = [h["candidate_path"] for h in trues if h["candidate_path"]]
        in_map = [p for p in true_paths if p.strip().lower() in cmap_paths]
        if not hits:
            coverage = "NOT_IN_REVIEW"
            resolution = "NOT_IN_REVIEW"
        elif true_paths and in_map:
            coverage = "IN_REVIEW"
            resolution = "RESOLVED_TRUE_PATH_IN_COPY_MAP"
        elif true_paths:
            coverage = "IN_REVIEW"
            resolution = "TRUE_TICKED_BUT_PATH_NOT_IN_COPY_MAP"
        elif trues:
            coverage = "IN_REVIEW"
            resolution = "TRUE_TICKED_BUT_NO_PATH"
        else:
            coverage = "IN_REVIEW"
            resolution = "IN_REVIEW_BUT_NO_TRUE_TICK"
        return {
            "review_present": coverage,
            "review_resolution": resolution,
            "review_candidate_rows": len(hits),
            "review_TRUE_ticks": len(trues),
            "review_TRUE_paths": len(true_paths),
            "review_TRUE_paths_in_copy_map": len(in_map),
            "review_TRUE_path_list": " ; ".join(true_paths),
            "review_notes": " | ".join({h["notes"] for h in hits if h["notes"]}),
        }

    issue_rows = []

    def add_issue(issue_type, sheet, excel_row, original: dict, extra: dict):
        row = {
            "issue_type": issue_type,
            "source_sheet": sheet,
            "excel_row": excel_row,
        }
        row.update(review_summary(sheet, excel_row))
        row.update(extra)
        for k, v in original.items():
            col = f"orig_{k}"
            if col not in row:
                row[col] = v
        issue_rows.append(row)

    # COMPANY WISE
    cw = pd.read_excel(FINAL, sheet_name="COMPANY WISE", dtype=object)
    cw["COMPANY NAME"] = cw["COMPANY NAME"].ffill()
    for i, r in cw.iterrows():
        excel_row = int(i) + 2
        original = {str(c): r.get(c) for c in cw.columns if c != "COMPANY_FF"}
        kind = status_kind(r.get("STATUS"))
        paths = split_paths(r.get("MATCHED PATH"))
        if kind == "NOT_FOUND":
            extra = review_summary("COMPANY WISE", excel_row)
            issue = extra["review_resolution"]
            add_issue(issue, "COMPANY WISE", excel_row, original, {})
        elif kind == "SKIPPED":
            add_issue("SKIPPED_IN_FINAL12", "COMPANY WISE", excel_row, original, {})
        elif kind != "BLANK" and not paths:
            add_issue("STATUS_OK_BUT_NO_PATH", "COMPANY WISE", excel_row, original, {})

    # UPLOADED FORMS
    uf = pd.read_excel(FINAL, sheet_name="UPLOADED FORMS - COMPANY NAME", dtype=object)
    for i, r in uf.iterrows():
        excel_row = int(i) + 2
        original = {str(c): r.get(c) for c in uf.columns}
        kind = status_kind(r.get("STATUS"))
        paths = split_paths(r.get("MATCHED PATH"))
        if kind == "NOT_FOUND":
            extra = review_summary("UPLOADED FORMS - COMPANY NAME", excel_row)
            add_issue(extra["review_resolution"], "UPLOADED FORMS - COMPANY NAME", excel_row, original, {})
        elif kind == "SKIPPED":
            add_issue("SKIPPED_IN_FINAL12", "UPLOADED FORMS - COMPANY NAME", excel_row, original, {})
        elif kind != "BLANK" and not paths:
            add_issue("STATUS_OK_BUT_NO_PATH", "UPLOADED FORMS - COMPANY NAME", excel_row, original, {})

    # DIN FORMS header row 2
    din = pd.read_excel(FINAL, sheet_name="DIN FORMS", header=1, dtype=object)
    for i, r in din.iterrows():
        if blank(r.get("STATUS")) and blank(r.get("NAME")) and blank(r.get("MATCHED PATH")):
            continue
        excel_row = int(i) + 3
        original = {str(c): r.get(c) for c in din.columns}
        kind = status_kind(r.get("STATUS"))
        paths = split_paths(r.get("MATCHED PATH"))
        if kind == "NOT_FOUND":
            extra = review_summary("DIN FORMS", excel_row)
            add_issue(extra["review_resolution"], "DIN FORMS", excel_row, original, {})
        elif kind == "SKIPPED":
            add_issue("SKIPPED_IN_FINAL12", "DIN FORMS", excel_row, original, {})
        elif kind != "BLANK" and not paths:
            add_issue("STATUS_OK_BUT_NO_PATH", "DIN FORMS", excel_row, original, {})

    # LEI
    lei = pd.read_excel(FINAL, sheet_name="LEI AND OTHERS", dtype=object)
    for i, r in lei.iterrows():
        if blank(r.get("STATUS")) and blank(r.get("NAME")) and blank(r.get("MATCHED PATH")):
            continue
        excel_row = int(i) + 2
        original = {str(c): r.get(c) for c in lei.columns}
        kind = status_kind(r.get("STATUS"))
        paths = split_paths(r.get("MATCHED PATH"))
        if kind == "NOT_FOUND":
            extra = review_summary("LEI AND OTHERS", excel_row)
            add_issue(extra["review_resolution"], "LEI AND OTHERS", excel_row, original, {})
        elif kind == "SKIPPED":
            add_issue("SKIPPED_IN_FINAL12", "LEI AND OTHERS", excel_row, original, {})
        elif kind != "BLANK" and not paths:
            add_issue("STATUS_OK_BUT_NO_PATH", "LEI AND OTHERS", excel_row, original, {})

    # REVIEW TRUE with no usable path
    true_issues = []
    for r in review:
        if not r["select_true"]:
            continue
        if r["candidate_path"] and r["candidate_path"].strip().lower() in cmap_paths:
            continue
        true_issues.append(
            {
                "issue_type": "TRUE_BUT_NO_PATH" if not r["candidate_path"] else "TRUE_PATH_NOT_IN_COPY_MAP",
                "review_row": r["review_row"],
                "sheet": r["inh_sheet"],
                "excel_row": r["inh_main_row"],
                "company": r["inh_company"],
                "combine": r["combine"],
                "candidate_name": r["candidate_name"],
                "candidate_path": r["candidate_path"],
                "notes": r["notes"],
                "select": r["select"],
            }
        )

    issues = pd.DataFrame(issue_rows)
    # Keep unresolved / missing only on ALL_ISSUES; also keep a dedicated NF coverage sheet of ALL not found
    nf_mask = issues["issue_type"].isin(
        [
            "NOT_IN_REVIEW",
            "IN_REVIEW_BUT_NO_TRUE_TICK",
            "TRUE_TICKED_BUT_NO_PATH",
            "TRUE_TICKED_BUT_PATH_NOT_IN_COPY_MAP",
            "RESOLVED_TRUE_PATH_IN_COPY_MAP",
        ]
    )
    nf_all = issues.loc[nf_mask].copy()
    still_open = issues.loc[
        issues["issue_type"].isin(
            [
                "NOT_IN_REVIEW",
                "IN_REVIEW_BUT_NO_TRUE_TICK",
                "TRUE_TICKED_BUT_NO_PATH",
                "TRUE_TICKED_BUT_PATH_NOT_IN_COPY_MAP",
                "SKIPPED_IN_FINAL12",
                "STATUS_OK_BUT_NO_PATH",
            ]
        )
    ].copy()

    nf_counts = nf_all["issue_type"].value_counts().to_dict() if len(nf_all) else {}
    open_counts = still_open["issue_type"].value_counts().to_dict() if len(still_open) else {}
    sheet_nf = nf_all.groupby(["source_sheet", "issue_type"]).size().reset_index(name="n") if len(nf_all) else pd.DataFrame()

    summary = pd.DataFrame(
        [
            ("final12_NOT_FOUND_total", int(nf_mask.sum()) if len(issues) else 0),
            ("NF_in_review", int((nf_all["review_present"] == "IN_REVIEW").sum()) if len(nf_all) else 0),
            ("NF_NOT_in_review", int(nf_counts.get("NOT_IN_REVIEW", 0))),
            ("NF_resolved_TRUE_path_in_copy_map", int(nf_counts.get("RESOLVED_TRUE_PATH_IN_COPY_MAP", 0))),
            ("NF_in_review_but_no_TRUE_tick", int(nf_counts.get("IN_REVIEW_BUT_NO_TRUE_TICK", 0))),
            ("NF_TRUE_ticked_but_no_path", int(nf_counts.get("TRUE_TICKED_BUT_NO_PATH", 0))),
            ("NF_TRUE_path_not_in_copy_map", int(nf_counts.get("TRUE_TICKED_BUT_PATH_NOT_IN_COPY_MAP", 0))),
            ("review_all_NF_resolved", "NO" if (nf_counts.get("NOT_IN_REVIEW", 0) or nf_counts.get("IN_REVIEW_BUT_NO_TRUE_TICK", 0) or nf_counts.get("TRUE_TICKED_BUT_NO_PATH", 0) or nf_counts.get("TRUE_TICKED_BUT_PATH_NOT_IN_COPY_MAP", 0)) else "YES"),
            ("SKIPPED_in_final12", int(open_counts.get("SKIPPED_IN_FINAL12", 0))),
            ("STATUS_OK_BUT_NO_PATH", int(open_counts.get("STATUS_OK_BUT_NO_PATH", 0))),
            ("review_TRUE_without_usable_path", len(true_issues)),
            ("open_issue_rows_to_fix", len(still_open)),
        ],
        columns=["metric", "value"],
    )

    # Preferred column order
    front = [
        "issue_type",
        "source_sheet",
        "excel_row",
        "review_present",
        "review_resolution",
        "review_candidate_rows",
        "review_TRUE_ticks",
        "review_TRUE_paths",
        "review_TRUE_paths_in_copy_map",
        "review_TRUE_path_list",
        "review_notes",
    ]
    orig_cols = [c for c in still_open.columns if c.startswith("orig_")]
    ordered = [c for c in front if c in still_open.columns] + orig_cols + [c for c in still_open.columns if c not in front and c not in orig_cols]
    still_open = still_open[ordered]
    nf_all = nf_all[[c for c in ordered if c in nf_all.columns]]

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="ANSWERS", index=False)
        still_open.to_excel(writer, sheet_name="ALL_OPEN_ISSUES_FULL_ROWS", index=False)
        nf_all.to_excel(writer, sheet_name="ALL_NOT_FOUND_FROM_FINAL12", index=False)
        nf_all[nf_all["issue_type"] == "NOT_IN_REVIEW"].to_excel(writer, sheet_name="NF_NOT_IN_REVIEW", index=False)
        nf_all[nf_all["issue_type"] == "IN_REVIEW_BUT_NO_TRUE_TICK"].to_excel(writer, sheet_name="NF_IN_REVIEW_NO_TRUE", index=False)
        nf_all[nf_all["issue_type"] == "RESOLVED_TRUE_PATH_IN_COPY_MAP"].to_excel(writer, sheet_name="NF_RESOLVED", index=False)
        still_open[still_open["issue_type"] == "SKIPPED_IN_FINAL12"].to_excel(writer, sheet_name="SKIPPED_FULL_ROWS", index=False)
        pd.DataFrame(true_issues).to_excel(writer, sheet_name="REVIEW_TRUE_NO_PATH", index=False)
        sheet_nf.to_excel(writer, sheet_name="NF_COUNTS_BY_SHEET", index=False)

        for name, ws in writer.sheets.items():
            style_sheet(ws)

    print("wrote", OUT)
    print(summary.to_string(index=False))
    print("open_issue_types", open_counts)
    print("nf_types", nf_counts)


if __name__ == "__main__":
    main()
