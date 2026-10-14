r"""
Generate a REVIEW workbook containing every folder inside the exact
month path for every remaining NOT FOUND row from (12).

Input : (12).xlsx  -- to find NOT FOUND rows
Output: NOT FOUND - REVIEW.xlsx

Structure of the review workbook (single sheet 'REVIEW'):

    Column A  SHEET             (main sheet the NF row lives in)
    Column B  MAIN_ROW          (row index in the main sheet — needed to merge back)
    Column C  COMPANY
    Column D  COMBINE
    Column E  FOLDER_SCOPE      (the specific month folder we searched inside)
    Column F  CANDIDATE_NAME    (folder name only)
    Column G  CANDIDATE_PATH    (full path — this is what goes into main workbook)
    Column H  SELECT            (LEAVE BLANK — put X / Y / 1 / any mark to include)
    Column I  NOTES             (optional — free text for the user)

For every NF row we emit:
    * one header row (bold, highlighted)  — SELECT column stays blank on this row
    * one row per candidate folder in that month scope
    * a blank spacer row after

You review the file, put 'X' (or any non-blank value) in column H for
folders that belong to that company, save it, send it back, and the merge
script will append those paths to the main workbook.
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
import re
from collections import defaultdict

LISTINGS = [
    r"C:\Users\logsarav\Downloads\all_files_list (2).txt",
    r"C:\Users\logsarav\Downloads\all_files_list_2025_26.txt",
]
SRC = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx"
DST = r"C:\Users\logsarav\Downloads\NOT FOUND - REVIEW.xlsx"

MONTHS3 = {"JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL",
           "AUG", "SEP", "OCT", "NOV", "DEC"}
YEAR_RE = re.compile(r"^\d{4}-(\d{2}|\d{4})$")
CO_PREFIXES = ("E:\\BACK UP FOLDER", "E:\\2025-26\\co")
OS_PREFIXES = ("F:\\", "E:\\2025-26\\os")


def canonical_year(y):
    m = re.match(r"^(\d{4})-(\d{2,4})$", str(y or "").strip())
    if not m:
        return y
    start, end = m.group(1), m.group(2)
    if len(end) == 4:
        return f"{start}-{end[-2:]}"
    return y


def month_code(text):
    if not text:
        return None
    alpha = re.sub(r"[^A-Z]", "", str(text).upper())
    if len(alpha) >= 3 and alpha[:3] in MONTHS3:
        return alpha[:3]
    return None


def is_valid_data_line(line):
    line = line.strip()
    if not line or line.startswith("=====") or line.startswith("-----"):
        return False
    if line.startswith("E:\\BACK UP FOLDER\\"):
        return True
    if line.startswith("E:\\2025-26\\co\\") or line.startswith("E:\\2025-26\\os\\"):
        return True
    if line.startswith("F:\\") and not line.startswith("F:\\System Volume Information") \
            and not line.startswith("F:\\$RECYCLE.BIN"):
        return True
    return False


def parse_combine(combine):
    if not combine:
        return None
    parts = re.split(r"\s*>\s*", str(combine).strip())
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return None
    if not YEAR_RE.match(parts[0]) and not re.match(r"^(\d{4})-(\d{2})$", parts[0]):
        return None
    year = canonical_year(parts[0])
    second = parts[1] if len(parts) > 1 else ""
    m3 = month_code(second)
    if m3:
        month_raw = second
        folder_type = parts[2] if len(parts) > 2 else ""
    else:
        month_raw = ""
        folder_type = second
    if " - " in folder_type:
        folder_type = folder_type.split(" - ", 1)[0].strip()
    return year, month_raw, folder_type


def filter_by_drive(children, folder_type):
    ft = (folder_type or "").strip().upper()
    if ft.startswith("CO"):
        return [(p, n) for p, n in children if p.startswith(CO_PREFIXES)]
    if ft.startswith("OS"):
        return [(p, n) for p, n in children if p.startswith(OS_PREFIXES)]
    return children


def build_index():
    print("Reading listings ...", flush=True)
    dirs = set()
    for p in LISTINGS:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if not is_valid_data_line(line):
                    continue
                parts = line.strip().split("\\")
                for i in range(2, len(parts)):
                    dirs.add("\\".join(parts[:i]))

    month_children = defaultdict(list)   # (year, m3) -> [(path, name), ...]
    year_children = defaultdict(list)
    month_scope   = defaultdict(set)     # (year, m3, drive_class) -> {month_folder_path}

    for d in dirs:
        parts = d.split("\\")
        year_idx = None
        for i in range(1, min(6, len(parts))):
            if YEAR_RE.match(parts[i]):
                year_idx = i
                break
        if year_idx is None:
            continue
        year = canonical_year(parts[year_idx])
        year_children[year].append((d, parts[-1]))
        for j in range(year_idx + 1, len(parts) - 1):
            m = month_code(parts[j])
            if m:
                child_path = "\\".join(parts[: j + 2])
                child_name = parts[j + 1]
                month_children[(year, m)].append((child_path, child_name))
                # remember the month-folder path itself
                month_folder = "\\".join(parts[: j + 1])
                if d.startswith(CO_PREFIXES):
                    month_scope[(year, m, "CO")].add(month_folder)
                elif d.startswith(OS_PREFIXES):
                    month_scope[(year, m, "OS")].add(month_folder)
                break

    for tbl in (month_children, year_children):
        for k in list(tbl):
            seen, out = set(), []
            for p, n in tbl[k]:
                if p not in seen:
                    seen.add(p); out.append((p, n))
            tbl[k] = out
    return month_children, year_children, month_scope


def collect_not_found_rows(wb):
    """Return list of (sheet, row, company, combine) for every STILL NOT FOUND / NOT FOUND row."""
    out = []
    for sname in ("UPLOADED FORMS - COMPANY NAME", "COMPANY WISE"):
        if sname not in wb.sheetnames:
            continue
        ws = wb[sname]
        mc = ws.max_column
        # last col = RECHECK (vs 9), prev = CHANGE (vs 8), prev = STATUS
        status_col = mc - 2

        current_company = None
        for r in range(2, ws.max_row + 1):
            if sname == "COMPANY WISE":
                v = ws.cell(row=r, column=2).value
                if v:
                    current_company = v
                company = current_company
                combine = ws.cell(row=r, column=3).value
            else:
                company = ws.cell(row=r, column=2).value
                year_v = ws.cell(row=r, column=3).value
                mo = ws.cell(row=r, column=4).value
                ft = ws.cell(row=r, column=5).value
                combine = f"{year_v} > {mo} > {ft}" if year_v else None

            status = str(ws.cell(row=r, column=status_col).value or "").strip().upper()
            if status.startswith("NOT FOUND"):
                out.append((sname, r, company, combine))
    return out


def main():
    month_children, year_children, month_scope = build_index()
    print(f"Loading {SRC}")
    wb = openpyxl.load_workbook(SRC, data_only=True)

    nf_rows = collect_not_found_rows(wb)
    print(f"Found {len(nf_rows)} NOT FOUND rows to review")

    # Build the review workbook
    out_wb = openpyxl.Workbook()
    ws = out_wb.active
    ws.title = "REVIEW"

    headers = ["SELECT (X)", "SHEET", "MAIN_ROW", "COMPANY", "COMBINE",
               "FOLDER_SCOPE", "CANDIDATE_NAME", "CANDIDATE_PATH", "NOTES"]
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=i, value=h)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill(fill_type="solid", start_color="1F4E78", end_color="1F4E78")
        c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"

    header_fill = PatternFill(fill_type="solid", start_color="FFF2CC", end_color="FFF2CC")
    header_font = Font(bold=True)
    no_cand_fill = PatternFill(fill_type="solid", start_color="F8CBAD", end_color="F8CBAD")
    zebra_fill_a = PatternFill(fill_type="solid", start_color="FFFFFF", end_color="FFFFFF")
    zebra_fill_b = PatternFill(fill_type="solid", start_color="EAF3FF", end_color="EAF3FF")

    r = 2
    review_count = 0
    zebra_toggle = False

    for sheet, main_row, company, combine in nf_rows:
        parsed = parse_combine(combine)
        if not parsed:
            # emit a header-only row noting the issue
            for col, val in enumerate(
                ["", sheet, main_row, company or "", combine or "",
                 "(cannot parse combine)", "", "", ""], 1):
                cell = ws.cell(row=r, column=col, value=val)
                cell.fill = no_cand_fill
                cell.font = header_font
            r += 1
            continue
        year, month_raw, folder_type = parsed
        m3 = month_code(month_raw)

        # Determine drive class
        ft = (folder_type or "").strip().upper()
        drive_class = "CO" if ft.startswith("CO") else ("OS" if ft.startswith("OS") else None)

        # If no month in combine, DON'T expand the entire year (would be huge)
        # Just emit one empty row asking user to specify month/type.
        if not m3:
            note = "(no month in combine \u2014 please add month/type in the main sheet or leave as NOT FOUND)"
            row_vals = ["", sheet, main_row, company or "", combine or "",
                        "(year-only combine)", note, "", ""]
            for col, val in enumerate(row_vals, 1):
                cell = ws.cell(row=r, column=col, value=val)
                cell.fill = no_cand_fill
            r += 1
            continue

        # Get scope path(s) and candidates for (year, month, drive)
        candidates = month_children.get((year, m3), [])
        candidates = filter_by_drive(candidates, folder_type)
        scope_paths = month_scope.get((year, m3, drive_class), set()) if drive_class \
                      else {sp for cls in ("CO", "OS") for sp in month_scope.get((year, m3, cls), set())}

        scope_display = " ; ".join(sorted(scope_paths)) if scope_paths else f"(no {drive_class or 'CO/OS'} folder for {year}/{m3 or '(no month)'})"

        # ---- header row for this NF entry ----
        hdr = ["", sheet, main_row, company or "", combine or "",
               scope_display, "", "", ""]
        for col, val in enumerate(hdr, 1):
            cell = ws.cell(row=r, column=col, value=val)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(vertical="center", wrap_text=True)
        # Add candidate count in NOTES header
        ws.cell(row=r, column=9, value=f"{len(candidates)} candidate(s) — tick X to include")
        r += 1

        if not candidates:
            for col, val in enumerate(
                ["", sheet, main_row, company or "", combine or "",
                 scope_display, "(no folders in this scope)", "", ""], 1):
                cell = ws.cell(row=r, column=col, value=val)
                cell.fill = no_cand_fill
            r += 1
        else:
            zebra_toggle = not zebra_toggle
            fill = zebra_fill_b if zebra_toggle else zebra_fill_a
            for path, name in sorted(candidates, key=lambda x: x[1].upper()):
                row_vals = ["", sheet, main_row, company or "", combine or "",
                            scope_display, name, path, ""]
                for col, val in enumerate(row_vals, 1):
                    cell = ws.cell(row=r, column=col, value=val)
                    cell.fill = fill
                r += 1
                review_count += 1
        # blank spacer row
        r += 1

    # Column widths
    widths = {1: 10, 2: 30, 3: 8, 4: 42, 5: 38, 6: 50, 7: 55, 8: 90, 9: 30}
    for col, w in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = w

    out_wb.save(DST)
    print(f"Saved {DST}")
    print(f"Total NF rows       : {len(nf_rows)}")
    print(f"Total candidate rows: {review_count}")


if __name__ == "__main__":
    main()
