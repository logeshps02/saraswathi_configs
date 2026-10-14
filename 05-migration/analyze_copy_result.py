"""Summarize finished copy: ok / missing / failed vs used map."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "_COPY_LOG.csv"
MISS = ROOT / "_COPY_MISSING.csv"
USED = ROOT / "STRUCTURED_COPY_MAP_FINAL_used.csv"


def main() -> None:
    with LOG.open("r", encoding="utf-8-sig", newline="") as f:
        log = list(csv.DictReader(f))
    with MISS.open("r", encoding="utf-8-sig", newline="") as f:
        miss = list(csv.DictReader(f))
    with USED.open("r", encoding="utf-8-sig", newline="") as f:
        used = list(csv.DictReader(f))

    print("log_rows", len(log), "cols", log[0].keys() if log else None)
    print("missing_rows", len(miss))
    print("used_rows", len(used))

    ok_vals = defaultdict(int)
    notes = defaultdict(int)
    failed = []
    not_ok = []
    seconds = 0.0
    for r in log:
        ok = str(r.get("ok") or "").strip()
        ok_vals[ok] += 1
        note = str(r.get("rc_or_note") or "").strip()
        notes[note] += 1
        try:
            seconds += float(r.get("seconds") or 0)
        except Exception:
            pass
        if ok not in {"1", "True", "true"}:
            not_ok.append(r)
            if "source_not_found" not in note.lower():
                failed.append(r)

    print("\nok value counts", dict(ok_vals))
    print("note counts:")
    for k, n in sorted(notes.items(), key=lambda x: -x[1]):
        print(f"  {n:5d}  {k}")
    print("seconds_sum", round(seconds, 1), "hours", round(seconds / 3600, 2))

    print("\n=== FAILED (ok!=1 and not source_not_found)", len(failed), "===")
    for r in failed:
        print(f"  ok={r.get('ok')} note={r.get('rc_or_note')} sec={r.get('seconds')}")
        print(f"    dest={r.get('dest_relative')}")
        print(f"    src={r.get('source_path')}")

    print("\n=== MISSING FILE", len(miss), "===")
    used_by_src = defaultdict(list)
    used_by_dest = defaultdict(list)
    for r in used:
        used_by_src[(r.get("source_path") or "").strip().lower()].append(r)
        used_by_dest[(r.get("dest_relative") or "").strip().lower()].append(r)

    for r in miss:
        src = (r.get("source_path") or "").strip()
        dest = (r.get("dest_relative") or "").strip()
        reason = r.get("reason")
        um = used_by_src.get(src.lower(), []) or used_by_dest.get(dest.lower(), [])
        origin = um[0].get("origin") if um else "?"
        company = um[0].get("company") if um else "?"
        sheet = um[0].get("source_sheet") if um else "?"
        row = um[0].get("excel_row") if um else "?"
        print(f"  {reason}")
        print(f"    src={src}")
        print(f"    dest={dest}")
        print(f"    map origin={origin} sheet={sheet} excel_row={row} company={company}")

    # classify missing
    print("\n=== MISSING CLASSIFICATION ===")
    classes = defaultdict(list)
    for r in miss:
        src = (r.get("source_path") or "").strip()
        if src.upper().startswith("H:\\"):
            classes["H_drive_not_present"].append(src)
        elif "\\" not in src and "/" not in src:
            classes["bare_name_not_full_path"].append(src)
        elif src.upper().startswith("F:\\") or src.upper().startswith("E:\\"):
            classes["E_or_F_path_not_found"].append(src)
        else:
            classes["other"].append(src)
    for k, v in classes.items():
        print(f"{k}: {len(v)}")
        for s in v:
            print("   ", s[:160])

    # check if failed dests still exist as other successful copies of same source
    print("\n=== same source copied OK elsewhere? ===")
    ok_src = {(r.get("source_path") or "").strip().lower() for r in log if str(r.get("ok")).strip() in {"1", "True", "true"}}
    for r in miss + failed:
        src = (r.get("source_path") or "").strip().lower()
        print(f"  missing/fail src also ok elsewhere? {src[:90]!r} -> {src in ok_src}")


if __name__ == "__main__":
    main()
