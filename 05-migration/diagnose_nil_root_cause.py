"""Root-cause: why 11 nil names became dest companies, and alias/remap issue.

Does not copy files. Does not touch Nextcloud.
"""
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
UPDATED = ROOT / "UPDATED COMPANY_FOLDERS_IN_FINAL_csv.csv"
USED = ROOT / "STRUCTURED_COPY_MAP_FINAL_used.csv"
FINAL12 = ROOT / "BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx"
OUT = Path(__file__).resolve().parent / "NIL_AND_ALIAS_ROOT_CAUSE.csv"
TXT = Path(__file__).resolve().parent / "NIL_AND_ALIAS_ROOT_CAUSE.txt"

NIL_NAMES = [
    "ARUNKUMAR CASES",
    "CERTIFIED FORMS",
    "CERTIFIED FORMS UPLOADED",
    "CFSS - NEOMAX",
    "CFSS FORMS - OTHER COMPANIES",
    "CHINNIAIH CASES - KYC",
    "CLSS 2014 FOR 8 COMPANIES",
    "LIST PREPARED",
    "MAHARAJ SIR LIST",
    "MAHARAJA SIR CLIENTS DIR-3 KYC AND WEB KY",
    "SURRENDER OF DIN",
]


def k(s: object) -> str:
    t = str(s or "").upper()
    t = re.sub(r"[^A-Z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def load_updated() -> dict[str, str]:
    out = {}
    with UPDATED.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            src = (r.get("company_folder_in_Final") or "").strip()
            dst = (r.get("company it shold be") or "").strip()
            if src:
                out[src] = dst
    return out


def scan_final12(names: list[str]) -> list[dict]:
    hits = []
    if not FINAL12.exists():
        return hits
    xl = pd.ExcelFile(FINAL12)
    want = {k(n) for n in names}
    for sheet in xl.sheet_names:
        df = pd.read_excel(FINAL12, sheet_name=sheet, dtype=object)
        cols = list(df.columns)
        for i, r in df.iterrows():
            excel_row = int(i) + 2
            for c in cols:
                val = r.get(c)
                if val is None or (isinstance(val, float) and pd.isna(val)):
                    continue
                text = str(val).strip()
                if k(text) in want or any(k(n) and k(n) in k(text) and len(k(n)) > 8 for n in names):
                    if k(text) not in want and not any(k(n) == k(text) for n in names):
                        # only exact-ish company-name cells
                        if str(c).upper() not in {"COMPANY NAME", "COMPANY"} and "NAME" not in str(c).upper():
                            continue
                    rec = {
                        "where": "final12",
                        "sheet": sheet,
                        "excel_row": excel_row,
                        "column": str(c),
                        "value": text[:180],
                    }
                    for extra in ("STATUS", "COMBINE", "YEAR", "MATCHED PATH", "COMPANY NAME"):
                        if extra in df.columns:
                            v = r.get(extra)
                            rec[extra] = "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)[:200]
                    hits.append(rec)
    return hits


def main() -> None:
    updated = load_updated()
    nils = [n for n, d in updated.items() if d.lower() == "nil"]
    remaps = [(n, d) for n, d in updated.items() if d and d.lower() != "nil"]
    keeps = [n for n, d in updated.items() if not d]

    with USED.open(encoding="utf-8-sig", newline="") as f:
        used = list(csv.DictReader(f))

    lines = []
    lines.append("ISSUE 1 — nil folders treated as companies")
    lines.append(f"updated_rows {len(updated)} keep {len(keeps)} remap {len(remaps)} nil {len(nils)}")
    lines.append("")

    csv_rows = []
    for name in nils:
        rows = [r for r in used if (r.get("dest_company") or "").strip() == name]
        origins = Counter((r.get("origin") or "") for r in rows)
        sheets = Counter((r.get("source_sheet") or "") for r in rows)
        kinds = Counter((r.get("review_kind") or "") for r in rows)
        lines.append(f"NIL dest_company={name!r} copy_map_rows={len(rows)}")
        lines.append(f"  origins {dict(origins)} sheets {dict(sheets)} review_kind {dict(kinds)}")
        for r in rows:
            lines.append(
                f"  row origin={r.get('origin')} sheet={r.get('source_sheet')} excel={r.get('excel_row')} "
                f"review_row={r.get('review_row')} company_col={r.get('company')!r} "
                f"status={r.get('status')!r} path={r.get('source_path')}"
            )
            csv_rows.append(
                {
                    "issue": "nil",
                    "dest_company": name,
                    "origin": r.get("origin"),
                    "source_sheet": r.get("source_sheet"),
                    "excel_row": r.get("excel_row"),
                    "review_row": r.get("review_row"),
                    "company_col": r.get("company"),
                    "status": r.get("status"),
                    "review_kind": r.get("review_kind"),
                    "source_path": r.get("source_path"),
                }
            )
        lines.append("")

    lines.append("ISSUE 1 — names in (12) workbook (COMPANY NAME / name-like cells)")
    hits = scan_final12(nils)
    by_name = defaultdict(list)
    for h in hits:
        by_name[k(h.get("value"))].append(h)
    for name in nils:
        hh = [h for h in hits if k(h.get("value")) == k(name)]
        lines.append(f"  {name!r} exact_name_cells={len(hh)}")
        for h in hh[:8]:
            lines.append(
                f"    {h.get('sheet')} row {h.get('excel_row')} col {h.get('column')} "
                f"STATUS={h.get('STATUS','')} PATH={(h.get('MATCHED PATH') or '')[:80]}"
            )
        if not hh:
            lines.append("    NOT a COMPANY NAME on (12) — copy map invented dest from REVIEW_TRUE / UF label")
    lines.append("")

    lines.append("ISSUE 2 — alias folders became their own dest_company")
    lines.append(
        "Root: copy map dest_company = sanitize(company column of that row). "
        "DIR-3 / person / duplicate-spelling folders were written as COMPANY NAME "
        "on UPLOADED FORMS or REVIEW TRUE, so they became top-level companies. "
        "Updated sheet now maps them to the real company."
    )
    # examples: dest_company equals alias source, remap target different
    alias_as_dest = 0
    samples = []
    remap_map = {a: b for a, b in remaps}
    dests = Counter((r.get("dest_company") or "").strip() for r in used)
    for alias, target in remaps:
        n = dests.get(alias, 0)
        if n:
            alias_as_dest += 1
            if len(samples) < 15:
                samples.append(f"  {alias!r} ({n} rows) should be {target!r}")
    lines.append(f"alias_names_that_exist_as_dest_company {alias_as_dest} of {len(remaps)}")
    lines.extend(samples)

    # how many dest companies look like DIR-3 / KYC / DIN
    dirty = [
        d
        for d in dests
        if d
        and re.search(r"\b(DIR-?3|DIR-?6|DIN\s?\d|KYC|FORM KYC|WEB KYC)\b", d, re.I)
    ]
    lines.append(f"dest_companies_looking_like_person_or_form {len(dirty)}")
    for d in dirty[:20]:
        lines.append(f"  {d} rows={dests[d]}")

    TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "issue",
                "dest_company",
                "origin",
                "source_sheet",
                "excel_row",
                "review_row",
                "company_col",
                "status",
                "review_kind",
                "source_path",
            ],
        )
        w.writeheader()
        w.writerows(csv_rows)
    print(TXT.read_text(encoding="utf-8")[:8000])
    print("wrote", TXT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
