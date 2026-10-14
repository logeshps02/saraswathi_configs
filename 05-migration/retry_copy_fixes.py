"""Retry only the two leftover copy issues.

Fix 1 — dest path too long (6 rows):
  Source still exists. Copy again into the renamed dest root F:\\Final
  (shorter than Final_Ordered_Folders_30_08_2026).

Fix 2 — 2017-18: sheet had the short/wrong name; real folder has extra forms after ';'.
  Copy only the 6 correct folders (not both names).

Do NOT rerun the full 6863 map.

On the backup PC:
  python retry_copy_fixes.py --dest F:\\Final --dry-run
  python retry_copy_fixes.py --dest F:\\Final
Total jobs: 6 long-dest + 6 correct 2017-18 folders = 12."""
from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROBOCOPY_OK = set(range(0, 8))

# dest_relative is Company\\Year\\folder  (same layout as the finished copy)
FIX_LONG_DEST = [
    {
        "issue": "long_dest",
        "company": "KIRUBA SUSTAINABLE AGRICULTURE FARMERS PRODUCER COMPANY LIMITED - PALANIYAPPAN MURUGESAN",
        "year": "2022-23",
        "source_path": r"F:\2022-2023\UPLOADED FORMS\4.JULY\UPLOADED ON 07.07.2022- PALANIYAPPAN  MURUGESAN FOR KIRUBA SUSTAINABLE AGRICULTURE FARMERS PRODUCER COMPANY LIMITED- DIR-3",
        "dest_relative": r"KIRUBA SUSTAINABLE AGRICULTURE FARMERS PRODUCER COMPANY LIMITED - PALANIYAPPAN MURUGESAN\2022-23\UPLOADED ON 07.07.2022- PALANIYAPPAN MURUGESAN FOR KIRUBA SUSTAINABLE AGRICULTURE FARMERS PRODUCER COMPANY LIMITED- DIR-3",
    },
    {
        "issue": "long_dest",
        "company": "P S N SPINNERS PRIVATE LIMITED-RUN FORM-RAJANARAYANA CORPORATE SERVICES PRIVATE LIMITED",
        "year": "2017-18",
        "source_path": r"F:\2017-18\UPLOADED FORMS\FEBRUARY-18\Uploaded on 23.02.2018 P S N SPINNERS PRIVATE LIMITED-RUN FORM-RAJANARAYANA CORPORATE SERVICES PRIVATE LIMITED-RUN Form",
        "dest_relative": r"P S N SPINNERS PRIVATE LIMITED-RUN FORM-RAJANARAYANA CORPORATE SERVICES PRIVATE LIMITED\2017-18\Uploaded on 23.02.2018 P S N SPINNERS PRIVATE LIMITED-RUN FORM-RAJANARAYANA CORPORATE SERVICES PRIVATE LIMITED-RUN Form",
    },
    {
        "issue": "long_dest",
        "company": "PRIDE INDIA PROPERTIES PRIVATE LIMITED &AMBIKA WOODS PRIVATE LIMITED&UMIYA TIMBER PRIVATE LIMITED",
        "year": "2024-25",
        "source_path": r"F:\2024-2025\UPLOADED FORMS\2.MAY 2024\UPLOADED ON 03.05.2024 PRIDE INDIA PROPERTIES PRIVATE LIMITED &AMBIKA WOODS PRIVATE LIMITED&UMIYA TIMBER PRIVATE LIMITED WEB KYC",
        "dest_relative": r"PRIDE INDIA PROPERTIES PRIVATE LIMITED &AMBIKA WOODS PRIVATE LIMITED&UMIYA TIMBER PRIVATE LIMITED\2024-25\UPLOADED ON 03.05.2024 PRIDE INDIA PROPERTIES PRIVATE LIMITED &AMBIKA WOODS PRIVATE LIMITED&UMIYA TIMBER PRIVATE LIMITED WEB KYC",
    },
    {
        "issue": "long_dest",
        "company": "PRIDE INDIA PROPERTIES PRIVATE LIMITED &AMBIKA WOODS PRIVATE LIMITED&UMIYA TIMBER PRIVATE LIMITED",
        "year": "2025-26",
        "source_path": r"E:\2025-26\os\UPLOADED FORMS\4. JULY 2025\UPLOADED ON 03.07.2025 PRIDE INDIA PROPERTIES PRIVATE LIMITED &AMBIKA WOODS PRIVATE LIMITED&UMIYA TIMBER PRIVATE LIMITED KYC WEB",
        "dest_relative": r"PRIDE INDIA PROPERTIES PRIVATE LIMITED &AMBIKA WOODS PRIVATE LIMITED&UMIYA TIMBER PRIVATE LIMITED\2025-26\UPLOADED ON 03.07.2025 PRIDE INDIA PROPERTIES PRIVATE LIMITED &AMBIKA WOODS PRIVATE LIMITED&UMIYA TIMBER PRIVATE LIMITED KYC WEB",
    },
    {
        "issue": "long_dest",
        "company": "SWAMIYARMADAM RATHNA MEMORIAL HOSPITAL PRIVATE LIMITED AND RATHNA FERTILITY CENTRE INDIA PRIVATE LIMITED",
        "year": "2024-25",
        "source_path": r"F:\2024-2025\UPLOADED FORMS\3.JUNE 2024\UPLOADED ON 14.06.2024 SWAMIYARMADAM RATHNA MEMORIAL HOSPITAL PRIVATE LIMITED AND RATHNA FERTILITY CENTRE INDIA PRIVATE LIMITED",
        "dest_relative": r"SWAMIYARMADAM RATHNA MEMORIAL HOSPITAL PRIVATE LIMITED AND RATHNA FERTILITY CENTRE INDIA PRIVATE LIMITED\2024-25\UPLOADED ON 14.06.2024 SWAMIYARMADAM RATHNA MEMORIAL HOSPITAL PRIVATE LIMITED AND RATHNA FERTILITY CENTRE INDIA PRIVATE LIMITED",
    },
    {
        "issue": "long_dest",
        "company": "SWAMIYARMADAM RATHNA MEMORIAL HOSPITAL PRIVATE LIMITED AND RATHNA FERTILITY CENTRE INDIA PRIVATE LIMITED",
        "year": "2024-25",
        "source_path": r"F:\2024-2025\UPLOADED FORMS\5.AUGUST 2024\UPLOADED ON 23.08.2024 SWAMIYARMADAM RATHNA MEMORIAL HOSPITAL PRIVATE LIMITED AND RATHNA FERTILITY CENTRE INDIA PRIVATE LIMITED",
        "dest_relative": r"SWAMIYARMADAM RATHNA MEMORIAL HOSPITAL PRIVATE LIMITED AND RATHNA FERTILITY CENTRE INDIA PRIVATE LIMITED\2024-25\UPLOADED ON 23.08.2024 SWAMIYARMADAM RATHNA MEMORIAL HOSPITAL PRIVATE LIMITED AND RATHNA FERTILITY CENTRE INDIA PRIVATE LIMITED",
    },
]

# Only the 6 correct folders (with extra form names after ';'). Short/wrong names skipped.
FIX_2017_18 = [
    {
        "issue": "2017_18_real_folder",
        "company": "GEOMEO INFORMATICS PRIVATE LIMITED",
        "year": "2017-18",
        "source_path": r"F:\2017-18\UPLOADED FORMS\OCTOBER-17\Uploaded on 10.10.17 GEOMEO INFORMATICS PRIVATE LIMITED-AOC-4;MGT-7;ADT-1",
    },
    {
        "issue": "2017_18_real_folder",
        "company": "ONDEOS TECHNOLOGIES PRIVATE LIMITED",
        "year": "2017-18",
        "source_path": r"F:\2017-18\UPLOADED FORMS\SEPTEMBER-17\Uploaded on 04.09.2017 ONDEOS TECHNOLOGIES PRIVATE LIMITED-MGT-14;STK-2",
    },
    {
        "issue": "2017_18_real_folder",
        "company": "QUADRATIC STRUCTURE INDIA PRIVATE LIMITED",
        "year": "2017-18",
        "source_path": r"F:\2017-18\UPLOADED FORMS\AUGUEST-17\Uploaded on 24.08.2017QUADRATIC STRUCTURE INDIA PRIVATE LIMITED-MGT-14;SH-7",
    },
    {
        "issue": "2017_18_real_folder",
        "company": "SKYWING HOLIDAYS PRIVATE LIMITED",
        "year": "2017-18",
        "source_path": r"F:\2017-18\UPLOADED FORMS\SEPTEMBER-17\Uploaded on 01.09.2017 SKYWING HOLIDAYS PRIVATE LIMITED-AOC-4;MGT-7",
    },
    {
        "issue": "2017_18_real_folder",
        "company": "SKYWING HOLIDAYS PRIVATE LIMITED",
        "year": "2017-18",
        "source_path": r"F:\2017-18\UPLOADED FORMS\AUGUEST-17\Uploaded on 18.08.2017 SKYWING HOLIDAYS PRIVATE LIMITED AOC-4;MGT-7",
    },
    {
        "issue": "2017_18_real_folder",
        "company": "SRI YANNARKAY SERVICERS LIMITED",
        "year": "2017-18",
        "source_path": r"F:\2017-18\UPLOADED FORMS\OCTOBER-17\Uploaded on 06.10.17&07.10.17 SRI YANNARKAY SERVICERS LTD-MGT-7;AOC-4",
    },
]


def folder_name(src: str) -> str:
    return src.rstrip("\\").split("\\")[-1]


def long_path(path: Path | str) -> str:
    """Windows extended path so dest folders over ~248 chars can be created."""
    s = os.path.abspath(str(path))
    if s.startswith("\\\\?\\") or s.startswith("\\\\.\\"):
        return s
    if s.startswith("\\\\"):
        return "\\\\?\\UNC\\" + s[2:]
    return "\\\\?\\" + s


def jobs() -> list[dict]:
    out = []
    for r in FIX_LONG_DEST:
        out.append(dict(r))
    for r in FIX_2017_18:
        rec = dict(r)
        rec["dest_relative"] = f"{r['company']}\\{r['year']}\\{folder_name(r['source_path'])}"
        out.append(rec)
    return out


def run_robocopy(src: Path, dst: Path) -> tuple[int, str]:
    Path(long_path(dst)).mkdir(parents=True, exist_ok=True)
    cmd = [
        "robocopy",
        long_path(src),
        long_path(dst),
        "/E",
        "/COPY:DAT",
        "/DCOPY:DAT",
        "/R:2",
        "/W:3",
        "/MT:4",
        "/XO",
        "/FFT",
        "/NP",
        "/NFL",
        "/NDL",
        "/NJH",
        "/BYTES",
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def copy_tree_python(src: Path, dst: Path) -> tuple[int, int]:
    copied = skipped = 0
    src_root = Path(long_path(src))
    dst_root = Path(long_path(dst))
    dst_root.mkdir(parents=True, exist_ok=True)
    for path in src_root.rglob("*"):
        rel = path.relative_to(src_root)
        target = dst_root / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if not path.is_file():
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if target.exists():
            try:
                if target.stat().st_size == size:
                    skipped += 1
                    continue
            except OSError:
                pass
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        copied += 1
    return copied, skipped


def main() -> None:
    ap = argparse.ArgumentParser(description="Retry 6 long-dest fails + 2017-18 real folders")
    ap.add_argument("--dest", default=r"F:\Final", help="Renamed dest root (default F:\\Final)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--only",
        choices=["all", "long", "2017", "remaining"],
        default="all",
        help="all = both; long = 6 dest-too-long; 2017 = 6 correct 2017-18; remaining = 2 SWAMI still failing",
    )
    args = ap.parse_args()
    dest_root = Path(args.dest)
    rows = jobs()
    if args.only == "long":
        rows = [r for r in rows if r["issue"] == "long_dest"]
    elif args.only == "2017":
        rows = [r for r in rows if r["issue"] == "2017_18_real_folder"]
    elif args.only == "remaining":
        rows = [r for r in rows if "SWAMIYARMADAM" in r.get("dest_relative", "")]

    use_robo = shutil.which("robocopy") and sys.platform.startswith("win")
    print(f"dest     : {dest_root}")
    print(f"jobs     : {len(rows)}")
    print(f"engine   : {'robocopy' if use_robo else 'python shutil'}")
    print(f"dry-run  : {args.dry_run}")
    print()

    if not args.dry_run:
        dest_root.mkdir(parents=True, exist_ok=True)
        log_path = dest_root / "_RETRY_FIXES_LOG.csv"
        miss_path = dest_root / "_RETRY_FIXES_MISSING.csv"
        new_log = not log_path.exists() or log_path.stat().st_size == 0
        new_miss = not miss_path.exists() or miss_path.stat().st_size == 0
        log_f = log_path.open("a", encoding="utf-8-sig", newline="")
        miss_f = miss_path.open("a", encoding="utf-8-sig", newline="")
        log_w = csv.writer(log_f)
        miss_w = csv.writer(miss_f)
        if new_log:
            log_w.writerow(["ok", "issue", "source_path", "dest_relative", "rc_or_note", "full_dest_len", "seconds"])
        if new_miss:
            miss_w.writerow(["issue", "source_path", "dest_relative", "reason"])
    else:
        log_f = miss_f = None
        log_w = miss_w = None

    ok = missing = failed = 0
    try:
        for i, row in enumerate(rows, start=1):
            src = Path(row["source_path"])
            rel = row["dest_relative"]
            dst = dest_root / rel
            full_len = len(str(dst))
            exists = src.exists()
            flag = "OK" if exists else "MISSING"
            print(f"[{i}/{len(rows)}] {row['issue']}  dest_len={full_len}  {flag}")
            print(f"    src  {src}")
            print(f"    dest {dst}")
            if args.dry_run:
                if exists:
                    ok += 1
                else:
                    missing += 1
                continue
            if not exists:
                missing += 1
                miss_w.writerow([row["issue"], str(src), rel, "source_not_found"])
                log_w.writerow([0, row["issue"], str(src), rel, "source_not_found", full_len, 0])
                continue
            t1 = time.time()
            try:
                if use_robo:
                    rc, _out = run_robocopy(src, dst)
                    secs = time.time() - t1
                    if rc in ROBOCOPY_OK:
                        ok += 1
                        log_w.writerow([1, row["issue"], str(src), rel, f"robocopy:{rc}", full_len, f"{secs:.1f}"])
                        print(f"    copied robocopy:{rc} {secs:.1f}s")
                    else:
                        failed += 1
                        log_w.writerow([0, row["issue"], str(src), rel, f"robocopy:{rc}", full_len, f"{secs:.1f}"])
                        print(f"    FAIL robocopy rc={rc}")
                else:
                    copied, skipped = copy_tree_python(src, dst)
                    secs = time.time() - t1
                    ok += 1
                    log_w.writerow(
                        [1, row["issue"], str(src), rel, f"copied={copied} skipped={skipped}", full_len, f"{secs:.1f}"]
                    )
                    print(f"    copied={copied} skipped={skipped} {secs:.1f}s")
            except Exception as exc:
                failed += 1
                log_w.writerow([0, row["issue"], str(src), rel, repr(exc), full_len, 0])
                print(f"    FAIL  {exc}")
            if log_f:
                log_f.flush()
    finally:
        if log_f:
            log_f.close()
        if miss_f:
            miss_f.close()

    print()
    print(f"done  ok={ok} missing={missing} failed={failed}")
    if not args.dry_run:
        print(f"log   {dest_root / '_RETRY_FIXES_LOG.csv'}")
        print(f"miss  {dest_root / '_RETRY_FIXES_MISSING.csv'}")


if __name__ == "__main__":
    main()
