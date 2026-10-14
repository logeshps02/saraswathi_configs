"""Check if the copy map put REVIEW_TRUE folders under a different company."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAP = Path(__file__).resolve().parent / "STRUCTURED_COPY_MAP_FINAL.csv"
REVIEW = ROOT / "NOT FOUND - REVIEW - ALL COMPLETED.xlsx"

from openpyxl import load_workbook

TRUE_LIKE = {True, "TRUE", "True", "true", "X", "x", "Y", "y", "1", 1, 1.0}


def blank(val) -> bool:
    if val is None:
        return True
    if isinstance(val, float) and str(val) == "nan":
        return True
    return str(val).strip() == ""


def is_true(val) -> bool:
    if val is True:
        return True
    if val is False or val is None:
        return False
    return str(val).strip().upper() in {"TRUE", "X", "Y", "1"} or val in TRUE_LIKE


def company_key(name) -> str:
    if blank(name):
        return ""
    s = str(name).upper()
    s = s.replace("PRIVATELIMITED", "PRIVATE LIMITED")
    s = s.replace("PRIVATELTD", "PRIVATE LTD")
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace(" PRIVATE LIMITED", " PVT LTD")
    s = s.replace(" LIMITED", " LTD")
    return s


def tokens_norm(name) -> set[str]:
    stop = {"PVT", "LTD", "OPC", "AND", "THE", "PRIVATE", "LIMITED"}
    out = set()
    for t in company_key(name).split():
        if t in stop:
            continue
        t = t.replace("0", "O")
        if len(t) > 4 and t.endswith("S"):
            t = t[:-1]
        out.add(t)
    return out


def main() -> None:
    with MAP.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    print("copy_map_rows", len(rows))
    by_origin = defaultdict(int)
    for r in rows:
        by_origin[r.get("origin") or ""] += 1
    print("origins", dict(by_origin))

    review_true = [r for r in rows if (r.get("origin") or "") == "REVIEW_TRUE"]
    print("REVIEW_TRUE rows in copy map", len(review_true))

    weak = [r for r in review_true if "company_name_weak_in_source_path" in (r.get("warnings") or "")]
    print("REVIEW_TRUE with weak company-in-path warning", len(weak))

    # Compare dest_company vs source folder name tokens
    mismatch = []
    for r in review_true:
        dest_co = r.get("dest_company") or r.get("company") or ""
        src = r.get("source_path") or ""
        folder = src.rstrip("\\").split("\\")[-1]
        want = tokens_norm(dest_co)
        have = tokens_norm(folder)
        if not want:
            mismatch.append(("empty_dest_company", r))
            continue
        # require at least 1 significant dest token in folder, or 2 if dest has 2+
        sig = [t for t in want if len(t) >= 4]
        if not sig:
            sig = list(want)
        hits = [t for t in sig if t in have]
        need = 1 if len(sig) <= 2 else 2
        if len(hits) < min(need, len(sig)):
            mismatch.append(("dest_vs_folder", r, dest_co, folder, hits, sig))

    print("REVIEW_TRUE dest-company vs folder-name weak", len(mismatch))
    for item in mismatch[:40]:
        if item[0] == "dest_vs_folder":
            _, r, dest_co, folder, hits, sig = item
            print(f"  dest={dest_co[:80]}")
            print(f"    folder={folder[:100]}")
            print(f"    hits={hits} need_from={sig[:8]} excel_row={r.get('excel_row')} review_row={r.get('review_row')}")
        else:
            print(" ", item[0], item[1].get("source_path"))

    # Cross-company inherit risk: added TRUE with blank company would inherit last.
    # Load review TRUE+path and see if dest company in map equals the TRUE row company
    # when TRUE row company is filled and different from previous header.
    wb = load_workbook(REVIEW, read_only=True, data_only=True)
    ws = wb["REVIEW"]
    last = {"sheet": None, "main": None, "company": None}
    inherit_diff = []
    true_n = 0
    empty_streak = 0
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if i == 1:
            continue
        vals = list(row[:8]) + [None] * 8
        sheet, main_row, company, combine, select, cand_name, cand_path, notes = vals[:8]
        if all(blank(v) for v in (sheet, main_row, company, combine, cand_name, cand_path, notes)):
            empty_streak += 1
            if empty_streak >= 20 and i > 50:
                break
            continue
        empty_streak = 0
        if not blank(sheet) and not blank(main_row):
            last["sheet"] = str(sheet).strip()
            try:
                last["main"] = int(float(main_row))
            except Exception:
                last["main"] = None
            if not blank(company):
                last["company"] = str(company).strip()
        if not is_true(select) or blank(cand_path):
            continue
        true_n += 1
        row_co = None if blank(company) else str(company).strip()
        inh_co = last["company"]
        if row_co and inh_co and company_key(row_co) != company_key(inh_co) and blank(sheet):
            inherit_diff.append(
                {
                    "review_row": i,
                    "true_company": row_co,
                    "prev_header_company": inh_co,
                    "path": str(cand_path).strip(),
                    "blank_sheet": blank(sheet),
                }
            )
        if row_co:
            last["company"] = row_co
    wb.close()
    print("\nTRUE+path review rows", true_n)
    print("added TRUE rows where COMPANY differs from previous header", len(inherit_diff))
    for x in inherit_diff[:25]:
        print(f"  rev={x['review_row']}")
        print(f"    true_co={x['true_company'][:90]}")
        print(f"    prev_co={x['prev_header_company'][:90]}")
        print(f"    path={x['path'][:120]}")

    # For those, check dest in copy map for that source path
    by_src = defaultdict(list)
    for r in review_true:
        by_src[(r.get("source_path") or "").strip().lower()].append(r)
    wrong_dest = []
    for x in inherit_diff:
        hits = by_src.get(x["path"].strip().lower(), [])
        for r in hits:
            dest = r.get("dest_company") or r.get("company") or ""
            if company_key(dest) != company_key(x["true_company"]) and tokens_norm(dest) != tokens_norm(x["true_company"]):
                wrong_dest.append((x, dest, r.get("dest_relative")))
    print("\ncopy-map dest company != TRUE row company (for added different-company TRUE)", len(wrong_dest))
    for x, dest, rel in wrong_dest[:20]:
        print(f"  dest={dest[:80]}")
        print(f"    should={x['true_company'][:80]}")
        print(f"    rel={rel}")


if __name__ == "__main__":
    main()
