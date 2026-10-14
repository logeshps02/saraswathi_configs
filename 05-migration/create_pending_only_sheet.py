"""Create a pending-only workbook: unfinished items with full details.

Does not include copied / resolved leftover rows.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(r"c:\Users\U.lalitha navya sri\Downloads\Logesh files")
REVIEW_XLSX = ROOT / "NOT FOUND - REVIEW - ALL COMPLETED.xlsx"
TODO_XLSX = ROOT / "05-migration" / "MISSING_AND_ISSUES_TO_DO.xlsx"
OUT = ROOT / "05-migration" / "PENDING_ONLY.xlsx"

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(color="FFFFFF", bold=True)
WRAP = Alignment(wrap_text=True, vertical="top")
FILLS = {
    "STILL_MISSING_FOLDER_NOT_ON_HDD": PatternFill("solid", fgColor="FFC7CE"),
    "NO_TRUE_AND_NO_LISTING_HIT": PatternFill("solid", fgColor="F4B183"),
    "NO_TRUE_BUT_NAME_IN_FILE_LIST": PatternFill("solid", fgColor="FFE699"),
}

COLS = [
    "sno",
    "pending_type",
    "what_staff_must_do",
    "company",
    "year",
    "combine",
    "mentioned_in",
    "source_sheet",
    "final12_excel_row",
    "review_excel_row",
    "folder_or_path",
    "listing_paths",
    "notes",
]


def write_df(wb, name: str, df: pd.DataFrame, color_col: str | None = None, table_name: str = "Tbl") -> None:
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
    for col in ws.columns:
        letter = get_column_letter(col[0].column)
        longest = 12
        for cell in col:
            cell.alignment = WRAP
            val = "" if cell.value is None else str(cell.value)
            longest = max(longest, min(len(val) + 2, 80))
        ws.column_dimensions[letter].width = longest
    ws.row_dimensions[1].height = 22
    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"
    t = Table(displayName=table_name[:30], ref=ref)
    t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    try:
        ws.add_table(t)
    except Exception:
        pass


def s(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return str(v).strip()


def build_pending() -> pd.DataFrame:
    miss = pd.read_excel(REVIEW_XLSX, sheet_name="REMAINING_MISSING", dtype=str).fillna("")
    open_st = pd.read_excel(REVIEW_XLSX, sheet_name="REVIEW_STILL_OPEN", dtype=str).fillna("")
    rows = []

    for rec in miss.to_dict("records"):
        if s(rec.get("still_needed")).upper() != "YES":
            continue
        rows.append(
            {
                "pending_type": s(rec.get("category")) or "STILL_MISSING_FOLDER_NOT_ON_HDD",
                "what_staff_must_do": "Find the 03.11.2022 GREEN WEALTH folder. It is not on D:. Do not copy the 24.09.2022 AOC-4, MGT-14 folder instead.",
                "company": s(rec.get("company")),
                "year": s(rec.get("year")),
                "combine": s(rec.get("combine")),
                "mentioned_in": s(rec.get("mentioned_in")),
                "source_sheet": s(rec.get("source_sheet_in_final12")),
                "final12_excel_row": s(rec.get("final12_excel_row")),
                "review_excel_row": s(rec.get("review_excel_row")),
                "folder_or_path": s(rec.get("source_path_as_in_sheet")),
                "listing_paths": "",
                "notes": s(rec.get("notes")),
            }
        )

    for rec in open_st.to_dict("records"):
        cat = s(rec.get("category"))
        if cat == "NO_TRUE_BUT_NAME_IN_FILE_LIST":
            do = "Staff pick: company name appears in listing. Confirm if one of listing_paths is the right folder. Do not auto-copy."
        else:
            do = "Staff pick: still no TRUE path in review and no listing hit. Locate the folder or confirm it does not exist."
        listing = s(rec.get("listing_paths"))
        folder = s(rec.get("source_path_as_in_sheet"))
        rows.append(
            {
                "pending_type": cat,
                "what_staff_must_do": do,
                "company": s(rec.get("company")),
                "year": s(rec.get("year")),
                "combine": s(rec.get("combine")),
                "mentioned_in": s(rec.get("mentioned_in")),
                "source_sheet": s(rec.get("source_sheet_in_final12")),
                "final12_excel_row": s(rec.get("final12_excel_row")),
                "review_excel_row": s(rec.get("review_excel_row")),
                "folder_or_path": folder if folder and folder != listing else "",
                "listing_paths": listing,
                "notes": s(rec.get("notes")),
            }
        )

    df = pd.DataFrame(rows)
    order = {
        "STILL_MISSING_FOLDER_NOT_ON_HDD": 0,
        "NO_TRUE_AND_NO_LISTING_HIT": 1,
        "NO_TRUE_BUT_NAME_IN_FILE_LIST": 2,
    }
    df["_o"] = df["pending_type"].map(order).fillna(9)
    df = df.sort_values(["_o", "company", "year", "final12_excel_row"]).drop(columns="_o")
    df.insert(0, "sno", range(1, len(df) + 1))
    return df[COLS]


def summary_df(df: pd.DataFrame) -> pd.DataFrame:
    counts = df["pending_type"].value_counts()
    return pd.DataFrame(
        [
            ["pending_total", len(df), "Only unfinished items. Copied leftover folders are not listed."],
            [
                "STILL_MISSING_FOLDER_NOT_ON_HDD",
                int(counts.get("STILL_MISSING_FOLDER_NOT_ON_HDD", 0)),
                "GREEN WEALTH 03.11.2022 folder not found on D:\\OFFICE SARASWATHI.",
            ],
            [
                "NO_TRUE_AND_NO_LISTING_HIT",
                int(counts.get("NO_TRUE_AND_NO_LISTING_HIT", 0)),
                "FINAL 12 NOT FOUND + review has no TRUE path. Staff must locate or confirm missing.",
            ],
            [
                "NO_TRUE_BUT_NAME_IN_FILE_LIST",
                int(counts.get("NO_TRUE_BUT_NAME_IN_FILE_LIST", 0)),
                "Company name appears in listing. Staff must pick the right folder. Do not auto-copy.",
            ],
            [
                "copied leftovers excluded",
                0,
                "16 leftover folders already copied from D: 2026-09-20 and rclone to DATA1. Not pending.",
            ],
        ],
        columns=["item", "count", "notes"],
    )


def legend_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["pending_type", "Why this row is still open"],
            ["what_staff_must_do", "Action for staff"],
            ["company / year / combine", "As listed in FINAL 12 / REVIEW"],
            ["mentioned_in", "FINAL 12 and/or NOT FOUND REVIEW"],
            ["source_sheet + final12_excel_row", "Tab and row in BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx"],
            ["review_excel_row", "Row on REVIEW sheet if this came from NOT FOUND REVIEW"],
            ["folder_or_path", "Folder name or path from the sheet, if any"],
            ["listing_paths", "Candidate folders from file listing (staff pick). Semicolon-separated."],
        ],
        columns=["column", "meaning"],
    )


def add_pending_tab(path: Path, df: pd.DataFrame) -> str:
    if not path.exists():
        return f"skip {path.name}"
    wb = load_workbook(path)
    write_df(wb, "PENDING", df, "pending_type", table_name="PENDINGTbl")
    if "PENDING" in wb.sheetnames:
        wb.move_sheet("PENDING", offset=0 - wb.sheetnames.index("PENDING"))
    try:
        wb.save(path)
        return str(path)
    except PermissionError:
        alt = path.with_name(path.stem + " - PENDING.xlsx")
        wb.save(alt)
        return str(alt)


def main() -> None:
    df = build_pending()
    wb = Workbook()
    default = wb.active
    wb.remove(default)
    write_df(wb, "PENDING", df, "pending_type", table_name="PendingOnlyTbl")
    write_df(wb, "SUMMARY", summary_df(df), table_name="PendingSumTbl")
    write_df(wb, "HOW_TO_READ", legend_df(), table_name="PendingHowTbl")
    wb.save(OUT)

    also = []
    also.append(add_pending_tab(TODO_XLSX, df))
    also.append(add_pending_tab(REVIEW_XLSX, df))

    print("saved", OUT)
    print("also", also)
    print("rows", len(df))
    print(df["pending_type"].value_counts().to_string())
    print(df[["sno", "pending_type", "company", "year"]].to_string(index=False))


if __name__ == "__main__":
    main()
