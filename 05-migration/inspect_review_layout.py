"""Dump REVIEW xlsx real headers, TRUE patterns, and the 98 'no TRUE' groups."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "NOT FOUND - REVIEW - ALL COMPLETED.xlsx"
FINAL = ROOT / "BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx"

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
    s = str(val).strip().upper()
    return s in {"TRUE", "X", "Y", "1"} or val in TRUE_LIKE


def main() -> None:
    wb = load_workbook(REVIEW, read_only=True, data_only=True)
    print("SHEETS", wb.sheetnames)
    for sname in wb.sheetnames:
        ws = wb[sname]
        print("\n====", sname, "max_col sample ====")
        for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
            vals = list(row[:12])
            print(i, [repr(v)[:80] if v is not None else None for v in vals])
            if i >= 8:
                break
    ws = wb["REVIEW"]
    header = None
    rows = []
    empty_streak = 0
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        vals = list(row[:12])
        if i == 1:
            header = vals
            print("\nHEADER", header)
            continue
        if all(blank(v) for v in vals):
            empty_streak += 1
            if empty_streak >= 40 and i > 100:
                break
            continue
        empty_streak = 0
        rows.append((i, vals))
    wb.close()
    print("content_rows", len(rows), "last_row", rows[-1][0] if rows else None)

    # Map by assumed completed-file order:
    # 0 SHEET, 1 MAIN_ROW, 2 COMPANY, 3 COMBINE, 4 SELECT, 5 NAME, 6 PATH, 7 NOTES
    select_vals = defaultdict(int)
    true_with_path = 0
    true_no_path = 0
    true_headerish = 0
    true_added_blank_sheet = 0
    notes_true = 0
    col4_samples = []
    for i, vals in rows:
        sel = vals[4] if len(vals) > 4 else None
        key = repr(sel)[:40]
        select_vals[key] += 1
        if is_true(sel):
            path = vals[6] if len(vals) > 6 else None
            name = vals[5] if len(vals) > 5 else None
            notes = vals[7] if len(vals) > 7 else None
            sheet = vals[0]
            if blank(path):
                true_no_path += 1
                if notes and "candidate" in str(notes).lower():
                    true_headerish += 1
            else:
                true_with_path += 1
                if blank(sheet):
                    true_added_blank_sheet += 1
            if len(col4_samples) < 15:
                col4_samples.append((i, sheet, vals[1], vals[2], sel, name, path, notes))
        if not blank(vals[7] if len(vals) > 7 else None) and is_true(vals[7]):
            notes_true += 1

    print("\nSELECT col4 value counts (top):")
    for k, n in sorted(select_vals.items(), key=lambda x: -x[1])[:20]:
        print(f"  {n:6d}  {k}")
    print("true_with_path", true_with_path)
    print("true_no_path", true_no_path)
    print("true_headerish_notes", true_headerish)
    print("true_added_blank_sheet_with_path", true_added_blank_sheet)
    print("notes_col_is_true", notes_true)
    print("sample TRUE rows:")
    for s in col4_samples:
        print(" ", s)

    # Group by inherited sheet+main_row
    last = {"sheet": None, "main": None, "company": None}
    groups = defaultdict(lambda: {"rows": [], "true_path": [], "true_any": [], "added": []})
    for i, vals in rows:
        sheet = None if blank(vals[0]) else str(vals[0]).strip()
        main = None
        if not blank(vals[1]):
            try:
                main = int(float(vals[1]))
            except Exception:
                main = None
        company = None if blank(vals[2]) else str(vals[2]).strip()
        if sheet and main is not None:
            last["sheet"] = sheet
            last["main"] = main
            if company:
                last["company"] = company
        inh = (last["sheet"], last["main"])
        rec = {
            "i": i,
            "sheet": sheet,
            "main": main,
            "company": company,
            "combine": vals[3],
            "select": vals[4],
            "name": vals[5],
            "path": vals[6],
            "notes": vals[7] if len(vals) > 7 else None,
        }
        groups[inh]["rows"].append(rec)
        if is_true(rec["select"]):
            groups[inh]["true_any"].append(rec)
            if not blank(rec["path"]):
                groups[inh]["true_path"].append(rec)
                if blank(sheet):
                    groups[inh]["added"].append(rec)

    print("\ngroups", len(groups))
    n_true_path = sum(1 for g in groups.values() if g["true_path"])
    n_true_any = sum(1 for g in groups.values() if g["true_any"])
    n_none = sum(1 for g in groups.values() if not g["true_any"])
    n_true_no_path = sum(1 for g in groups.values() if g["true_any"] and not g["true_path"])
    print("groups_with_TRUE_path", n_true_path)
    print("groups_with_any_TRUE", n_true_any)
    print("groups_TRUE_but_no_path", n_true_no_path)
    print("groups_no_TRUE_at_all", n_none)

    # Show groups with TRUE header but path on added row
    added = sum(1 for g in groups.values() if g["added"])
    print("groups_with_added_TRUE_path_blank_sheet", added)

    print("\n--- groups TRUE but no path (up to 20) ---")
    shown = 0
    for k, g in groups.items():
        if g["true_any"] and not g["true_path"]:
            print("KEY", k, "company", (g["true_any"][0].get("company") or (g["rows"][0].get("company"))))
            for rec in g["rows"][:6]:
                print("  ", rec["i"], rec["select"], rec["name"], rec["path"], rec["notes"])
            shown += 1
            if shown >= 12:
                break

    print("\n--- groups no TRUE at all (up to 15) ---")
    shown = 0
    for k, g in groups.items():
        if not g["true_any"]:
            r0 = g["rows"][0]
            names = [str(x["name"])[:50] for x in g["rows"] if not blank(x["name"])][:4]
            print("KEY", k, "company", r0.get("company"), "n_rows", len(g["rows"]), "names", names, "notes", r0.get("notes"))
            shown += 1
            if shown >= 15:
                break

    # Also check if SELECT might actually be col0 (original layout)
    print("\n--- if col0 were SELECT ---")
    c0 = defaultdict(int)
    for i, vals in rows[:30]:
        c0[repr(vals[0])[:40]] += 1
    print("first30 col0", dict(c0))


if __name__ == "__main__":
    main()
