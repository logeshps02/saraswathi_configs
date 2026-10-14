"""Compare each nil_unsorted parent vs already-mapped company children.

Does not copy. Does not delete. Writes leftover report for drop/keep decisions.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"c:\Users\U.lalitha navya sri\Downloads\Logesh files")
SAFE = ROOT / "05-migration" / "STRUCTURED_COPY_MAP_SAFE.csv"
OUT = ROOT / "05-migration" / "UNSORTED_LEFTOVER_COMPARE.txt"
CSV_OUT = ROOT / "05-migration" / "UNSORTED_LEFTOVER_COMPARE.csv"


def norm(p: str) -> str:
    return (p or "").strip().strip('"').replace("/", "\\").rstrip("\\").upper()


def load_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def child_dirs(path: Path) -> list[Path]:
    try:
        return sorted([p for p in path.iterdir() if p.is_dir()], key=lambda x: x.name.lower())
    except OSError as e:
        return [Path(f"__ERROR__:{e}")]


def main() -> None:
    rows = load_rows(SAFE)
    unsorted = [r for r in rows if (r.get("remap_action") or "").strip() == "nil_unsorted"]
    all_src = []
    by_src = defaultdict(list)
    for r in rows:
        sp = (r.get("source_path") or "").strip()
        if not sp:
            continue
        n = norm(sp)
        all_src.append(n)
        by_src[n].append(r)

    lines: list[str] = []
    csv_rows: list[dict] = []
    lines.append(f"safe_rows {len(rows)}")
    lines.append(f"nil_unsorted {len(unsorted)}")
    lines.append(f"E_drive {Path('E:/').exists()}")
    lines.append(f"F_drive {Path('F:/').exists()}")
    dest_root = Path(r"F:\f")
    lines.append(f"dest_F_f {dest_root.exists()}")
    lines.append("")

    for i, u in enumerate(unsorted, 1):
        parent = (u.get("source_path") or "").strip()
        dest_co = (u.get("dest_company") or "").strip()
        dest_rel = (u.get("dest_relative") or "").strip()
        pn = norm(parent)
        ppath = Path(parent)
        source_exists = ppath.exists()
        mapped_children = []
        for n, rs in by_src.items():
            if n == pn:
                continue
            if n.startswith(pn + "\\"):
                mapped_children.extend(rs)

        leftover_names: list[str] = []
        listed: list[str] = []
        list_error = ""
        if source_exists:
            kids = child_dirs(ppath)
            if kids and str(kids[0]).startswith("__ERROR__:"):
                list_error = str(kids[0])
            else:
                mapped_norms = {norm(r.get("source_path") or "") for r in mapped_children}
                mapped_norms.add(pn)
                for k in kids:
                    kn = norm(str(k))
                    listed.append(k.name)
                    under = any(m == kn or m.startswith(kn + "\\") for m in mapped_norms)
                    exact = kn in mapped_norms
                    if not exact and not under:
                        leftover_names.append(k.name)
        else:
            leftover_names = ["__SOURCE_OFFLINE__"]

        dest_path = dest_root / dest_rel if dest_root.exists() else None
        dest_exists = bool(dest_path and dest_path.exists())
        dest_child_count = 0
        if dest_exists:
            try:
                dest_child_count = sum(1 for _ in dest_path.iterdir())
            except OSError:
                dest_child_count = -1

        decision = "KEEP_UNSORTED"
        reason = "unique_or_unknown"
        if leftover_names == ["__SOURCE_OFFLINE__"]:
            if mapped_children:
                decision = "CANDIDATE_DROP_PARENT_MAP_ONLY"
                reason = "children_mapped_source_offline"
            else:
                decision = "KEEP_UNSORTED"
                reason = "no_mapped_children_source_offline"
        elif list_error:
            decision = "KEEP_UNSORTED"
            reason = "listdir_error"
        elif mapped_children and not leftover_names:
            decision = "DROP_PARENT_DUPLICATE"
            reason = "all_immediate_children_already_mapped"
        elif mapped_children and leftover_names:
            decision = "KEEP_UNSORTED_HAS_LEFTOVER"
            reason = "some_children_mapped_some_not"
        elif not mapped_children:
            decision = "KEEP_UNSORTED"
            reason = "no_other_map_rows_under_parent"

        lines.append(f"=== {i}. {dest_co} ===")
        lines.append(f"source {parent}")
        lines.append(f"source_exists {source_exists}")
        lines.append(f"dest_relative {dest_rel}")
        lines.append(f"dest_exists {dest_exists} dest_child_count {dest_child_count}")
        lines.append(f"mapped_child_rows {len(mapped_children)}")
        for r in mapped_children[:40]:
            lines.append(
                f"  CHILD dest={r.get('dest_company')} year={r.get('dest_year')} "
                f"folder={r.get('dest_folder')} src={r.get('source_path')}"
            )
        if len(mapped_children) > 40:
            lines.append(f"  ... {len(mapped_children) - 40} more child rows")
        lines.append(f"listed_immediate_children {len(listed)}")
        if listed:
            lines.append("  listed: " + " | ".join(listed[:80]))
        if list_error:
            lines.append(f"list_error {list_error}")
        lines.append(f"leftover_immediate {leftover_names}")
        lines.append(f"DECISION {decision} reason={reason}")
        lines.append("")

        csv_rows.append(
            {
                "dest_company": dest_co,
                "source_path": parent,
                "source_exists": source_exists,
                "dest_exists": dest_exists,
                "dest_child_count": dest_child_count,
                "mapped_child_rows": len(mapped_children),
                "listed_children": len(listed),
                "leftover": " | ".join(leftover_names),
                "decision": decision,
                "reason": reason,
            }
        )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with CSV_OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()) if csv_rows else [])
        w.writeheader()
        w.writerows(csv_rows)
    print(OUT)
    print(CSV_OUT)
    print("\n".join(lines[:80]))


if __name__ == "__main__":
    main()
