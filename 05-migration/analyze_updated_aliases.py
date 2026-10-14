"""Summarize UPDATED COMPANY_FOLDERS_IN_FINAL_csv.csv (keep / remap / nil)."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATED = ROOT / "UPDATED COMPANY_FOLDERS_IN_FINAL_csv.csv"


def main() -> None:
    with UPDATED.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    print("rows", len(rows))
    print("cols", list(rows[0].keys()) if rows else None)
    keep = remap = nil = other = 0
    nil_names: list[str] = []
    remap_pairs: list[tuple[str, str]] = []
    for r in rows:
        src = (r.get("company_folder_in_Final") or "").strip()
        dst = (r.get("company it shold be") or "").strip()
        if not src:
            other += 1
            continue
        if not dst:
            keep += 1
        elif dst.lower() == "nil":
            nil += 1
            nil_names.append(src)
        else:
            remap += 1
            remap_pairs.append((src, dst))
    print("keep", keep, "remap", remap, "nil", nil, "other", other)
    print("--- nil ---")
    for n in nil_names:
        print(n)
    print("--- remaps ---")
    for a, b in remap_pairs:
        print(f"{a} => {b}")


if __name__ == "__main__":
    main()
