"""One clean workbook: the original 98 + current TO_DO only. No extra sheets."""
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
OUT = ROOT / "05-migration" / "THE_98_AND_TO_DO.xlsx"

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(color="FFFFFF", bold=True)
WRAP = Alignment(wrap_text=True, vertical="top")
GREEN = PatternFill("solid", fgColor="C6EFCE")
ORANGE = PatternFill("solid", fgColor="F4B183")
YELLOW = PatternFill("solid", fgColor="FFE699")
RED = PatternFill("solid", fgColor="FFC7CE")

HAPPENED = {
    "RESOLVED_TRUE_ADDED_PATH": "DONE — TRUE path was used and copied",
    "RESOLVED_TRUE_ON_LISTED_FOLDER": "DONE — TRUE listed folder was copied",
    "RESOLVED_TRUE_ADDED_PATH_MATCHED_BY_COMPANY": "DONE — TRUE path was used and copied",
    "NO_TRUE_BUT_NAME_IN_FILE_LIST": "TO DO — company name is in the file list; pick if that folder is right",
    "STILL_NO_TRUE": "TO DO — still no TRUE path; pick the folder",
}

FILLS_HAPPENED = {
    "DONE — TRUE path was used and copied": GREEN,
    "DONE — TRUE listed folder was copied": GREEN,
    "TO DO — company name is in the file list; pick if that folder is right": YELLOW,
    "TO DO — still no TRUE path; pick the folder": RED,
    "TO DO — copy when H: is attached": ORANGE,
}


def style_sheet(ws, name: str) -> None:
    for col in ws.columns:
        letter = get_column_letter(col[0].column)
        longest = 12
        for cell in col:
            cell.alignment = WRAP
            val = "" if cell.value is None else str(cell.value)
            longest = max(longest, min(len(val) + 2, 72))
        ws.column_dimensions[letter].width = longest
    ws.row_dimensions[1].height = 22
    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
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
    if color_col and color_col in df.columns:
        idx = list(df.columns).index(color_col) + 1
        for i, val in enumerate(df[color_col].tolist(), start=2):
            fill = FILLS_HAPPENED.get(str(val))
            if fill:
                ws.cell(i, idx).fill = fill
    style_sheet(ws, title)


def main() -> None:
    nf = pd.read_excel(ISSUES, sheet_name="NF_IN_REVIEW_NO_TRUE", dtype=str).fillna("")
    style = pd.read_excel(RESOLVED, sheet_name="REVIEW_STYLE_RESOLVED", dtype=str).fillna("")
    nf["k"] = nf["source_sheet"].str.strip() + "|" + nf["excel_row"].str.strip()
    style["k"] = style["source_sheet"].str.strip() + "|" + style["excel_row"].str.strip()
    m = nf.merge(
        style[["k", "status", "company", "year", "combine", "resolved_path", "listing_paths"]],
        on="k",
        how="left",
        suffixes=("", "_r"),
    )

    the98 = pd.DataFrame(
        {
            "what_happened": m["status"].map(HAPPENED).fillna("CHECK"),
            "company": m["orig_COMPANY NAME"].where(m["orig_COMPANY NAME"].str.strip() != "", m["company"]),
            "year": m["year"].where(m["year"].str.strip() != "", m["orig_COMBINE"]),
            "combine": m["orig_COMBINE"],
            "mentioned_in": "FINAL 12",
            "sheet": m["source_sheet"],
            "row": m["excel_row"],
            "path": m["resolved_path"].where(m["resolved_path"].str.strip() != "", m["listing_paths"]),
        }
    )
    the98["_o"] = the98["what_happened"].str.startswith("TO DO").astype(int)
    the98 = the98.sort_values(["_o", "company", "year", "row"]).drop(columns="_o")

    todo98 = the98[the98["what_happened"].str.startswith("TO DO")].copy()
    todo98 = todo98.rename(columns={"what_happened": "to_do"})

    extra = []
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
                "to_do": "TO DO — copy when H: is attached",
                "company": rec.get("company") or rowm.get("company") or "",
                "year": rec.get("year") or rowm.get("year") or "",
                "combine": rowm.get("combine") or "",
                "mentioned_in": "NOT FOUND REVIEW",
                "sheet": "REVIEW",
                "row": rowm.get("review_row") or "",
                "path": src,
            }
        )

    # listing-only rows that were not in the original 98
    open_st = style[style["status"].isin(["STILL_NO_TRUE", "NO_TRUE_BUT_NAME_IN_FILE_LIST"])].copy()
    have = set(nf["k"])
    for rec in open_st.to_dict("records"):
        k = rec["k"]
        if k in have:
            continue
        extra.append(
            {
                "to_do": (
                    "TO DO — still no TRUE path; pick the folder"
                    if rec["status"] == "STILL_NO_TRUE"
                    else "TO DO — company name is in the file list; pick if that folder is right"
                ),
                "company": rec.get("company") or "",
                "year": rec.get("year") or "",
                "combine": rec.get("combine") or "",
                "mentioned_in": "FINAL 12",
                "sheet": rec.get("source_sheet") or "",
                "row": rec.get("excel_row") or "",
                "path": rec.get("listing_paths") or rec.get("resolved_path") or "",
            }
        )

    todo = pd.concat([todo98, pd.DataFrame(extra)], ignore_index=True)
    order = {
        "TO DO — copy when H: is attached": 0,
        "TO DO — company name is in the file list; pick if that folder is right": 1,
        "TO DO — still no TRUE path; pick the folder": 2,
    }
    todo["_o"] = todo["to_do"].map(order).fillna(9)
    todo = todo.sort_values(["_o", "company", "year", "row"]).drop(columns="_o")

    counts = pd.DataFrame(
        [
            ["Original leftover (no TRUE in review)", 98, "Sheet THE_98"],
            ["Of those 98 — already copied", int(the98["what_happened"].str.startswith("DONE").sum()), "Not on TO_DO"],
            ["Of those 98 — still to do", int(the98["what_happened"].str.startswith("TO DO").sum()), "On TO_DO"],
            ["Extra to do (not in the 98) — H: drive", int((todo["to_do"] == "TO DO — copy when H: is attached").sum()), "Appended on TO_DO"],
            ["TO_DO total", len(todo), "Only unfinished work"],
        ],
        columns=["item", "count", "where"],
    )

    wb = Workbook()
    wb.remove(wb.active)
    add_df(wb, "TO_DO", todo, "to_do")
    add_df(wb, "THE_98", the98, "what_happened")
    add_df(wb, "COUNTS", counts)
    wb.save(OUT)
    print("saved", OUT)
    print("THE_98", len(the98))
    print(the98["what_happened"].value_counts().to_string())
    print("TO_DO", len(todo))
    print(todo["to_do"].value_counts().to_string())


if __name__ == "__main__":
    main()
