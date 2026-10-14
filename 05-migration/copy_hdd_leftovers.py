"""Copy previous COPY_FAILED_AND_MISSING folders from D:\\OFFICE SARASWATHI.

Sources verified on this HDD. Dest uses existing F:\\f company names where they exist.
Year 2024-24 from the old map is corrected to 2024-25.
GREEN WEALTH 2022-23 folder was not found on D: and is skipped.
"""
from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEST_ROOT = Path(r"C:\SARASWATHI_LEFTOVERS")
LOG = HERE / "HDD_LEFTOVER_COPY_LOG.csv"
ROBOCOPY_OK = set(range(0, 8))

JOBS = [
    {
        "company": "ADR PLASTIC PRIVATE LIMITED",
        "year": "2024-25",
        "source": Path(r"D:\OFFICE SARASWATHI\2024-25\SEARCH AND STATUS REPORT\ADR PLASTICS PRIVATE LIMITED-03.06.2024"),
    },
    {
        "company": "CONCRETIA ROCK PRODUCTS PRIVATE LIMITED",
        "year": "2017-18",
        "source": Path(r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\MARCH-18\Uploaded on 28 & 29.03.2018 CONCRETIA ROCK PRODUCTS PRIVATE LIMITED- MGT-14 & SH-7"),
    },
    {
        "company": "GEOMEO INFORMATICS PRIVATE LIMITED",
        "year": "2017-18",
        "source": Path(r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\OCTOBER-17\Uploaded on 10.10.17 GEOMEO INFORMATICS PRIVATE LIMITED-AOC-4;MGT-7;ADT-1"),
    },
    {
        "company": "MYSTEVA SOLAR GREEN ENERGY PRIVATE LIMITED",
        "year": "2024-25",
        "source": Path(r"D:\OFFICE SARASWATHI\2024-25\RESOLUTIONS\1.BANK ACCOUNT OPENING RESOLUTIONS\MYSTEVA SOLAR GREEN ENERGY PRIVATE LIMITED"),
    },
    {
        "company": "MYSTEVA SOLAR GREEN ENERGY PRIVATE LIMITED",
        "year": "2024-25",
        "source": Path(r"D:\OFFICE SARASWATHI\2024-25\RESOLUTIONS\2.GST RESOLUTIONS\MYSTEVA SOLAR GREEN ENERGY PRIVATE LIMITED-GST RESOLUTION"),
    },
    {
        "company": "ONDEOS TECHNOLOGIES PRIVATE LIMITED",
        "year": "2017-18",
        "source": Path(r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\SEPTEMBER-17\Uploaded on 04.09.2017 ONDEOS TECHNOLOGIES PRIVATE LIMITED-MGT-14;STK-2"),
    },
    {
        "company": "KIRUBA SUSTAINABLE AGRICULTURE FARMERS PRODUCER COMPANY LIMITED",
        "year": "2022-23",
        "source": Path(r"D:\OFFICE SARASWATHI\2022-23\UPLOADED FORMS\4.JULY\UPLOADED ON 07.07.2022- PALANIYAPPAN  MURUGESAN FOR KIRUBA SUSTAINABLE AGRICULTURE FARMERS PRODUCER COMPANY LIMITED- DIR-3"),
    },
    {
        "company": "P S N SPINNERS PRIVATE LIMITED",
        "year": "2017-18",
        "source": Path(r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\FEBRUARY-18\Uploaded on 23.02.2018 P S N SPINNERS PRIVATE LIMITED-RUN FORM-RAJANARAYANA CORPORATE SERVICES PRIVATE LIMITED-RUN Form"),
    },
    {
        "company": "PRIDE INDIA PROPERTIES PRIVATE LIMITED &AMBIKA WOODS PRIVATE LIMITED&UMIYA TIMBER PRIVATE LIMITED",
        "year": "2024-25",
        "source": Path(r"D:\OFFICE SARASWATHI\2024-25\UPLOADED FORMS\2.MAY 2024\UPLOADED ON 03.05.2024 PRIDE INDIA PROPERTIES PRIVATE LIMITED &AMBIKA WOODS PRIVATE LIMITED&UMIYA TIMBER PRIVATE LIMITED WEB KYC"),
    },
    {
        "company": "PRIDE INDIA PROPERTIES PRIVATE LIMITED &AMBIKA WOODS PRIVATE LIMITED&UMIYA TIMBER PRIVATE LIMITED",
        "year": "2025-26",
        "source": Path(r"D:\OFFICE SARASWATHI\2025-26\UPLOADED FORMS\4. JULY 2025\UPLOADED ON 03.07.2025 PRIDE INDIA PROPERTIES PRIVATE LIMITED &AMBIKA WOODS PRIVATE LIMITED&UMIYA TIMBER PRIVATE LIMITED KYC WEB"),
    },
    {
        "company": "QUADRATIC STRUCTURE INDIA PRIVATE LIMITED",
        "year": "2017-18",
        "source": Path(r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\AUGUEST-17\Uploaded on 24.08.2017QUADRATIC STRUCTURE INDIA PRIVATE LIMITED-MGT-14;SH-7"),
    },
    {
        "company": "SKYWING HOLIDAYS PRIVATE LIMITED",
        "year": "2017-18",
        "source": Path(r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\SEPTEMBER-17\Uploaded on 01.09.2017 SKYWING HOLIDAYS PRIVATE LIMITED-AOC-4;MGT-7"),
    },
    {
        "company": "SKYWING HOLIDAYS PRIVATE LIMITED",
        "year": "2017-18",
        "source": Path(r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\AUGUEST-17\Uploaded on 18.08.2017 SKYWING HOLIDAYS PRIVATE LIMITED AOC-4;MGT-7"),
    },
    {
        "company": "SRI YANNARKAY SERVICERS LIMITED",
        "year": "2017-18",
        "source": Path(r"D:\OFFICE SARASWATHI\2017-18\UPLOADED FORMS\OCTOBER-17\Uploaded on 06.10.17&07.10.17 SRI YANNARKAY SERVICERS LTD-MGT-7;AOC-4"),
    },
    {
        "company": "SWAMIYARMADAM RATHNA MEMORIAL HOSIPITAL PRIVATE LIMITED",
        "year": "2024-25",
        "source": Path(r"D:\OFFICE SARASWATHI\2024-25\UPLOADED FORMS\3.JUNE 2024\UPLOADED ON 14.06.2024 SWAMIYARMADAM RATHNA MEMORIAL HOSPITAL PRIVATE LIMITED AND RATHNA FERTILITY CENTRE INDIA PRIVATE LIMITED"),
    },
    {
        "company": "SWAMIYARMADAM RATHNA MEMORIAL HOSIPITAL PRIVATE LIMITED",
        "year": "2024-25",
        "source": Path(r"D:\OFFICE SARASWATHI\2024-25\UPLOADED FORMS\5.AUGUST 2024\UPLOADED ON 23.08.2024 SWAMIYARMADAM RATHNA MEMORIAL HOSPITAL PRIVATE LIMITED AND RATHNA FERTILITY CENTRE INDIA PRIVATE LIMITED"),
    },
]


def long_path(path: Path | str) -> str:
    s = os.path.abspath(str(path))
    if s.startswith("\\\\?\\") or s.startswith("\\\\.\\"):
        return s
    if s.startswith("\\\\"):
        return "\\\\?\\UNC\\" + s[2:]
    return "\\\\?\\" + s


def dest_for(job: dict) -> Path:
    return DEST_ROOT / job["company"] / job["year"] / job["source"].name


def copy_tree(src: Path, dst: Path) -> tuple[int, int]:
    """Copy files; skip dest files of the same size. Return (copied, skipped)."""
    copied = skipped = 0
    src_root = Path(long_path(src))
    dst_root = Path(long_path(dst))
    dst_root.mkdir(parents=True, exist_ok=True)
    for path in src_root.rglob("*"):
        if path.is_dir():
            Path(long_path(dst_root / path.relative_to(src_root))).mkdir(parents=True, exist_ok=True)
            continue
        if not path.is_file():
            continue
        rel = path.relative_to(src_root)
        target = Path(long_path(dst_root / rel))
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            size = path.stat().st_size
            if target.exists() and target.stat().st_size == size:
                skipped += 1
                continue
        except OSError:
            pass
        shutil.copy2(path, target)
        copied += 1
    return copied, skipped


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = []
    ok = missing = failed = 0
    print(f"dest={DEST_ROOT}")
    print(f"jobs={len(JOBS)}")
    for i, job in enumerate(JOBS, 1):
        src = job["source"]
        dst = dest_for(job)
        rel = f"{job['company']}\\{job['year']}\\{src.name}"
        exists = src.is_dir()
        status = "ok"
        note = ""
        if not exists:
            status = "missing"
            missing += 1
            note = "source_not_found"
        elif args.dry_run:
            status = "dry_ok"
            ok += 1
        else:
            try:
                copied, skipped = copy_tree(src, dst)
                status = "ok"
                ok += 1
                note = f"copied={copied} skipped={skipped}"
            except OSError as e:
                status = "failed"
                failed += 1
                note = str(e)
        print(f"[{i}/{len(JOBS)}] {status}  {rel}")
        if status != "ok" and status != "dry_ok":
            print(f"    src={src}")
            print(f"    note={note}")
        rows.append(
            {
                "status": status,
                "company": job["company"],
                "year": job["year"],
                "source_path": str(src),
                "dest_relative": rel,
                "note": note,
            }
        )

    with LOG.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["status", "company", "year", "source_path", "dest_relative", "note"])
        w.writeheader()
        w.writerows(rows)
    print(f"ok={ok} missing={missing} failed={failed} log={LOG}")
    return 1 if missing or failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
