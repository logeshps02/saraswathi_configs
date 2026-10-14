"""Would the corrected review create extra dest folders not in the used copy map?"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
USED = ROOT / "STRUCTURED_COPY_MAP_FINAL_used.csv"
REVIEW_X = Path(__file__).resolve().parent / "REVIEW_RESOLVED_CORRECT.xlsx"

ILLEGAL = re.compile(r'[<>:"/\\|?*]')
YEAR_RE = re.compile(r"(20\d{2})-(20\d{2}|\d{2})")


def sanitize(name: str) -> str:
    s = ILLEGAL.sub(" ", str(name or "")).strip()
    s = re.sub(r"\s+", " ", s)
    return s[:180] or "UNKNOWN"


def folder_name(src: str) -> str:
    return sanitize(src.rstrip("\\").split("\\")[-1])


def canonical_year(text) -> str | None:
    if text is None or str(text).strip() == "" or str(text) == "nan":
        return None
    m = YEAR_RE.search(str(text).strip())
    if not m:
        return None
    start, end = m.group(1), m.group(2)
    if len(end) == 4:
        end = end[-2:]
    return f"{start}-{end}"


def main() -> None:
    with USED.open("r", encoding="utf-8-sig", newline="") as f:
        used = list(csv.DictReader(f))
    used_dest = {(r.get("dest_relative") or "").strip().lower() for r in used}
    used_src = {(r.get("source_path") or "").strip().lower() for r in used}
    used_co_year_src = {
        (
            (r.get("dest_company") or "").strip().lower(),
            (r.get("dest_year") or "").strip().lower(),
            (r.get("source_path") or "").strip().lower(),
        )
        for r in used
    }

    style = pd.read_excel(REVIEW_X, "REVIEW_STYLE_RESOLVED")
    print("used rows", len(used), "unique dest", len(used_dest), "unique src", len(used_src))
    print("review style", len(style))
    print(style["status"].value_counts().to_string())

    extra_dest = []
    already = 0
    no_path = 0
    listing_extra = []
    listing_already = 0
    still = []

    for _, r in style.iterrows():
        status = str(r.get("status") or "")
        company = str(r.get("company") or "").strip()
        year = canonical_year(r.get("year")) or canonical_year(r.get("combine")) or "UNKNOWN-YEAR"
        dest_co = sanitize(company)

        if status.startswith("RESOLVED"):
            paths = [p.strip() for p in str(r.get("resolved_path") or "").split(" ; ") if p.strip()]
            if not paths:
                no_path += 1
                continue
            for p in paths:
                rel = f"{dest_co}\\{sanitize(year)}\\{folder_name(p)}"
                key = (
                    dest_co.lower(),
                    sanitize(year).lower(),
                    p.strip().lower(),
                )
                if key in used_co_year_src or rel.lower() in used_dest:
                    already += 1
                else:
                    extra_dest.append(
                        {
                            "company": company,
                            "year": year,
                            "sheet": r.get("source_sheet"),
                            "excel_row": r.get("excel_row"),
                            "status": status,
                            "dest_would_be": rel,
                            "source_path": p,
                            "src_already_in_used": p.strip().lower() in used_src,
                        }
                    )
        elif status == "NO_TRUE_BUT_NAME_IN_FILE_LIST":
            paths = [p.strip() for p in str(r.get("listing_paths") or "").split(" ; ") if p.strip()]
            for p in paths:
                rel = f"{dest_co}\\{sanitize(year)}\\{folder_name(p)}"
                if rel.lower() in used_dest or p.strip().lower() in used_src:
                    listing_already += 1
                else:
                    listing_extra.append(
                        {
                            "company": company,
                            "year": year,
                            "sheet": r.get("source_sheet"),
                            "excel_row": r.get("excel_row"),
                            "dest_would_be": rel,
                            "source_path": p,
                        }
                    )
        elif status == "STILL_NO_TRUE":
            still.append(
                {
                    "company": company,
                    "year": year,
                    "sheet": r.get("source_sheet"),
                    "excel_row": r.get("excel_row"),
                    "combine": r.get("combine"),
                }
            )

    print("\nRESOLVED TRUE dest already covered by used map (company+year+src or dest)", already)
    print("RESOLVED TRUE would create NEW dest not in used map", len(extra_dest))
    print("RESOLVED TRUE with empty path", no_path)

    by_co = defaultdict(int)
    src_in = 0
    src_out = 0
    for x in extra_dest:
        by_co[x["company"]] += 1
        if x["src_already_in_used"]:
            src_in += 1
        else:
            src_out += 1
    print("  of those extra dests, source already copied somewhere in used map", src_in)
    print("  of those extra dests, source not in used map at all", src_out)
    print("  companies affected", len(by_co))
    print("\n--- extra dest companies (top) ---")
    for co, n in sorted(by_co.items(), key=lambda x: -x[1])[:30]:
        print(f"  {n:3d}  {co}")
    print("\n--- extra dest samples (30) ---")
    for x in extra_dest[:30]:
        print(f"  {x['sheet']}|{x['excel_row']}|{x['year']}|{x['company'][:60]}")
        print(f"    dest={x['dest_would_be'][:130]}")
        print(f"    src_in_used={x['src_already_in_used']}  {x['source_path'][:120]}")

    print("\nlisting hits already represented", listing_already)
    print("listing hits that would be new dests", len(listing_extra))
    listing_co = sorted({x["company"] for x in listing_extra})
    print("listing extra companies", len(listing_co))
    for co in listing_co:
        print("  ", co)

    print("\nSTILL_NO_TRUE", len(still))
    for x in still:
        print(f"  {x['sheet']}|{x['excel_row']}|{x['year']}|{x['company']}|{x['combine']}")

    out = Path(__file__).resolve().parent / "USED_VS_CORRECT_EXTRA.csv"
    pd.DataFrame(extra_dest).to_csv(out, index=False, encoding="utf-8-sig")
    print("\nwrote", out, "rows", len(extra_dest))


if __name__ == "__main__":
    main()
