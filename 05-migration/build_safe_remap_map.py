"""Build STRUCTURED_COPY_MAP_SAFE.csv — no guessed companies, no dropped rows.

Follow staff aliases until they stop. Nil never becomes a company.
Does not copy files. Does not touch Nextcloud.
"""
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATED = ROOT / "UPDATED COMPANY_FOLDERS_IN_FINAL_csv.csv"
USED = ROOT / "STRUCTURED_COPY_MAP_FINAL_used.csv"
OUT = Path(__file__).resolve().parent / "STRUCTURED_COPY_MAP_SAFE.csv"
REPORT = Path(__file__).resolve().parent / "SAFE_REMAP_REPORT.txt"
UNSORTED = "_UNSORTED"


def sanitize(name: object) -> str:
    s = str(name or "").strip()
    s = re.sub(r'[<>:"/\\|?*\r\n\t]', " ", s)
    s = re.sub(r"\s+", " ", s).strip().rstrip(". ")
    if len(s) > 180:
        s = s[:180].rstrip(". ")
    return s or "(unknown)"


def key(name: object) -> str:
    s = str(name or "").upper()
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def folder_of(path: str) -> str:
    p = str(path or "").rstrip("\\/")
    if "\\" in p:
        return p.split("\\")[-1]
    return p.split("/")[-1]


def load_aliases():
    exact = {}
    nils = set()
    by_key = {}
    with UPDATED.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            src = (r.get("company_folder_in_Final") or "").strip()
            dst = (r.get("company it shold be") or "").strip()
            if not src or not dst:
                continue
            if dst.lower() == "nil":
                nils.add(src)
                nils.add(key(src))
                continue
            dest = sanitize(dst)
            exact[src] = dest
            k = key(src)
            if k:
                by_key[k] = dest
    return exact, nils, by_key


def follow_alias(start, exact, by_key):
    cur = start
    action = "keep"
    hops = 0
    seen = {start}
    while hops < 8:
        nxt = None
        tag = "remap_alias"
        if cur in exact:
            nxt = exact[cur]
        elif key(cur) in by_key:
            nxt = by_key[key(cur)]
            tag = "remap_alias_key"
        else:
            break
        if not nxt or nxt == cur or nxt in seen:
            break
        cur = nxt
        seen.add(nxt)
        hops += 1
        action = "remap_alias_chain" if hops >= 2 else tag
    return cur, action, hops


def rewrite(row, company):
    out = dict(row)
    year = (row.get("dest_year") or "").strip() or "unknown"
    folder = (row.get("dest_folder") or "").strip() or folder_of(row.get("source_path") or "")
    out["dest_company"] = company
    out["dest_year"] = year
    out["dest_folder"] = folder
    out["dest_relative"] = f"{company}\\{year}\\{folder}"
    return out


def main():
    exact, nils, by_key = load_aliases()
    with USED.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys()) if rows else []
    for extra in ("remap_action", "old_dest_company"):
        if extra not in fieldnames:
            fieldnames.append(extra)
    out_rows = []
    stats = Counter()
    nil_rows = []
    chain_rows = []
    collisions = defaultdict(list)
    src_norm = Counter()
    for r in rows:
        dest = (r.get("dest_company") or "").strip()
        src_path = (r.get("source_path") or "").strip()
        if dest in nils or key(dest) in nils:
            new_co = f"{UNSORTED}\\{sanitize(dest)}"
            action = "nil_unsorted"
            nil_rows.append(f"{dest} | {src_path}")
        else:
            new_co, action, hops = follow_alias(dest, exact, by_key)
            if hops >= 2:
                chain_rows.append(f"{dest} => {new_co} | {src_path}")
        out = rewrite(r, new_co)
        out["remap_action"] = action
        out["old_dest_company"] = dest
        out_rows.append(out)
        stats[action] += 1
        collisions[out["dest_relative"].lower()].append(src_path)
        src_norm[src_path.replace("/", "\\").lower()] += 1
    real_coll = {k: v for k, v in collisions.items() if len(v) > 1}
    nested = []
    paths = sorted({(r.get("source_path") or "").strip().replace("/", "\\") for r in out_rows if (r.get("source_path") or "").strip()})
    for p in paths:
        pl = p.lower().rstrip("\\") + "\\"
        for q in paths:
            if p == q:
                continue
            ql = q.lower().rstrip("\\") + "\\"
            if pl.startswith(ql) and pl != ql:
                nested.append((p, q))
                break
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)
    companies = sorted({r["dest_company"] for r in out_rows})
    lines = [
        f"input_rows {len(rows)}",
        f"output_rows {len(out_rows)}",
        f"companies_after {len(companies)}",
        f"action keep {stats['keep']}",
        f"action remap_alias {stats['remap_alias']}",
        f"action remap_alias_key {stats['remap_alias_key']}",
        f"action remap_alias_chain {stats['remap_alias_chain']}",
        f"action nil_unsorted {stats['nil_unsorted']}",
        "",
        "nil_unsorted rows:",
        *nil_rows,
        "",
        f"chain remaps (2+ hops) {len(chain_rows)}",
        *chain_rows,
        "",
        f"duplicate dest_relative {len(real_coll)}",
        f"nested parent/child {len(nested)}",
        f"wrote {OUT}",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:20]))
    print("report", REPORT)


if __name__ == "__main__":
    main()
