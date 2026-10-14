"""Print every copy row that did not succeed."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "_COPY_LOG.csv"
MISS = ROOT / "_COPY_MISSING.csv"
USED = ROOT / "STRUCTURED_COPY_MAP_FINAL_used.csv"
OUT = Path(__file__).resolve().parent / "COPY_FAILED_AND_MISSING.csv"


def main() -> None:
    with LOG.open("r", encoding="utf-8-sig", newline="") as f:
        log = list(csv.DictReader(f))
    with USED.open("r", encoding="utf-8-sig", newline="") as f:
        used = list(csv.DictReader(f))
    used_by_dest = {
        (r.get("dest_relative") or "").strip().lower(): r for r in used
    }

    bad = []
    for i, r in enumerate(log, start=2):
        ok = str(r.get("ok") or "").strip()
        if ok in {"1", "True", "true"}:
            continue
        dest = (r.get("dest_relative") or "").strip()
        um = used_by_dest.get(dest.lower(), {})
        note = (r.get("rc_or_note") or "").strip()
        if "source_not_found" in note.lower():
            kind = "MISSING_SOURCE"
        elif "too long" in note.lower():
            kind = "FAILED_PATH_TOO_LONG"
        else:
            kind = "FAILED_OTHER"
        bad.append(
            {
                "kind": kind,
                "log_excel_row": i,
                "ok": ok,
                "rc_or_note": note,
                "source_path": r.get("source_path"),
                "dest_relative": dest,
                "origin": um.get("origin"),
                "source_sheet": um.get("source_sheet"),
                "excel_row": um.get("excel_row"),
                "company": um.get("company"),
                "year": um.get("year"),
            }
        )

    print("TOTAL_NOT_OK", len(bad))
    from collections import Counter
    print("by kind", dict(Counter(x["kind"] for x in bad)))
    print()
    for n, x in enumerate(bad, 1):
        print(f"{n}. [{x['kind']}]")
        print(f"   company : {x['company']}")
        print(f"   year    : {x['year']}")
        print(f"   origin  : {x['origin']}  {x['source_sheet']} row {x['excel_row']}")
        print(f"   reason  : {x['rc_or_note']}")
        print(f"   source  : {x['source_path']}")
        print(f"   dest    : {x['dest_relative']}")
        print()

    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(bad[0].keys()))
        w.writeheader()
        w.writerows(bad)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
