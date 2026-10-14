"""Split dest company folders into disjoint sync jobs.

No recopy. No E:/F: source. Run on the laptop that has the copied tree.

  python split_sync_batches.py --dest F:\\f --jobs 4
  python split_sync_batches.py --dest F:\\f --jobs 4 --write-rclone

Then run the printed rclone / Nextcloud pairs. Default jobs=4 so RDS
(db.t4g.micro) is not flooded. Do not raise --jobs above 6.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "sync_batches"

SKIP_NAMES = {
    "_COPY_LOG.csv",
    "_COPY_MISSING.csv",
    "_UNSORTED_REORG_LOG.csv",
    "UNSORTED_DEST_REORG_PLAN.csv",
    "desktop.ini",
    "Thumbs.db",
}


def list_roots(dest: Path) -> list[Path]:
    roots: list[Path] = []
    for p in dest.iterdir():
        if p.name in SKIP_NAMES or p.name.startswith("_COPY"):
            continue
        if p.name.startswith("~"):
            continue
        if p.is_dir():
            if p.name.upper() == "_UNSORTED":
                # empty leftover dir is skippable; if anything remains, last batch
                try:
                    if not any(p.iterdir()):
                        continue
                except OSError:
                    continue
            roots.append(p)
    roots.sort(key=lambda x: x.name.upper())
    return roots


def split(roots: list[Path], jobs: int) -> list[list[Path]]:
    jobs = max(1, min(jobs, 6))
    batches: list[list[Path]] = [[] for _ in range(jobs)]
    # round-robin so each job gets mixed sizes, not all A-C then all huge Z
    for i, r in enumerate(roots):
        batches[i % jobs].append(r)
    return [b for b in batches if b]


def write_batches(batches: list[list[Path]], dest: Path, remote: str, write_rclone: bool) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = OUT / "SYNC_BATCHES.txt"
    csv_path = OUT / "SYNC_BATCHES.csv"
    lines = [
        f"dest {dest}",
        f"remote {remote}",
        f"jobs {len(batches)}",
        f"folders {sum(len(b) for b in batches)}",
        "Do not recopy. Pause the Nextcloud desktop pair before rclone.",
        "Keep --transfers 4 and at most 4 rclone processes.",
        "If SAVEPOINT / disk alarm: stop extra jobs, leave 1 running.",
        "",
    ]
    csv_rows: list[list[str]] = [["batch", "n", "folder"]]
    rclone_lines: list[str] = [
        "@echo off",
        "REM Generated. Prefer: python run_parallel_rclone.py --dest F:\\f --jobs 4",
        "REM rclone remote name = nextcloud (WebDAV). App password only. Do not paste in chat.",
        "REM Each job copies whole company folders from its batch_NN.txt (not --files-from).",
        "",
        f"python \"{HERE / 'run_parallel_rclone.py'}\" --dest \"{dest}\" --jobs {len(batches)} --remote \"{remote}\"",
        "",
    ]
    for i, batch in enumerate(batches, start=1):
        name = f"batch_{i:02d}.txt"
        bpath = OUT / name
        bpath.write_text("\n".join(p.name for p in batch) + "\n", encoding="utf-8")
        lines.append(f"=== {name}  folders={len(batch)} ===")
        for p in batch:
            lines.append(f"  {p.name}")
            csv_rows.append([str(i), str(len(batch)), p.name])
        lines.append("")
    summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(csv_rows)
    if write_rclone:
        bat = OUT / "run_rclone_parallel.bat"
        bat.write_text("\n".join(rclone_lines) + "\n", encoding="utf-8")
        print(f"rclone bat: {bat}")
    print(f"summary : {summary}")
    print(f"csv     : {csv_path}")
    print(f"jobs    : {len(batches)}")
    print(f"folders : {sum(len(b) for b in batches)}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Split dest folders into parallel sync jobs")
    ap.add_argument("--dest", required=True, help="Copied tree, e.g. F:\\f")
    ap.add_argument("--jobs", type=int, default=4, help="Disjoint jobs (1-6). Default 4.")
    ap.add_argument("--remote", default="Backup_data/Final_v2", help="Nextcloud path under the user")
    ap.add_argument("--write-rclone", action="store_true", help="Also write run_rclone_parallel.bat")
    args = ap.parse_args()
    dest = Path(args.dest)
    if not dest.exists():
        raise SystemExit(f"DEST not found: {dest}\nRun this on the laptop that has the copied tree.")
    jobs = max(1, min(int(args.jobs), 6))
    roots = list_roots(dest)
    if not roots:
        raise SystemExit(f"No company folders under {dest}")
    batches = split(roots, jobs)
    write_batches(batches, dest, args.remote.strip().strip("/"), args.write_rclone)
    print()
    print("Nextcloud client alternative: Add folder pair per batch folder list,")
    print("all pointing at the same remote parent. Max 4 pairs. Pause extra if SAVEPOINT.")


if __name__ == "__main__":
    main()
