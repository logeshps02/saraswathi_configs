"""Leftover vs mapped-child compare using local all-files lists + copy log.

Does not copy. Does not delete. Sources on the other laptop are not required.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"c:\Users\U.lalitha navya sri\Downloads\Logesh files")
SAFE = ROOT / "05-migration" / "STRUCTURED_COPY_MAP_SAFE.csv"
LISTS = [
    ROOT / "CHAT_EXPORT" / "source_lists" / "all_files_list (2).txt",
    ROOT / "CHAT_EXPORT" / "source_lists" / "all_files_list_2025_26.txt",
]
LOG = ROOT / "_COPY_LOG.csv"
MISS = ROOT / "_COPY_MISSING.csv"
OUT = ROOT / "05-migration" / "UNSORTED_VS_LISTS_AND_COPY_LOG.txt"
CSV_OUT = ROOT / "05-migration" / "UNSORTED_VS_LISTS_AND_COPY_LOG.csv"


def norm(p: str) -> str:
    return (p or "").strip().strip('"').replace("/", "\\").rstrip("\\").upper()


def load_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def first_child(parent_n: str, file_n: str) -> str | None:
    if file_n == parent_n:
        return None
    prefix = parent_n + "\\"
    if not file_n.startswith(prefix):
        return None
    rest = file_n[len(prefix) :]
    return rest.split("\\", 1)[0]


def iter_listing_paths(path: Path):
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("====="):
                continue
            if len(s) >= 3 and s[1] == ":" and s[2] == "\\":
                yield s


def main() -> None:
    rows = load_rows(SAFE)
    unsorted = [r for r in rows if (r.get("remap_action") or "").strip() == "nil_unsorted"]
    by_src: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        sp = (r.get("source_path") or "").strip()
        if sp:
            by_src[norm(sp)].append(r)

    parents = []
    for u in unsorted:
        p = (u.get("source_path") or "").strip()
        parents.append(
            {
                "row": u,
                "parent": p,
                "pn": norm(p),
                "hits": [],
                "roots_seen": set(),
            }
        )

    list_stats = []
    for lp in LISTS:
        n_lines = 0
        n_paths = 0
        roots = set()
        with lp.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                n_lines += 1
                s = line.strip()
                if s.startswith("===== FILE LIST"):
                    roots.add(s)
                if not s or s.startswith("====="):
                    continue
                if not (len(s) >= 3 and s[1] == ":" and s[2] == "\\"):
                    continue
                n_paths += 1
                sn = norm(s)
                for rec in parents:
                    if sn == rec["pn"] or sn.startswith(rec["pn"] + "\\"):
                        rec["hits"].append(s)
        list_stats.append((lp.name, n_lines, n_paths, sorted(roots)))

    log_by_src: dict[str, list[dict]] = defaultdict(list)
    dests_by_src: dict[str, set[str]] = defaultdict(set)
    with LOG.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            n = norm(r.get("source_path") or "")
            log_by_src[n].append(r)
            dests_by_src[n].add((r.get("dest_relative") or "").strip())

    missing_srcs = set()
    if MISS.is_file():
        with MISS.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                missing_srcs.add(norm(r.get("source_path") or ""))

    lines: list[str] = []
    csv_rows: list[dict] = []
    lines.append("=== INPUTS ===")
    lines.append(f"safe_rows {len(rows)} nil_unsorted {len(unsorted)}")
    lines.append(f"copy_log {LOG} exists {LOG.is_file()}")
    lines.append(f"copy_missing {MISS} exists {MISS.is_file()}")
    for name, n_lines, n_paths, roots in list_stats:
        lines.append(f"list {name} lines {n_lines} paths {n_paths}")
        for r in roots:
            lines.append(f"  {r}")
    lines.append("")

    for rec in parents:
        u = rec["row"]
        parent = rec["parent"]
        pn = rec["pn"]
        dest_co = (u.get("dest_company") or "").strip()
        dest_rel = (u.get("dest_relative") or "").strip()
        hits = rec["hits"]
        mapped_children = []
        for n, rs in by_src.items():
            if n == pn:
                continue
            if n.startswith(pn + "\\"):
                mapped_children.extend(rs)
        mapped_norms = {norm(r.get("source_path") or "") for r in mapped_children}

        files_at_parent = 0
        child_files: dict[str, int] = defaultdict(int)
        for h in hits:
            hn = norm(h)
            if hn == pn:
                files_at_parent += 1
                continue
            ch = first_child(pn, hn)
            if ch:
                child_files[ch] += 1

        leftover = []
        covered = []
        for ch, cnt in sorted(child_files.items(), key=lambda x: x[0]):
            kn = pn + "\\" + ch
            exact = kn in mapped_norms
            under = any(m == kn or m.startswith(kn + "\\") for m in mapped_norms)
            # whole parent also copied under a company (same source_path)
            parent_also_company = any(
                (r.get("dest_company") or "").startswith("_UNSORTED") is False
                for r in by_src.get(pn, [])
            )
            if exact or under:
                covered.append(f"{ch} ({cnt} files)")
            else:
                leftover.append(f"{ch} ({cnt} files)")

        parent_log = log_by_src.get(pn, [])
        child_log_ok = 0
        child_log_fail = 0
        child_log_dests = []
        for r in mapped_children:
            n = norm(r.get("source_path") or "")
            hits_log = log_by_src.get(n, [])
            if any(str(x.get("ok") or "") in {"1", "true", "True"} for x in hits_log):
                child_log_ok += 1
            elif hits_log:
                child_log_fail += 1
            child_log_dests.extend(sorted(dests_by_src.get(n, [])))
        parent_also_company_rows = [
            r
            for r in by_src.get(pn, [])
            if not (r.get("dest_company") or "").startswith("_UNSORTED")
        ]

        in_missing = pn in missing_srcs
        listed = bool(hits) or files_at_parent

        if not listed:
            decision = "KEEP_UNSORTED_NOT_IN_LISTS"
            reason = "parent_path_not_in_all_files_lists"
        elif leftover:
            decision = "KEEP_UNSORTED_HAS_LEFTOVER"
            reason = "listing_has_unmapped_immediate_children"
        elif mapped_children or parent_also_company_rows:
            decision = "DROP_PARENT_DUPLICATE"
            reason = "all_listed_children_mapped_or_parent_also_company"
        else:
            decision = "KEEP_UNSORTED"
            reason = "listed_but_no_company_children"

        lines.append(f"=== {dest_co} ===")
        lines.append(f"source {parent}")
        lines.append(f"dest_relative {dest_rel}")
        lines.append(f"listing_hits {len(hits)} files_at_parent_level {files_at_parent}")
        lines.append(f"immediate_children {len(child_files)}")
        for ch, cnt in sorted(child_files.items()):
            lines.append(f"  CHILD_DIR {ch}  files={cnt}")
        lines.append(f"mapped_child_rows {len(mapped_children)}")
        for r in mapped_children:
            lines.append(
                f"  MAP {r.get('dest_company')} | {r.get('dest_folder')} | {r.get('source_path')}"
            )
        if parent_also_company_rows:
            for r in parent_also_company_rows:
                lines.append(
                    f"  SAME_SOURCE_ALSO {r.get('dest_company')} | {r.get('dest_relative')}"
                )
        lines.append(f"covered_children {covered}")
        lines.append(f"leftover_children {leftover}")
        lines.append(
            f"copy_log parent_rows {len(parent_log)} dests {sorted(dests_by_src.get(pn, []))}"
        )
        for r in parent_log:
            lines.append(
                f"  LOG ok={r.get('ok')} dest={r.get('dest_relative')} note={r.get('rc_or_note')}"
            )
        lines.append(
            f"copy_log mapped_children ok={child_log_ok} fail={child_log_fail} in_missing={in_missing}"
        )
        lines.append(f"DECISION {decision} reason={reason}")
        lines.append("")

        csv_rows.append(
            {
                "dest_company": dest_co,
                "source_path": parent,
                "listing_hits": len(hits),
                "immediate_children": len(child_files),
                "mapped_child_rows": len(mapped_children),
                "same_source_also_company": len(parent_also_company_rows),
                "leftover": " | ".join(leftover) if leftover else "",
                "parent_in_missing": in_missing,
                "parent_copy_ok": any(
                    str(x.get("ok") or "") in {"1", "true", "True"} for x in parent_log
                ),
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
    print("\n".join(lines))


if __name__ == "__main__":
    main()
