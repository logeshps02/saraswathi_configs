"""Apply UPDATED COMPANY_FOLDERS aliases onto STRUCTURED_COPY_MAP_FINAL_used.csv.

keep   = blank 'company it shold be' -> dest_company unchanged
remap  = named target -> dest_company becomes that name
nil    = not a company folder -> dest_company taken from (12) COMPANY NAME
         for that source path / folder; leftover _UNMAPPED_NIL if unknown

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
OUT = Path(__file__).resolve().parent / "STRUCTURED_COPY_MAP_REMAPPED.csv"
REPORT = Path(__file__).resolve().parent / "REMAP_APPLY_REPORT.txt"

YEAR_RE = re.compile(r"(20\d{2})-(20\d{2}|\d{2})")


def sanitize(name: object) -> str:
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return "(unknown)"
    s = str(name).strip()
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


def split_paths(val: object) -> list[str]:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return []
    text = str(val).strip()
    if not text:
        return []
    parts = [p.strip() for p in text.split(" ; ") if p.strip()]
    if len(parts) == 1 and ";" in text:
        parts = [p.strip() for p in text.split(";") if p.strip()]
    return parts


def load_aliases() -> tuple[dict[str, str], set[str], dict[str, str]]:
    """Return exact_map, nil_keys, key_map (upper key -> dest)."""
    exact: dict[str, str] = {}
    nils: set[str] = set()
    by_key: dict[str, str] = {}
    with UPDATED.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            src = (r.get("company_folder_in_Final") or "").strip()
            dst = (r.get("company it shold be") or "").strip()
            if not src:
                continue
            if not dst:
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


def index_final12() -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """source_path -> companies, folder_name -> companies from COMPANY WISE."""
    by_path: dict[str, list[str]] = defaultdict(list)
    by_folder: dict[str, list[str]] = defaultdict(list)
    if not FINAL12.exists():
        return by_path, by_folder
    xl = pd.ExcelFile(FINAL12)
    sheets = []
    for name in ("COMPANY WISE", "UPLOADED FORMS - COMPANY NAME"):
        if name in xl.sheet_names:
            sheets.append(name)
    for sheet in sheets:
        df = pd.read_excel(FINAL12, sheet_name=sheet, dtype=object)
        if "COMPANY NAME" not in df.columns:
            continue
        if sheet == "COMPANY WISE":
            df["COMPANY_FF"] = df["COMPANY NAME"].ffill()
        else:
            df["COMPANY_FF"] = df["COMPANY NAME"]
        path_col = "MATCHED PATH" if "MATCHED PATH" in df.columns else None
        if path_col is None:
            for c in df.columns:
                if "PATH" in str(c).upper():
                    path_col = c
                    break
        if path_col is None:
            continue
        for _, r in df.iterrows():
            company = sanitize(r.get("COMPANY_FF"))
            if not company or company == "(unknown)":
                continue
            for p in split_paths(r.get(path_col)):
                by_path[p.replace("/", "\\").lower()].append(company)
                by_folder[folder_of(p).upper()].append(company)
    return by_path, by_folder


def pick_company(cands: list[str]) -> str | None:
    if not cands:
        return None
    counts = Counter(cands)
    if len(counts) == 1:
        return cands[0]
    # majority
    name, n = counts.most_common(1)[0]
    if n >= 2 and n > sum(counts.values()) / 2:
        return name
    return None


def rewrite_dest(row: dict, company: str) -> dict:
    out = dict(row)
    year = (row.get("dest_year") or "").strip() or "unknown"
    folder = (row.get("dest_folder") or "").strip() or folder_of(row.get("source_path") or "")
    out["dest_company"] = company
    out["dest_year"] = year
    out["dest_folder"] = folder
    out["dest_relative"] = f"{company}\\{year}\\{folder}"
    return out


def main() -> None:
    exact, nils, by_key = load_aliases()
    by_path, by_folder = index_final12()
    with USED.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys()) if rows else []
    if "remap_action" not in fieldnames:
        fieldnames.append("remap_action")

    out_rows: list[dict] = []
    stats = Counter()
    nil_unmapped: list[str] = []
    for r in rows:
        dest = (r.get("dest_company") or "").strip()
        src_path = (r.get("source_path") or "").strip()
        action = "keep"
        new_co = dest
        if dest in exact:
            new_co = exact[dest]
            action = "remap_alias"
        elif key(dest) in by_key:
            new_co = by_key[key(dest)]
            action = "remap_alias_key"
        elif dest in nils or key(dest) in nils:
            cands = []
            cands.extend(by_path.get(src_path.replace("/", "\\").lower(), []))
            cands.extend(by_folder.get(folder_of(src_path).upper(), []))
            picked = pick_company(cands)
            if picked:
                new_co = picked
                action = "nil_from_12"
            else:
                new_co = f"_UNMAPPED_NIL\\{sanitize(dest)}"
                action = "nil_unmapped"
                nil_unmapped.append(f"{dest} | {src_path}")
        stats[action] += 1
        nr = rewrite_dest(r, new_co)
        nr["remap_action"] = action
        out_rows.append(nr)

    # dest_relative collisions: append (2) on dest_folder
    seen: dict[str, int] = {}
    for r in out_rows:
        rel = r["dest_relative"]
        n = seen.get(rel, 0)
        seen[rel] = n + 1
        if n:
            folder = r["dest_folder"]
            stem = folder
            extra = f" ({n + 1})"
            if not folder.endswith(extra):
                r["dest_folder"] = f"{stem} ({n + 1})"
                r["dest_relative"] = f"{r['dest_company']}\\{r['dest_year']}\\{r['dest_folder']}"
                r["remap_action"] += "; dest_name_collision_renamed"

    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)

    companies = sorted({r["dest_company"] for r in out_rows if not r["dest_company"].startswith("_UNMAPPED")})
    report = []
    report.append(f"input_rows {len(rows)}")
    report.append(f"output_rows {len(out_rows)}")
    report.append(f"companies_after {len(companies)}")
    for k, v in stats.most_common():
        report.append(f"action {k} {v}")
    report.append(f"nil_unmapped {len(nil_unmapped)}")
    report.extend(nil_unmapped[:80])
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report[:30]))
    print("wrote", OUT)
    print("wrote", REPORT)


if __name__ == "__main__":
    main()
