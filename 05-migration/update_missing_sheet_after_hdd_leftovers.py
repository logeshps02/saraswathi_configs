"""Update REMAINING_MISSING / TO_DO after D: leftover copy + rclone 2026-09-20.

Does not change REVIEW / Sheet1 history. Marks copied leftovers vs still missing.
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
FALLBACK_REVIEW = ROOT / "NOT FOUND - REVIEW - ALL COMPLETED - REMAINING MISSING.xlsx"
TODO_XLSX = ROOT / "05-migration" / "MISSING_AND_ISSUES_TO_DO.xlsx"
FULL_ROWS = ROOT / "05-migration" / "MISSING_AND_ISSUES_FULL_ROWS.xlsx"

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(color="FFFFFF", bold=True)
WRAP = Alignment(wrap_text=True, vertical="top")
FILLS = {
    "NEED_H_DRIVE": PatternFill("solid", fgColor="F4B183"),
    "STILL_MISSING_FOLDER_NOT_ON_HDD": PatternFill("solid", fgColor="FFC7CE"),
    "COPIED_FROM_D_DRIVE_2026_09_20": PatternFill("solid", fgColor="C6EFCE"),
    "NOT_A_REAL_FOLDER_NAME_ONLY": PatternFill("solid", fgColor="D9D9D9"),
    "SHORT_WRONG_2017_18_ALREADY_COPIED_CORRECT": PatternFill("solid", fgColor="C6EFCE"),
    "NO_TRUE_AND_NO_LISTING_HIT": PatternFill("solid", fgColor="FFC7CE"),
    "NO_TRUE_BUT_NAME_IN_FILE_LIST": PatternFill("solid", fgColor="FFE699"),
}

NOTE_COPIED = (
    "FOUND on D:\\OFFICE SARASWATHI (same as old H:). Copied 2026-09-20 to "
    "C:\\SARASWATHI_LEFTOVERS then rclone copy to nextcloud Backup_data/DATA1 "
    "(leftover job 187 files / 16 folders). Not missing."
)
NOTE_COMBINED = (
    "Covered by the combined 2017-18 ';forms' folder. That folder was also copied "
    "from D: on 2026-09-20 and rclone'd to Backup_data/DATA1. Not missing."
)
NOTE_SHORT = (
    "Sheet had the short/wrong folder name. Real folder has extra forms after ';'. "
    "Correct folder copied from D: on 2026-09-20 and rclone'd to Backup_data/DATA1. Not missing."
)
NOTE_GREEN = (
    "STILL MISSING. Excel name UPLOADED ON 03.11.2022-GREEN WEALTH AGRO INDIA LIMITED_"
    "MGT-7_19-20, 20-21 was not found on D:\\OFFICE SARASWATHI. Nearby different folder "
    "UPLOADED ON 24.09.2022 GREEN WEALTH AGRO INDIA LIMITED-AOC-4, MGT-14 was NOT copied "
    "(different job). Staff must locate the 03.11.2022 folder."
)

COPIED_BY_LOG_ROW = {
    "157": {
        "d": r"D:\OFFICE SARASWATHI\2024-25\SEARCH AND STATUS REPORT\ADR PLASTICS PRIVATE LIMITED-03.06.2024",
        "dest": r"ADR PLASTIC PRIVATE LIMITED\2024-25\ADR PLASTICS PRIVATE LIMITED-03.06.2024",
    },
    "1111": {
        "d": r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\MARCH-18\Uploaded on 28 & 29.03.2018 CONCRETIA ROCK PRODUCTS PRIVATE LIMITED- MGT-14 & SH-7",
        "dest": r"CONCRETIA ROCK PRODUCTS PRIVATE LIMITED\2017-18\Uploaded on 28 & 29.03.2018 CONCRETIA ROCK PRODUCTS PRIVATE LIMITED- MGT-14 & SH-7",
    },
    "3250": {
        "d": r"D:\OFFICE SARASWATHI\2024-25\RESOLUTIONS\1.BANK ACCOUNT OPENING RESOLUTIONS\MYSTEVA SOLAR GREEN ENERGY PRIVATE LIMITED",
        "dest": r"MYSTEVA SOLAR GREEN ENERGY PRIVATE LIMITED\2024-25\MYSTEVA SOLAR GREEN ENERGY PRIVATE LIMITED",
    },
    "3251": {
        "d": r"D:\OFFICE SARASWATHI\2024-25\RESOLUTIONS\2.GST RESOLUTIONS\MYSTEVA SOLAR GREEN ENERGY PRIVATE LIMITED-GST RESOLUTION",
        "dest": r"MYSTEVA SOLAR GREEN ENERGY PRIVATE LIMITED\2024-25\MYSTEVA SOLAR GREEN ENERGY PRIVATE LIMITED-GST RESOLUTION",
    },
    "1752": {
        "d": r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\OCTOBER-17\Uploaded on 10.10.17 GEOMEO INFORMATICS PRIVATE LIMITED-AOC-4;MGT-7;ADT-1",
        "dest": r"GEOMEO INFORMATICS PRIVATE LIMITED\2017-18\Uploaded on 10.10.17 GEOMEO INFORMATICS PRIVATE LIMITED-AOC-4;MGT-7;ADT-1",
    },
    "3529": {
        "d": r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\SEPTEMBER-17\Uploaded on 04.09.2017 ONDEOS TECHNOLOGIES PRIVATE LIMITED-MGT-14;STK-2",
        "dest": r"ONDEOS TECHNOLOGIES PRIVATE LIMITED\2017-18\Uploaded on 04.09.2017 ONDEOS TECHNOLOGIES PRIVATE LIMITED-MGT-14;STK-2",
    },
    "4275": {
        "d": r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\AUGUEST-17\Uploaded on 24.08.2017QUADRATIC STRUCTURE INDIA PRIVATE LIMITED-MGT-14;SH-7",
        "dest": r"QUADRATIC STRUCTURE INDIA PRIVATE LIMITED\2017-18\Uploaded on 24.08.2017QUADRATIC STRUCTURE INDIA PRIVATE LIMITED-MGT-14;SH-7",
    },
    "5231": {
        "d": r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\SEPTEMBER-17\Uploaded on 01.09.2017 SKYWING HOLIDAYS PRIVATE LIMITED-AOC-4;MGT-7",
        "dest": r"SKYWING HOLIDAYS PRIVATE LIMITED\2017-18\Uploaded on 01.09.2017 SKYWING HOLIDAYS PRIVATE LIMITED-AOC-4;MGT-7",
    },
    "5232": {
        "d": r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\AUGUEST-17\Uploaded on 18.08.2017 SKYWING HOLIDAYS PRIVATE LIMITED AOC-4;MGT-7",
        "dest": r"SKYWING HOLIDAYS PRIVATE LIMITED\2017-18\Uploaded on 18.08.2017 SKYWING HOLIDAYS PRIVATE LIMITED AOC-4;MGT-7",
    },
    "5491": {
        "d": r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\OCTOBER-17\Uploaded on 06.10.17&07.10.17 SRI YANNARKAY SERVICERS LTD-MGT-7;AOC-4",
        "dest": r"SRI YANNARKAY SERVICERS LIMITED\2017-18\Uploaded on 06.10.17&07.10.17 SRI YANNARKAY SERVICERS LTD-MGT-7;AOC-4",
    },
}

NAME_ONLY_COVERED = {
    "1750": "1752",
    "1751": "1752",
    "3528": "3529",
    "4270": "4275",
    "5230": "5231",
    "5490": "5491",
}


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
    table = Table(displayName=name.replace(" ", "_")[:28] + "UpdTbl", ref=ref)
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    try:
        ws.add_table(table)
    except Exception:
        pass


def update_remaining(df: pd.DataFrame) -> pd.DataFrame:
    out_rows = []
    for rec in df.to_dict("records"):
        rec = {k: ("" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)) for k, v in rec.items()}
        log = str(rec.get("copy_log_row") or "").strip()
        src = str(rec.get("source_path_as_in_sheet") or "")
        company = rec.get("company") or ""
        rec["status_2026_09_20"] = rec.get("status_2026_09_20") or ""
        rec["copied_from_D"] = rec.get("copied_from_D") or ""
        rec["dest_on_DATA1"] = rec.get("dest_on_DATA1") or ""

        if "GREEN WEALTH" in company or "03.11.2022-GREEN WEALTH" in src:
            rec["still_needed"] = "YES"
            rec["category"] = "STILL_MISSING_FOLDER_NOT_ON_HDD"
            rec["what_to_do"] = "YES — still missing; folder name not on D:"
            rec["status_2026_09_20"] = "STILL MISSING"
            rec["copied_from_D"] = ""
            rec["dest_on_DATA1"] = ""
            rec["notes"] = NOTE_GREEN
        elif log in COPIED_BY_LOG_ROW:
            hit = COPIED_BY_LOG_ROW[log]
            rec["still_needed"] = "NO"
            rec["category"] = "COPIED_FROM_D_DRIVE_2026_09_20"
            rec["what_to_do"] = "NO — copied from D: 2026-09-20 and rclone to DATA1"
            rec["status_2026_09_20"] = "COPIED + RCLONE DONE"
            rec["copied_from_D"] = hit["d"]
            rec["dest_on_DATA1"] = hit["dest"]
            rec["notes"] = NOTE_COPIED
        elif log in NAME_ONLY_COVERED:
            cover = COPIED_BY_LOG_ROW[NAME_ONLY_COVERED[log]]
            rec["still_needed"] = "NO"
            rec["category"] = "NOT_A_REAL_FOLDER_NAME_ONLY"
            rec["what_to_do"] = "NO — leave; combined folder copied from D:"
            rec["status_2026_09_20"] = "COVERED BY COMBINED FOLDER COPIED"
            rec["copied_from_D"] = cover["d"]
            rec["dest_on_DATA1"] = cover["dest"]
            rec["notes"] = NOTE_COMBINED
        elif rec.get("category") == "SHORT_WRONG_2017_18_ALREADY_COPIED_CORRECT":
            rec["still_needed"] = "NO"
            rec["what_to_do"] = "NO — already copied under the correct longer name (also from D: 2026-09-20)"
            rec["status_2026_09_20"] = "COPIED + RCLONE DONE"
            rec["notes"] = NOTE_SHORT
        out_rows.append(rec)

    out = pd.DataFrame(out_rows)
    order = {
        "STILL_MISSING_FOLDER_NOT_ON_HDD": 0,
        "COPIED_FROM_D_DRIVE_2026_09_20": 1,
        "NOT_A_REAL_FOLDER_NAME_ONLY": 2,
        "SHORT_WRONG_2017_18_ALREADY_COPIED_CORRECT": 3,
    }
    out["_o"] = out["category"].map(order).fillna(9)
    out = out.sort_values(["_o", "company", "year", "final12_excel_row"]).drop(columns="_o")
    cols = [
        "still_needed",
        "category",
        "what_to_do",
        "status_2026_09_20",
        "mentioned_in_file",
        "mentioned_in",
        "origin",
        "source_sheet_in_final12",
        "final12_excel_row",
        "review_sheet",
        "review_excel_row",
        "company",
        "year",
        "combine",
        "source_path_as_in_sheet",
        "copied_from_D",
        "dest_on_DATA1",
        "dest_relative_in_F_Final",
        "correct_source_if_any",
        "copy_log_row",
        "notes",
    ]
    for c in cols:
        if c not in out.columns:
            out[c] = ""
    return out[cols]


def summary_df(copy_df: pd.DataFrame) -> pd.DataFrame:
    still = int((copy_df["still_needed"] == "YES").sum())
    copied = int((copy_df["category"] == "COPIED_FROM_D_DRIVE_2026_09_20").sum())
    name_only = int((copy_df["category"] == "NOT_A_REAL_FOLDER_NAME_ONLY").sum())
    short = int((copy_df["category"] == "SHORT_WRONG_2017_18_ALREADY_COPIED_CORRECT").sum())
    return pd.DataFrame(
        [
            [
                "STILL_MISSING_FOLDER_NOT_ON_HDD",
                still,
                "GREEN WEALTH 03.11.2022 MGT-7 19-20, 20-21. Not on D:. Only copy still missing from the leftover list.",
            ],
            [
                "COPIED_FROM_D_DRIVE_2026_09_20",
                copied,
                "Old H: / leftover folders found on D: and rclone'd to Backup_data/DATA1 (16 folders, 187 files).",
            ],
            [
                "NOT_A_REAL_FOLDER_NAME_ONLY",
                name_only,
                "Form name only (ADT-1/MGT-7/STK-2/SH-7/AOC-4). Combined 2017-18 folder copied. Leave.",
            ],
            [
                "SHORT_WRONG_2017_18_ALREADY_COPIED_CORRECT",
                short,
                "Wrong/short 2017-18 name. Correct ;forms folder copied from D: and rclone'd.",
            ],
            [
                "Long-path / path-not-found leftovers (KIRUBA, PSN, PRIDE x2, SWAMI x2)",
                0,
                "DONE 2026-09-20 from D:. rclone leftovers. Dest uses F:\\f company spelling (KIRUBA without PALANIYAPPAN suffix; SWAMI HOSIPITAL typo).",
            ],
            [
                "THIRUKONDA SUBRAMANIAN SIVAKUMAR DIR-3 KYC",
                0,
                "Not a missing file. Copied under _UNSORTED\\THIRUKONDA SUBRAMANIAN SIVAKUMAR\\2026-27. Staff must name the company.",
            ],
            [
                "REVIEW leftover — no TRUE, name in listing",
                19,
                "Unchanged. Not in leftover HDD copy. Staff pick folder. See REVIEW_STILL_OPEN / TO_DO.",
            ],
            [
                "REVIEW leftover — still no TRUE",
                14,
                "Unchanged. LITTLE MOPPET / N.R.K INFRA / NEOMAX / PRANAVSREE. See REVIEW_STILL_OPEN / TO_DO.",
            ],
        ],
        columns=["item", "count", "notes"],
    )


def update_todo(path: Path) -> Path:
    wb = load_workbook(path)
    ws = wb["TO_DO"]
    rows = list(ws.iter_rows(values_only=True))
    header = list(rows[0])
    keep = []
    for row in rows[1:]:
        rec = dict(zip(header, row))
        todo = str(rec.get("to_do") or "")
        if todo.startswith("Copy when H:"):
            continue
        if "GREEN WEALTH" in str(rec.get("company") or "").upper():
            continue
        if todo.startswith("Still missing"):
            continue
        keep.append(rec)

    green = {
        "to_do": "Still missing — folder not on HDD",
        "company": "GREEN WEALTH AGRO INDIA LIMITED",
        "year": "2022-23",
        "mentioned_in": "NOT FOUND REVIEW",
        "sheet": "REVIEW",
        "row": "1169",
        "path": "UPLOADED ON 03.11.2022-GREEN WEALTH AGRO INDIA LIMITED_MGT-7_19-20, 20-21",
        "note": NOTE_GREEN,
    }
    df = pd.DataFrame([green] + keep)
    order = {
        "Still missing — folder not on HDD": 0,
        "Name is in file list — pick if it is the right folder": 1,
        "Still no TRUE path — pick the folder": 2,
    }
    df["_o"] = df["to_do"].map(order).fillna(9)
    df = df.sort_values(["_o", "company", "year", "row"]).drop(columns="_o")
    write_df(wb, "TO_DO", df)
    if "TO_DO" in wb.sheetnames:
        wb.move_sheet("TO_DO", offset=0 - wb.sheetnames.index("TO_DO"))
    out = path
    try:
        wb.save(out)
    except PermissionError:
        out = path.with_name(path.stem + " - UPDATED.xlsx")
        wb.save(out)
    return out


def save_review(wb, out_path: Path, copy_df: pd.DataFrame) -> Path:
    write_df(wb, "REMAINING_MISSING", copy_df, "category")
    write_df(wb, "REMAINING_SUMMARY", summary_df(copy_df))
    order_names = [
        "REVIEW",
        "Sheet1",
        "REMAINING_SUMMARY",
        "REMAINING_MISSING",
        "REVIEW_STILL_OPEN",
        "HOW_TO_READ",
    ]
    for i, n in enumerate(order_names):
        if n in wb.sheetnames:
            wb.move_sheet(n, offset=i - wb.sheetnames.index(n))
    try:
        wb.save(out_path)
        return out_path
    except PermissionError:
        alt = FALLBACK_REVIEW if out_path != FALLBACK_REVIEW else ROOT / "NOT FOUND - REVIEW - ALL COMPLETED - REMAINING MISSING UPDATED.xlsx"
        wb.save(alt)
        return alt


def main() -> None:
    src = REVIEW_XLSX if REVIEW_XLSX.exists() else FALLBACK_REVIEW
    remaining = pd.read_excel(src, sheet_name="REMAINING_MISSING", dtype=str).fillna("")
    copy_df = update_remaining(remaining)

    saved = []
    for path in [REVIEW_XLSX, FALLBACK_REVIEW]:
        if not path.exists():
            continue
        wb = load_workbook(path)
        saved.append(str(save_review(wb, path, copy_df)))

    todo_saved = None
    if TODO_XLSX.exists():
        todo_saved = str(update_todo(TODO_XLSX))
    if FULL_ROWS.exists():
        try:
            todo_saved2 = str(update_todo(FULL_ROWS))
        except KeyError:
            todo_saved2 = "FULL_ROWS has no TO_DO"
        saved.append(todo_saved2)

    print("saved_review", saved)
    print("saved_todo", todo_saved)
    print("still_needed")
    print(copy_df[copy_df["still_needed"] == "YES"][["company", "year", "source_path_as_in_sheet"]].to_string(index=False))
    print("category")
    print(copy_df["category"].value_counts().to_string())


if __name__ == "__main__":
    main()
