"""Compare HP F:\\f company folders vs 2026-27 map dest companies.

Rule: append 2026-27 only under an existing F:\\f company name.
Do not guess. Do not recopy F:\\f.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
FF = HERE / "F_F_COMPANY_FOLDERS.txt"
MAP = HERE / "STRUCTURED_COPY_MAP_2026_27.csv"
OUT_TXT = HERE / "FF_VS_2026_27_REPORT.txt"
OUT_CSV = HERE / "FF_VS_2026_27.csv"

NON_COMPANY = {
    "ALREADY FILED DIN 4FORMS",
    "DIN FORMS",
    "GPS AGENCY",
    "KARAI MURUGAN CRANE",
    "KM BIOMED",
    "NEOMAX GROUP",
    "PKP HOSPITAILITY FORM 11",
    "POMMYS",
    "RIGHT TRUST",
    "ROYALCREST REAL ESTATE DUBAI",
    "SARUMATHI ANNAMALAI PETRO",
    "SASTIKAA ASSOCIATION",
    "THIRU PUBLICATIONS",
}


def norm(s: str) -> str:
    return " ".join(s.upper().replace(".", " ").replace(",", " ").split())


def main() -> None:
    ff_names = [
        ln.strip()
        for ln in FF.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    ff_set = set(ff_names)
    ff_norm = {norm(n): n for n in ff_names}

    rows = list(csv.DictReader(MAP.open(encoding="utf-8", newline="")))
    dests: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        dests[r["dest_company"]].append(r)

    exact = []
    norm_hit = []
    missing = []
    unsorted = []

    for dest, group in sorted(dests.items(), key=lambda x: x[0].upper()):
        hows = sorted({g["match_how"] for g in group})
        rec = {
            "dest_company": dest,
            "n_jobs": str(len(group)),
            "match_how": "+".join(hows),
        }
        if dest == "_UNSORTED" or dest.startswith("_UNSORTED"):
            rec["ff_status"] = "unsorted_keep"
            rec["ff_name"] = ""
            unsorted.append(rec)
            continue
        if dest in ff_set:
            rec["ff_status"] = "exact"
            rec["ff_name"] = dest
            exact.append(rec)
            continue
        n = norm(dest)
        if n in ff_norm:
            rec["ff_status"] = "norm_match"
            rec["ff_name"] = ff_norm[n]
            norm_hit.append(rec)
            continue
        rec["ff_status"] = "not_on_ff"
        rec["ff_name"] = ""
        missing.append(rec)

    all_recs = exact + norm_hit + missing + unsorted
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["dest_company", "ff_status", "ff_name", "n_jobs", "match_how"],
        )
        w.writeheader()
        w.writerows(all_recs)

    ff_not_company = [n for n in ff_names if n.upper() in NON_COMPANY or n in NON_COMPANY]
    lines = [
        "F:\\f company folders vs 2026-27 map",
        f"F:\\f folders: {len(ff_names)}",
        f"2026-27 dest companies: {len(dests)}",
        f"2026-27 job rows: {len(rows)}",
        "",
        f"exact name on F:\\f (append 2026-27 here): {len(exact)}",
        f"same name ignoring punctuation: {len(norm_hit)}",
        f"NOT on F:\\f (would create a new DATA1 company folder): {len(missing)}",
        f"unsorted dests: {len(unsorted)}",
        "",
        "NOT on F:\\f:",
    ]
    for r in missing:
        lines.append(f"  {r['dest_company']}  ({r['n_jobs']} jobs, {r['match_how']})")
    lines.append("")
    lines.append("norm-only matches (rename dest to F:\\f spelling if different):")
    for r in norm_hit:
        if r["dest_company"] != r["ff_name"]:
            lines.append(f"  MAP={r['dest_company']}  ->  FF={r['ff_name']}")
    if not any(r["dest_company"] != r["ff_name"] for r in norm_hit):
        lines.append("  (none)")
    lines.append("")
    lines.append("F:\\f names tagged as likely non-company piles:")
    for n in ff_not_company:
        lines.append(f"  {n}")
    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_TXT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
