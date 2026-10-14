"""Compare the copy map already in use vs current FINAL map and corrected review."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
USED = ROOT / "STRUCTURED_COPY_MAP_FINAL_used.csv"
CUR = Path(__file__).resolve().parent / "STRUCTURED_COPY_MAP_FINAL.csv"
REVIEW_X = Path(__file__).resolve().parent / "REVIEW_RESOLVED_CORRECT.xlsx"


def load_csv(p: Path) -> list[dict]:
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def key_dest_src(r: dict) -> tuple[str, str]:
    return (
        (r.get("dest_relative") or "").strip().lower(),
        (r.get("source_path") or "").strip().lower(),
    )


def key_src(r: dict) -> str:
    return (r.get("source_path") or "").strip().lower()


def main() -> None:
    used = load_csv(USED)
    cur = load_csv(CUR)
    print("USED file", USED, "rows", len(used), "cols", list(used[0].keys()) if used else [])
    print("CUR  file", CUR, "rows", len(cur), "cols", list(cur[0].keys()) if cur else [])

    used_origin = defaultdict(int)
    cur_origin = defaultdict(int)
    for r in used:
        used_origin[r.get("origin") or ""] += 1
    for r in cur:
        cur_origin[r.get("origin") or ""] += 1
    print("USED origins", dict(used_origin))
    print("CUR  origins", dict(cur_origin))
    print("USED companies", len({(r.get("dest_company") or "").strip().lower() for r in used}))
    print("CUR  companies", len({(r.get("dest_company") or "").strip().lower() for r in cur}))

    used_pairs = {key_dest_src(r) for r in used}
    cur_pairs = {key_dest_src(r) for r in cur}
    only_used = used_pairs - cur_pairs
    only_cur = cur_pairs - used_pairs
    both = used_pairs & cur_pairs
    print("\nidentical dest+source pairs", len(both))
    print("in USED not in CUR", len(only_used))
    print("in CUR not in USED", len(only_cur))

    used_src = {key_src(r) for r in used if key_src(r)}
    cur_src = {key_src(r) for r in cur if key_src(r)}
    print("\nsource paths USED", len(used_src), "CUR", len(cur_src))
    print("source only USED", len(used_src - cur_src))
    print("source only CUR", len(cur_src - used_src))

    # dest-only differences for same source
    used_by_src = defaultdict(list)
    cur_by_src = defaultdict(list)
    for r in used:
        used_by_src[key_src(r)].append(r)
    for r in cur:
        cur_by_src[key_src(r)].append(r)

    dest_changed = []
    for src in used_src & cur_src:
        ud = {(x.get("dest_relative") or "").strip().lower() for x in used_by_src[src]}
        cd = {(x.get("dest_relative") or "").strip().lower() for x in cur_by_src[src]}
        if ud != cd:
            dest_changed.append((src, ud, cd, used_by_src[src][0], cur_by_src[src][0]))
    print("same source, different dest_relative", len(dest_changed))
    for src, ud, cd, u, c in dest_changed[:20]:
        print("  USED dest:", u.get("dest_relative"))
        print("  CUR  dest:", c.get("dest_relative"))
        print("  src:", (u.get("source_path") or "")[:140])
        print("  USED company/year:", u.get("dest_company"), u.get("dest_year"), "origin", u.get("origin"))
        print("  CUR  company/year:", c.get("dest_company"), c.get("dest_year"), "origin", c.get("origin"))
        print()

    # origin split of pair diffs
    used_lookup = {key_dest_src(r): r for r in used}
    cur_lookup = {key_dest_src(r): r for r in cur}
    only_used_by_origin = defaultdict(int)
    only_cur_by_origin = defaultdict(int)
    for k in only_used:
        only_used_by_origin[used_lookup[k].get("origin") or ""] += 1
    for k in only_cur:
        only_cur_by_origin[cur_lookup[k].get("origin") or ""] += 1
    print("only USED by origin", dict(only_used_by_origin))
    print("only CUR by origin", dict(only_cur_by_origin))

    print("\n--- sample only in USED (first 15) ---")
    for i, k in enumerate(sorted(only_used)[:15], 1):
        r = used_lookup[k]
        print(f"{i}. origin={r.get('origin')} dest={r.get('dest_relative')[:110]}")
        print(f"   src={r.get('source_path')[:120]}")
    print("\n--- sample only in CUR (first 15) ---")
    for i, k in enumerate(sorted(only_cur)[:15], 1):
        r = cur_lookup[k]
        print(f"{i}. origin={r.get('origin')} dest={r.get('dest_relative')[:110]}")
        print(f"   src={r.get('source_path')[:120]}")

    # REVIEW_TRUE comparison
    used_rt = [r for r in used if (r.get("origin") or "") == "REVIEW_TRUE"]
    cur_rt = [r for r in cur if (r.get("origin") or "") == "REVIEW_TRUE"]
    print("\nREVIEW_TRUE USED", len(used_rt), "CUR", len(cur_rt))
    used_rt_src = {key_src(r) for r in used_rt}
    cur_rt_src = {key_src(r) for r in cur_rt}
    print("REVIEW_TRUE src only USED", len(used_rt_src - cur_rt_src))
    print("REVIEW_TRUE src only CUR", len(cur_rt_src - used_rt_src))

    # Corrected review workbook
    if REVIEW_X.is_file():
        style = pd.read_excel(REVIEW_X, "REVIEW_STYLE_RESOLVED")
        still = pd.read_excel(REVIEW_X, "STILL_OPEN_FULL_ROWS")
        print("\nREVIEW_RESOLVED_CORRECT rows", len(style))
        print(style["status"].value_counts().to_string())
        resolved = style[style["status"].astype(str).str.startswith("RESOLVED")]
        # paths from resolved vs used map
        resolved_paths = set()
        for p in resolved["resolved_path"].fillna(""):
            for part in str(p).split(" ; "):
                part = part.strip().lower()
                if part:
                    resolved_paths.add(part)
        print("unique TRUE resolved paths", len(resolved_paths))
        print("TRUE resolved paths already in USED map", len(resolved_paths & used_src))
        print("TRUE resolved paths NOT in USED map", len(resolved_paths - used_src))
        missing_true = sorted(resolved_paths - used_src)
        print("\n--- TRUE paths not in USED (first 30) ---")
        for p in missing_true[:30]:
            print(" ", p[:160])

        # For missing TRUE paths, which companies
        miss_companies = defaultdict(int)
        for _, r in resolved.iterrows():
            paths = [x.strip().lower() for x in str(r.get("resolved_path") or "").split(" ; ") if x.strip()]
            if any(p not in used_src for p in paths):
                miss_companies[str(r.get("company") or "")] += 1
        print("\nNF rows whose TRUE path is not fully in USED:", sum(miss_companies.values()), "companies", len(miss_companies))
        for co, n in sorted(miss_companies.items(), key=lambda x: -x[1])[:25]:
            print(f"  {n:3d}  {co}")

        listing = style[style["status"] == "NO_TRUE_BUT_NAME_IN_FILE_LIST"]
        listing_paths = set()
        for p in listing["listing_paths"].fillna(""):
            for part in str(p).split(" ; "):
                part = part.strip().lower()
                if part:
                    listing_paths.add(part)
        print("\nlisting-only unique paths", len(listing_paths))
        print("listing-only already in USED", len(listing_paths & used_src))
        print("listing-only not in USED", len(listing_paths - used_src))

        still_no = style[style["status"] == "STILL_NO_TRUE"]
        print("\nSTILL_NO_TRUE rows", len(still_no), "companies", still_no["company"].nunique())

    # Would extra TRUE paths collide with existing dest?
    extra_src = (resolved_paths - used_src) if REVIEW_X.is_file() else set()
    print("\nCONCLUSION COUNTS")
    print("  keep copying USED rows", len(used))
    print("  USED vs CUR dest+src identical", len(both), "/", max(len(used_pairs), len(cur_pairs)))
    print("  extra TRUE paths to add later", len(extra_src) if REVIEW_X.is_file() else "n/a")
    print("  listing-only extra (do not auto-add)", len(listing_paths - used_src) if REVIEW_X.is_file() else "n/a")
    print("  still no path", len(still_no) if REVIEW_X.is_file() else "n/a")


if __name__ == "__main__":
    main()
