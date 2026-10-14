"""Rebuild STRUCTURED_COPY_MAP_2026_27.csv from C:\\SARASWATHI_2026_27.

Used after the CSV was truncated. Does not copy from HDD.
Applies F:\\f spelling remaps:
  SEL JEGAT PRINTER PRIVATE LIMITED -> SEL JEGAT PRINTERS PRIVATE LIMITED
  PALANIAPPA MOTOR PRIVATE LIMITED  -> PALANIAPPA'S MOTORS (exact F:\\f name)
"""
from __future__ import annotations

import csv
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEST = Path(r"C:\SARASWATHI_2026_27")
FF = HERE / "F_F_COMPANY_FOLDERS.txt"
OUT = HERE / "STRUCTURED_COPY_MAP_2026_27.csv"
REPORT = HERE / "FF_REMAP_2026_27.txt"

OS_ROOT = Path(r"D:\OFFICE SARASWATHI\2026-27\UPLOADED FORMS")
CH_ROOT = Path(r"D:\OFFICE SARASWATHI\CHENNAI OFFICE BACK UP\2026-2027\UPLOADED FORMS")


def ff_palaniappa() -> str:
    for line in FF.read_text(encoding="utf-8").splitlines():
        name = line.strip()
        if "PALANIAPPA" in name.upper() and "MOTOR" in name.upper():
            return name
    return "PALANIAPPA'S MOTORS PRIVATE LIMITED"


def infer_office_month(folder: str) -> tuple[str, str, str]:
    """Best-effort source path. HDD may be unplugged."""
    office = "CHENNAI" if folder.endswith("_CHENNAI") else "OS"
    src_name = folder[: -len("_CHENNAI")] if folder.endswith("_CHENNAI") else folder
    root = CH_ROOT if office == "CHENNAI" else OS_ROOT
    month = ""
    source = str(root / src_name)
    if root.exists():
        for month_dir in sorted(p for p in root.iterdir() if p.is_dir()):
            cand = month_dir / src_name
            if cand.exists():
                month = month_dir.name
                source = str(cand)
                break
    return office, month, source


def walk_jobs() -> list[dict]:
    rows: list[dict] = []
    for company_dir in sorted(p for p in DEST.iterdir() if p.is_dir()):
        year_dir = company_dir / "2026-27"
        if not year_dir.is_dir():
            continue
        for job in sorted(p for p in year_dir.iterdir() if p.is_dir()):
            office, month, source = infer_office_month(job.name)
            rows.append(
                {
                    "dest_relative": str(Path(company_dir.name) / "2026-27" / job.name),
                    "dest_company": company_dir.name,
                    "dest_year": "2026-27",
                    "dest_folder": job.name,
                    "source_path": source,
                    "office": office,
                    "month": month,
                    "match_how": "from_dest",
                    "guess": job.name,
                    "origin": "HDD_2026_27",
                }
            )
    return rows


def move_company(old: str, new: str, notes: list[str]) -> None:
    src = DEST / old
    dst = DEST / new
    if not src.exists():
        notes.append(f"SKIP move, missing: {old}")
        return
    dst.mkdir(parents=True, exist_ok=True)
    year_src = src / "2026-27"
    year_dst = dst / "2026-27"
    year_dst.mkdir(parents=True, exist_ok=True)
    if year_src.is_dir():
        for job in year_src.iterdir():
            target = year_dst / job.name
            if target.exists():
                notes.append(f"KEEP both, dest exists: {target}")
                continue
            shutil.move(str(job), str(target))
            notes.append(f"MOVED {job} -> {target}")
        try:
            year_src.rmdir()
            src.rmdir()
        except OSError:
            notes.append(f"LEFT leftover: {src}")
    else:
        notes.append(f"NO 2026-27 under {old}")


def main() -> None:
    pal = ff_palaniappa()
    remaps = {
        "SEL JEGAT PRINTER PRIVATE LIMITED": "SEL JEGAT PRINTERS PRIVATE LIMITED",
        "PALANIAPPA MOTOR PRIVATE LIMITED": pal,
    }
    notes: list[str] = []
    for old, new in remaps.items():
        move_company(old, new, notes)

    rows = walk_jobs()
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "dest_relative",
                "dest_company",
                "dest_year",
                "dest_folder",
                "source_path",
                "office",
                "month",
                "match_how",
                "guess",
                "origin",
            ],
        )
        w.writeheader()
        w.writerows(rows)

    companies = sorted({r["dest_company"] for r in rows})
    REPORT.write_text(
        "\n".join(
            [
                f"rebuilt rows: {len(rows)}",
                f"dest companies: {len(companies)}",
                f"palaniappa dest: {pal}",
                "",
                "moves:",
                *notes,
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(REPORT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
