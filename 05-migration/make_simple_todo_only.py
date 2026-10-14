"""Rebuild THE_98_AND_TO_DO.xlsx: open items only, with file/row/reason."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(r"c:\Users\U.lalitha navya sri\Downloads\Logesh files")
ISSUES = ROOT / "05-migration" / "MISSING_AND_ISSUES_FULL_ROWS.xlsx"
RESOLVED = ROOT / "05-migration" / "REVIEW_RESOLVED_CORRECT.xlsx"
MISS = ROOT / "05-migration" / "COPY_FAILED_AND_MISSING.csv"
MAP = ROOT / "05-migration" / "STRUCTURED_COPY_MAP_FINAL.csv"
REVIEW = ROOT / "NOT FOUND - REVIEW - ALL COMPLETED.xlsx"
REVIEW_CSV = ROOT / "NOT FOUND - REVIEW - ALL COMPLETED-REVIEW,NOT FOUND - REVIEW - ALL COMPLETED-Sheet1" / "NOT FOUND - REVIEW - ALL COMPLETED-REVIEW.csv"
OUT = ROOT / "05-migration" / "STILL_TO_DO.xlsx"
LOG = ROOT / "05-migration" / "_todo_build_log.txt"

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(color="FFFFFF", bold=True)
WRAP = Alignment(wrap_text=True, vertical="top")
ORANGE = PatternFill("solid", fgColor="F4B183")
YELLOW = PatternFill("solid", fgColor="FFE699")
RED = PatternFill("solid", fgColor="FFC7CE")
FILLS = {
    "Copy when H: is attached": ORANGE,
    "Path is in file list — not copied": YELLOW,
    "No folder picked yet": RED,
}


def style_sheet(ws, name: str, color_col: str | None, cols: list[str]) -> None:
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
    if color_col and color_col in cols:
        idx = cols.index(color_col) + 1
        for i in range(2, ws.max_row + 1):
            fill = FILLS.get(str(ws.cell(i, idx).value or ""))
            if fill:
                ws.cell(i, idx).fill = fill
    ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"
    t = Table(displayName=name[:20] + "Tbl", ref=ref)
    t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    try:
        ws.add_table(t)
    except Exception:
        pass


def add_df(wb, title: str, df: pd.DataFrame, color_col: str | None = None) -> None:
    ws = wb.create_sheet(title)
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(list(r))
    style_sheet(ws, title, color_col, list(df.columns))


def review_row_for(rev: pd.DataFrame, sheet: str, excel_row: str) -> str:
    if rev.empty:
        return ""
    hit = rev[(rev["SHEET"].str.strip() == str(sheet).strip()) & (rev["MAIN_ROW"].str.strip() == str(excel_row).strip())]
    if hit.empty:
        return ""
    # Excel row numbers in REVIEW: header is 1, data starts at 2 → index+2
    nums = sorted({int(i) + 2 for i in hit.index.tolist()})
    if not nums:
        return ""
    if len(nums) == 1:
        return str(nums[0])
    return f"{nums[0]}-{nums[-1]} ({len(nums)} lines)"


def main() -> None:
    nf = pd.read_excel(ISSUES, sheet_name="NF_IN_REVIEW_NO_TRUE", dtype=str).fillna("")
    style = pd.read_excel(RESOLVED, sheet_name="REVIEW_STYLE_RESOLVED", dtype=str).fillna("")
    nf["k"] = nf["source_sheet"].str.strip() + "|" + nf["excel_row"].str.strip()
    style["k"] = style["source_sheet"].str.strip() + "|" + style["excel_row"].str.strip()

    rev = pd.DataFrame(columns=["SHEET", "MAIN_ROW"])
    rev_ok = False
    err = ""
    try:
        rev = pd.read_csv(REVIEW_CSV, dtype=str).fillna("")
        rev.columns = list(rev.columns)
        # expected first cols
        if "SHEET" not in rev.columns and len(rev.columns) >= 2:
            rev = rev.rename(columns={rev.columns[0]: "SHEET", rev.columns[1]: "MAIN_ROW"})
        rev = rev[rev["SHEET"].astype(str).str.strip() != ""].copy()
        rev_ok = True
        err = f"csv rows {len(rev)}"
    except Exception as e:
        err = f"csv: {e}"
    LOG.write_text(f"review_ok={rev_ok} {err}\n", encoding="utf-8")

    m = nf.merge(
        style[["k", "status", "company", "year", "combine", "listing_paths", "listing_name_hits", "true_review_rows"]],
        on="k",
        how="left",
        suffixes=("", "_r"),
    )
    open98 = m[m["status"].isin(["STILL_NO_TRUE", "NO_TRUE_BUT_NAME_IN_FILE_LIST"])].copy()

    rows98 = []
    for rec in open98.to_dict("records"):
        st = rec.get("status") or ""
        listing = str(rec.get("listing_paths") or "").strip()
        if st == "NO_TRUE_BUT_NAME_IN_FILE_LIST":
            issue = "Path is in file list — not copied"
            reason = (
                "FINAL 12 said NOT FOUND. Review did not tick TRUE for this company/year, "
                "so it was not copied. A folder with this company name exists in the file list — "
                "confirm if that is the right folder, then we can copy it."
            )
            path = listing
        else:
            issue = "No folder picked yet"
            reason = (
                "FINAL 12 said NOT FOUND. Review also has no TRUE path, and this company name "
                "was not found as a folder in the file list. Need the correct folder path."
            )
            path = ""
        sheet = rec.get("source_sheet") or ""
        excel_row = rec.get("excel_row") or ""
        rows98.append(
            {
                "issue": issue,
                "reason_not_done": reason,
                "company": rec.get("orig_COMPANY NAME") or rec.get("company") or "",
                "year": rec.get("year") or "",
                "combine": rec.get("orig_COMBINE") or rec.get("combine") or "",
                "mentioned_in_FINAL_12": "YES",
                "FINAL_12_sheet": sheet,
                "FINAL_12_row": excel_row,
                "mentioned_in_NOT_FOUND_REVIEW": "YES — listed, but no TRUE tick",
                "REVIEW_sheet": "REVIEW",
                "REVIEW_row": review_row_for(rev, sheet, excel_row) if rev_ok else "",
                "path_if_any": path,
            }
        )
    df98 = pd.DataFrame(rows98)
    df98["_o"] = df98["issue"].map({"Path is in file list — not copied": 0, "No folder picked yet": 1}).fillna(9)
    df98 = df98.sort_values(["_o", "company", "year", "FINAL_12_row"]).drop(columns="_o")

    # extras not in original 98
    extra = []
    have = set(nf["k"])
    open_st = style[style["status"].isin(["STILL_NO_TRUE", "NO_TRUE_BUT_NAME_IN_FILE_LIST"])]
    for rec in open_st.to_dict("records"):
        if rec["k"] in have:
            continue
        st = rec.get("status") or ""
        listing = str(rec.get("listing_paths") or "").strip()
        sheet = rec.get("source_sheet") or ""
        excel_row = rec.get("excel_row") or ""
        if st == "NO_TRUE_BUT_NAME_IN_FILE_LIST":
            issue = "Path is in file list — not copied"
            reason = (
                "FINAL 12 said NOT FOUND. Review did not tick TRUE. "
                "A folder with this company name exists in the file list — confirm if it is right, then copy."
            )
        else:
            issue = "No folder picked yet"
            reason = (
                "FINAL 12 said NOT FOUND. Review has no TRUE path and the name was not found in the file list."
            )
        extra.append(
            {
                "issue": issue,
                "reason_not_done": reason,
                "company": rec.get("company") or "",
                "year": rec.get("year") or "",
                "combine": rec.get("combine") or "",
                "mentioned_in_FINAL_12": "YES",
                "FINAL_12_sheet": sheet,
                "FINAL_12_row": excel_row,
                "mentioned_in_NOT_FOUND_REVIEW": "YES — listed, but no TRUE tick",
                "REVIEW_sheet": "REVIEW",
                "REVIEW_row": review_row_for(rev, sheet, excel_row) if rev_ok else "",
                "path_if_any": listing,
                "from_original_98": "NO — extra leftover",
            }
        )

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
        rowm = hit.iloc[0].to_dict() if not hit.empty else {}
        extra.append(
            {
                "issue": "Copy when H: is attached",
                "reason_not_done": (
                    "Path is known and was marked TRUE in NOT FOUND REVIEW. "
                    "It was not copied because drive H: (OFFICE SARASWATHI) was not attached on the backup PC."
                ),
                "company": rec.get("company") or rowm.get("company") or "",
                "year": rec.get("year") or rowm.get("year") or "",
                "combine": rowm.get("combine") or "",
                "mentioned_in_FINAL_12": "YES",
                "FINAL_12_sheet": rec.get("source_sheet") or rowm.get("source_sheet") or "",
                "FINAL_12_row": rec.get("excel_row") or rowm.get("excel_row") or "",
                "mentioned_in_NOT_FOUND_REVIEW": "YES — TRUE",
                "REVIEW_sheet": "REVIEW",
                "REVIEW_row": rowm.get("review_row") or "",
                "path_if_any": src,
                "from_original_98": "NO — copy leftover (H: drive)",
            }
        )

    todo98 = df98.copy()
    todo98["from_original_98"] = "YES"
    todo = pd.concat([todo98, pd.DataFrame(extra)], ignore_index=True)
    order = {
        "Copy when H: is attached": 0,
        "Path is in file list — not copied": 1,
        "No folder picked yet": 2,
    }
    todo["_o"] = todo["issue"].map(order).fillna(9)
    todo = todo.sort_values(["_o", "from_original_98", "company", "year", "FINAL_12_row"]).drop(columns="_o")

    counts = pd.DataFrame(
        [
            ["Original 98", 98, "66 already copied — removed from this file"],
            ["Still open from the 98", len(df98), "Sheet STILL_OPEN_FROM_98"],
            ["Extra not in the 98 (H: + other leftover)", len(todo) - len(df98), "On TO_DO only"],
            ["TO_DO total", len(todo), "Only unfinished work"],
        ],
        columns=["item", "count", "note"],
    )

    wb = Workbook()
    wb.remove(wb.active)
    add_df(wb, "TO_DO", todo, "issue")
    add_df(wb, "STILL_OPEN_FROM_98", df98, "issue")
    add_df(wb, "COUNTS", counts)
    wb.save(OUT)
    msg = (
        f"saved {OUT}\n"
        f"STILL_OPEN_FROM_98 {len(df98)}\n{df98['issue'].value_counts().to_string()}\n"
        f"TO_DO {len(todo)}\n{todo['issue'].value_counts().to_string()}\n"
        f"review_ok {rev_ok} review_rows {len(rev)}\n"
    )
    LOG.write_text(msg, encoding="utf-8")
    print(msg)


if __name__ == "__main__":
    main()
