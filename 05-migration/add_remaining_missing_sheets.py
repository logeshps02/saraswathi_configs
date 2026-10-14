"""Add remaining-missing sheets to NOT FOUND - REVIEW - ALL COMPLETED.xlsx.

Does not change REVIEW / Sheet1. New sheets only.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(r"c:\Users\U.lalitha navya sri\Downloads\Logesh files")
REVIEW_XLSX = ROOT / "NOT FOUND - REVIEW - ALL COMPLETED.xlsx"
FALLBACK_XLSX = ROOT / "NOT FOUND - REVIEW - ALL COMPLETED - REMAINING MISSING.xlsx"
MAP_CSV = ROOT / "05-migration" / "STRUCTURED_COPY_MAP_FINAL.csv"
MISS_CSV = ROOT / "05-migration" / "COPY_FAILED_AND_MISSING.csv"
RESOLVED_XLSX = ROOT / "05-migration" / "REVIEW_RESOLVED_CORRECT.xlsx"

FINAL_FILE = "BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx"
REVIEW_FILE = "NOT FOUND - REVIEW - ALL COMPLETED.xlsx"

CORRECT_2017 = {
    r"F:\2017-18\UPLOADED FORMS\OCTOBER-17\Uploaded on 10.10.17 GEOMEO INFORMATICS PRIVATE LIMITED-AOC-4": r"F:\2017-18\UPLOADED FORMS\OCTOBER-17\Uploaded on 10.10.17 GEOMEO INFORMATICS PRIVATE LIMITED-AOC-4;MGT-7;ADT-1",
    r"F:\2017-18\UPLOADED FORMS\SEPTEMBER-17\Uploaded on 04.09.2017 ONDEOS TECHNOLOGIES PRIVATE LIMITED-MGT-14": r"F:\2017-18\UPLOADED FORMS\SEPTEMBER-17\Uploaded on 04.09.2017 ONDEOS TECHNOLOGIES PRIVATE LIMITED-MGT-14;STK-2",
    r"F:\2017-18\UPLOADED FORMS\AUGUEST-17\Uploaded on 24.08.2017QUADRATIC STRUCTURE INDIA PRIVATE LIMITED-MGT-14": r"F:\2017-18\UPLOADED FORMS\AUGUEST-17\Uploaded on 24.08.2017QUADRATIC STRUCTURE INDIA PRIVATE LIMITED-MGT-14;SH-7",
    r"F:\2017-18\UPLOADED FORMS\SEPTEMBER-17\Uploaded on 01.09.2017 SKYWING HOLIDAYS PRIVATE LIMITED-AOC-4": r"F:\2017-18\UPLOADED FORMS\SEPTEMBER-17\Uploaded on 01.09.2017 SKYWING HOLIDAYS PRIVATE LIMITED-AOC-4;MGT-7",
    r"F:\2017-18\UPLOADED FORMS\AUGUEST-17\Uploaded on 18.08.2017 SKYWING HOLIDAYS PRIVATE LIMITED AOC-4": r"F:\2017-18\UPLOADED FORMS\AUGUEST-17\Uploaded on 18.08.2017 SKYWING HOLIDAYS PRIVATE LIMITED AOC-4;MGT-7",
    r"F:\2017-18\UPLOADED FORMS\OCTOBER-17\Uploaded on 06.10.17&07.10.17 SRI YANNARKAY SERVICERS LTD-MGT-7": r"F:\2017-18\UPLOADED FORMS\OCTOBER-17\Uploaded on 06.10.17&07.10.17 SRI YANNARKAY SERVICERS LTD-MGT-7;AOC-4",
}

NAME_ONLY = {"ADT-1", "MGT-7", "STK-2", "SH-7", "AOC-4"}

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(color="FFFFFF", bold=True)
WRAP = Alignment(wrap_text=True, vertical="top")
FILLS = {
    "NEED_H_DRIVE": PatternFill("solid", fgColor="F4B183"),
    "NOT_A_REAL_FOLDER_NAME_ONLY": PatternFill("solid", fgColor="D9D9D9"),
    "SHORT_WRONG_2017_18_ALREADY_COPIED_CORRECT": PatternFill("solid", fgColor="C6EFCE"),
    "NO_TRUE_AND_NO_LISTING_HIT": PatternFill("solid", fgColor="FFC7CE"),
    "NO_TRUE_BUT_NAME_IN_FILE_LIST": PatternFill("solid", fgColor="FFE699"),
}


def mentioned_in(origin: str) -> tuple[str, str]:
    if str(origin).startswith("REVIEW"):
        return REVIEW_FILE, "NOT FOUND REVIEW"
    return FINAL_FILE, "FINAL 12"


def classify_copy_row(source_path: str) -> tuple[str, str, str]:
    sp = str(source_path or "").strip()
    if sp.startswith(r"H:\OFFICE SARASWATHI"):
        return (
            "NEED_H_DRIVE",
            "YES — copy when H: is attached",
            "Source is on H:\\OFFICE SARASWATHI. Not copied because that drive was not attached.",
        )
    if sp in NAME_ONLY or (":" not in sp and "\\" not in sp):
        return (
            "NOT_A_REAL_FOLDER_NAME_ONLY",
            "NO — leave",
            "Sheet listed a form name only (no drive/path). Not a real folder. The combined 2017-18 folder was copied separately if it existed.",
        )
    if sp in CORRECT_2017:
        return (
            "SHORT_WRONG_2017_18_ALREADY_COPIED_CORRECT",
            "NO — already copied under the correct longer name",
            "Sheet had the short/wrong folder name. Real folder has extra forms after ';'. That correct folder is already in F:\\Final.",
        )
    return ("OTHER_MISSING", "CHECK", "")


def autosize(ws, max_width: int = 70) -> None:
    for col in ws.columns:
        letter = get_column_letter(col[0].column)
        longest = 0
        for cell in col:
            val = "" if cell.value is None else str(cell.value)
            longest = max(longest, min(len(val), max_width))
            cell.alignment = WRAP
        ws.column_dimensions[letter].width = min(max(12, longest + 2), max_width)
    ws.auto_filter.ref = ws.dimensions
    ws.freeze_panes = "A2"
    ws.row_dimensions[1].height = 22
    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT


def write_df(wb, name: str, df: pd.DataFrame, color_col: str | None = None) -> None:
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name)
    if df.empty:
        ws.append(["(no rows)"])
        return
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(list(r))
    if color_col and color_col in df.columns:
        idx = list(df.columns).index(color_col) + 1
        for i, val in enumerate(df[color_col].tolist(), start=2):
            fill = FILLS.get(str(val))
            if fill:
                ws.cell(i, idx).fill = fill
    autosize(ws)
    ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"
    table = Table(displayName=name.replace(" ", "_")[:30] + "Tbl", ref=ref)
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    try:
        ws.add_table(table)
    except Exception:
        pass


def main() -> None:
    miss = pd.read_csv(MISS_CSV, dtype=str).fillna("")
    miss = miss[miss["kind"] == "MISSING_SOURCE"].copy()
    mp = pd.read_csv(MAP_CSV, dtype=str).fillna("")

    rows = []
    for rec in miss.to_dict("records"):
        src = rec.get("source_path", "")
        dest = rec.get("dest_relative", "")
        hit = mp[(mp["source_path"] == src) & (mp["dest_relative"] == dest)]
        if hit.empty:
            hit = mp[mp["dest_relative"] == dest]
        m = hit.iloc[0].to_dict() if not hit.empty else {}
        origin = rec.get("origin") or m.get("origin") or ""
        file_name, file_kind = mentioned_in(origin)
        category, action, note = classify_copy_row(src)
        excel_row = rec.get("excel_row") or m.get("excel_row") or ""
        review_row = m.get("review_row") or ""
        source_sheet = rec.get("source_sheet") or m.get("source_sheet") or ""
        rows.append(
            {
                "still_needed": action.split("—")[0].strip() if "—" in action else action,
                "category": category,
                "what_to_do": action,
                "mentioned_in_file": file_name,
                "mentioned_in": file_kind,
                "origin": origin,
                "source_sheet_in_final12": source_sheet,
                "final12_excel_row": excel_row,
                "review_sheet": "REVIEW" if file_kind == "NOT FOUND REVIEW" else "",
                "review_excel_row": review_row,
                "company": rec.get("company") or m.get("company") or "",
                "year": rec.get("year") or m.get("year") or "",
                "combine": m.get("combine") or "",
                "source_path_as_in_sheet": src,
                "dest_relative_in_F_Final": dest,
                "correct_source_if_any": CORRECT_2017.get(src, ""),
                "copy_log_row": rec.get("log_excel_row") or "",
                "notes": note,
            }
        )
    copy_df = pd.DataFrame(rows)
    order = [
        "NEED_H_DRIVE",
        "NOT_A_REAL_FOLDER_NAME_ONLY",
        "SHORT_WRONG_2017_18_ALREADY_COPIED_CORRECT",
        "OTHER_MISSING",
    ]
    copy_df["_ord"] = copy_df["category"].map({k: i for i, k in enumerate(order)}).fillna(99)
    copy_df = copy_df.sort_values(["_ord", "company", "year", "final12_excel_row"]).drop(columns="_ord")

    style = pd.read_excel(RESOLVED_XLSX, sheet_name="REVIEW_STYLE_RESOLVED", dtype=str).fillna("")
    open_st = style[style["status"].isin(["STILL_NO_TRUE", "NO_TRUE_BUT_NAME_IN_FILE_LIST"])].copy()
    review_open_rows = []
    for rec in open_st.to_dict("records"):
        st = rec.get("status", "")
        if st == "STILL_NO_TRUE":
            cat = "NO_TRUE_AND_NO_LISTING_HIT"
            action = "NO auto-copy — still no TRUE in review"
            note = "NOT FOUND in FINAL 12. Review has no TRUE path for this company/year. Not in the 6863 copy."
        else:
            cat = "NO_TRUE_BUT_NAME_IN_FILE_LIST"
            action = "NO auto-copy — listing-only (do not assume TRUE)"
            note = "NOT FOUND in FINAL 12. Company name appears in the file listing, but review did not mark TRUE. Not in the 6863 copy."
        review_open_rows.append(
            {
                "still_needed": "REVIEW leftover — not in copy map",
                "category": cat,
                "what_to_do": action,
                "mentioned_in_file": FINAL_FILE + " (NOT FOUND row) + " + REVIEW_FILE,
                "mentioned_in": "FINAL 12 + NOT FOUND REVIEW",
                "origin": "REVIEW leftover (not copied)",
                "source_sheet_in_final12": rec.get("source_sheet") or "",
                "final12_excel_row": rec.get("excel_row") or "",
                "review_sheet": "REVIEW",
                "review_excel_row": rec.get("true_review_rows") or "",
                "company": rec.get("company") or "",
                "year": rec.get("year") or "",
                "combine": rec.get("combine") or "",
                "source_path_as_in_sheet": rec.get("resolved_path") or rec.get("listing_paths") or "",
                "dest_relative_in_F_Final": "",
                "listing_paths": rec.get("listing_paths") or "",
                "listing_name_hits": rec.get("listing_name_hits") or "",
                "notes": note,
            }
        )
    review_open = pd.DataFrame(review_open_rows)
    if not review_open.empty:
        review_open = review_open.sort_values(["category", "company", "year", "final12_excel_row"])

    summary = pd.DataFrame(
        [
            ["NEED_H_DRIVE", int((copy_df["category"] == "NEED_H_DRIVE").sum()), "Real folders on H:. Copy only when H: is attached."],
            ["NOT_A_REAL_FOLDER_NAME_ONLY", int((copy_df["category"] == "NOT_A_REAL_FOLDER_NAME_ONLY").sum()), "Form name only in FINAL 12. Not a folder. Leave."],
            ["SHORT_WRONG_2017_18_ALREADY_COPIED_CORRECT", int((copy_df["category"] == "SHORT_WRONG_2017_18_ALREADY_COPIED_CORRECT").sum()), "Wrong/short 2017-18 name. Correct ;forms folder already in F:\\Final."],
            ["REVIEW leftover — no TRUE, name in listing", int((style["status"] == "NO_TRUE_BUT_NAME_IN_FILE_LIST").sum()), "Not in 6863 copy. Do not auto-add."],
            ["REVIEW leftover — still no TRUE", int((style["status"] == "STILL_NO_TRUE").sum()), "Not in 6863 copy. LITTLE MOPPET / N.R.K INFRA / NEOMAX / PRANAVSREE etc."],
            ["Long-dest retries (KIRUBA, PSN, PRIDE x2, SWAMI x2)", 0, "DONE. Not missing. SWAMI 14.06.2024 dest exists; source had 0 files."],
            ["Correct 2017-18 ;forms folders", 0, "DONE. 6 folders copied into F:\\Final."],
        ],
        columns=["item", "count", "notes"],
    )

    legend = pd.DataFrame(
        [
            ["still_needed / category", "How to read the leftover"],
            ["mentioned_in_file", "Workbook where this row was listed"],
            ["mentioned_in", "FINAL 12 = BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx; NOT FOUND REVIEW = this file"],
            ["source_sheet_in_final12", "Tab inside FINAL 12 (COMPANY WISE / UPLOADED FORMS - COMPANY NAME / …)"],
            ["final12_excel_row", "Excel row number in that FINAL 12 sheet (1 = header, so data rows start at 2)"],
            ["review_excel_row", "Excel row number on the REVIEW sheet of this file, if origin is REVIEW_TRUE"],
            ["REVIEW and Sheet1", "Unchanged. New sheets only. Do not rerun the 6863 copy."],
        ],
        columns=["column", "meaning"],
    )

    try:
        wb = load_workbook(REVIEW_XLSX)
        out_path = REVIEW_XLSX
    except PermissionError:
        wb = load_workbook(REVIEW_XLSX)
        out_path = FALLBACK_XLSX

    write_df(wb, "REMAINING_MISSING", copy_df, "category")
    write_df(wb, "REVIEW_STILL_OPEN", review_open, "category")
    write_df(wb, "REMAINING_SUMMARY", summary)
    write_df(wb, "HOW_TO_READ", legend)

    # keep REVIEW / Sheet1 first
    order_names = ["REVIEW", "Sheet1", "REMAINING_SUMMARY", "REMAINING_MISSING", "REVIEW_STILL_OPEN", "HOW_TO_READ"]
    for i, n in enumerate(order_names):
        if n in wb.sheetnames:
            wb.move_sheet(n, offset=i - wb.sheetnames.index(n))

    try:
        wb.save(out_path)
    except PermissionError:
        out_path = FALLBACK_XLSX
        wb.save(out_path)
    print("saved", out_path)
    print("REMAINING_MISSING", len(copy_df))
    print(copy_df["category"].value_counts().to_string())
    print("REVIEW_STILL_OPEN", len(review_open))
    if not review_open.empty:
        print(review_open["category"].value_counts().to_string())


if __name__ == "__main__":
    main()
