"""Add one simple TO_DO sheet to MISSING_AND_ISSUES_FULL_ROWS.xlsx.

Only unfinished items. No copied/resolved rows. Few columns.
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
ISSUES = ROOT / "05-migration" / "MISSING_AND_ISSUES_FULL_ROWS.xlsx"
RESOLVED = ROOT / "05-migration" / "REVIEW_RESOLVED_CORRECT.xlsx"
MISS = ROOT / "05-migration" / "COPY_FAILED_AND_MISSING.csv"
MAP = ROOT / "05-migration" / "STRUCTURED_COPY_MAP_FINAL.csv"
FALLBACK = ROOT / "05-migration" / "MISSING_AND_ISSUES_TO_DO.xlsx"

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(color="FFFFFF", bold=True)
WRAP = Alignment(wrap_text=True, vertical="top")


def write_df(wb, name: str, df: pd.DataFrame) -> None:
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name, 0)
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(list(r))
    for col in ws.columns:
        letter = get_column_letter(col[0].column)
        longest = 12
        for cell in col:
            cell.alignment = WRAP
            val = "" if cell.value is None else str(cell.value)
            longest = max(longest, min(len(val) + 2, 70))
        ws.column_dimensions[letter].width = longest
    ws.row_dimensions[1].height = 22
    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"
    t = Table(displayName="TO_DO_Tbl", ref=ref)
    t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    try:
        ws.add_table(t)
    except Exception:
        pass


def main() -> None:
    rows = []

    miss = pd.read_csv(MISS, dtype=str).fillna("")
    mp = pd.read_csv(MAP, dtype=str).fillna("")
    h = miss[
        (miss["kind"] == "MISSING_SOURCE")
        & miss["source_path"].str.startswith(r"H:\OFFICE SARASWATHI")
    ]
    for rec in h.to_dict("records"):
        src = rec["source_path"]
        dest = rec["dest_relative"]
        hit = mp[(mp["source_path"] == src) & (mp["dest_relative"] == dest)]
        m = hit.iloc[0].to_dict() if not hit.empty else {}
        origin = rec.get("origin") or m.get("origin") or ""
        if str(origin).startswith("REVIEW"):
            mentioned = "NOT FOUND REVIEW"
            sheet = "REVIEW"
            row = m.get("review_row") or ""
            also = f"FINAL 12 / {rec.get('source_sheet') or m.get('source_sheet') or ''} / row {rec.get('excel_row') or m.get('excel_row') or ''}"
        else:
            mentioned = "FINAL 12"
            sheet = rec.get("source_sheet") or m.get("source_sheet") or ""
            row = rec.get("excel_row") or m.get("excel_row") or ""
            also = ""
        rows.append(
            {
                "to_do": "Copy when H: is attached",
                "company": rec.get("company") or m.get("company") or "",
                "year": rec.get("year") or m.get("year") or "",
                "mentioned_in": mentioned,
                "sheet": sheet,
                "row": row,
                "path": src,
                "note": also.strip(),
            }
        )

    style = pd.read_excel(RESOLVED, sheet_name="REVIEW_STYLE_RESOLVED", dtype=str).fillna("")
    open_st = style[style["status"].isin(["STILL_NO_TRUE", "NO_TRUE_BUT_NAME_IN_FILE_LIST"])]
    for rec in open_st.to_dict("records"):
        st = rec.get("status") or ""
        if st == "STILL_NO_TRUE":
            todo = "Still no TRUE path — pick the folder"
            path = ""
            note = ""
        else:
            todo = "Name is in file list — pick if it is the right folder"
            path = rec.get("listing_paths") or ""
            note = ""
        rows.append(
            {
                "to_do": todo,
                "company": rec.get("company") or "",
                "year": rec.get("year") or "",
                "mentioned_in": "FINAL 12",
                "sheet": rec.get("source_sheet") or "",
                "row": rec.get("excel_row") or "",
                "path": path,
                "note": note,
            }
        )

    df = pd.DataFrame(rows)
    order = {
        "Copy when H: is attached": 0,
        "Name is in file list — pick if it is the right folder": 1,
        "Still no TRUE path — pick the folder": 2,
    }
    df["_o"] = df["to_do"].map(order).fillna(9)
    df = df.sort_values(["_o", "company", "year", "row"]).drop(columns="_o")
    # drop empty note column if unused
    if (df["note"].astype(str).str.strip() == "").all():
        df = df.drop(columns=["note"])
    else:
        df["note"] = df["note"].where(df["note"].astype(str).str.strip() != "", "")

    out = ISSUES
    try:
        wb = load_workbook(ISSUES)
    except PermissionError:
        wb = load_workbook(ISSUES)
        out = FALLBACK
    write_df(wb, "TO_DO", df)
    try:
        wb.save(out)
    except PermissionError:
        out = FALLBACK
        wb.save(out)
    print("saved", out)
    print("rows", len(df))
    print(df["to_do"].value_counts().to_string())


if __name__ == "__main__":
    main()
