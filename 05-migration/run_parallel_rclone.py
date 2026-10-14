"""Upload dest company folders in parallel via rclone WebDAV.

No recopy. Pause the Nextcloud desktop pair first.

  python run_parallel_rclone.py --dest F:\\f --jobs 4 --dry-run
  python run_parallel_rclone.py --dest F:\\f --jobs 4

Requires rclone remote named `nextcloud` (WebDAV). Do not paste passwords.
Jobs 1-6, transfers 4 per job. If SAVEPOINT / disk alarm: Ctrl+C, rerun --jobs 1.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from split_sync_batches import list_roots, split

HERE = Path(__file__).resolve().parent


def rclone_copy(src: Path, remote: str, folder: str, transfers: int, dry: bool) -> tuple[str, int, str]:
    dst = f"nextcloud:{remote}/{folder}"
    cmd = [
        "rclone",
        "copy",
        str(src / folder),
        dst,
        "--transfers",
        str(transfers),
        "--checkers",
        "8",
        "--create-empty-src-dirs",
        "--exclude",
        "~$*",
        "--exclude",
        "Thumbs.db",
        "--exclude",
        "desktop.ini",
        "--exclude",
        "*.tmp",
        "--exclude",
        "_COPY_*.csv",
        "--exclude",
        "_UNSORTED_REORG_LOG.csv",
        "--exclude",
        "_SYNC_*.log",
        "--log-level",
        "INFO",
    ]
    if dry:
        cmd.append("--dry-run")
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (p.stdout or "") + (p.stderr or "")
    sec = time.time() - t0
    return folder, p.returncode, f"{sec:.1f}s rc={p.returncode}\n{out[-4000:]}"


def worker(dest: Path, remote: str, folders: list[str], transfers: int, dry: bool, job_id: int, log_dir: Path) -> tuple[int, int, int]:
    ok = fail = 0
    log = log_dir / f"_SYNC_JOB_{job_id:02d}.log"
    with log.open("a", encoding="utf-8") as f:
        f.write(f"job {job_id} folders {len(folders)} dry={dry}\n")
        for name in folders:
            folder, rc, detail = rclone_copy(dest, remote, name, transfers, dry)
            line = f"{'OK' if rc == 0 else 'FAIL'} {folder} {detail.splitlines()[0] if detail else ''}\n"
            print(f"[job {job_id}] {line.strip()}", flush=True)
            f.write(line)
            f.write(detail)
            f.write("\n")
            f.flush()
            if rc == 0:
                ok += 1
            else:
                fail += 1
    return job_id, ok, fail


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", required=True)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--transfers", type=int, default=4)
    ap.add_argument("--remote", default="Backup_data/Final_v2")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dest = Path(args.dest)
    if not dest.exists():
        raise SystemExit(f"DEST not found: {dest}")
    jobs = max(1, min(int(args.jobs), 6))
    transfers = max(1, min(int(args.transfers), 8))
    remote = args.remote.strip().strip("/")
    roots = list_roots(dest)
    batches = split(roots, jobs)
    print(f"dest      : {dest}")
    print(f"remote    : nextcloud:{remote}")
    print(f"jobs      : {len(batches)}")
    print(f"transfers : {transfers} per job")
    print(f"folders   : {sum(len(b) for b in batches)}")
    print(f"dry-run   : {args.dry_run}")
    print("Pause Nextcloud desktop pair first. Ctrl+C if SAVEPOINT / disk alarm.")
    print()
    t0 = time.time()
    ok = fail = 0
    with ThreadPoolExecutor(max_workers=len(batches)) as ex:
        futs = [
            ex.submit(
                worker,
                dest,
                remote,
                [p.name for p in batch],
                transfers,
                args.dry_run,
                i,
                dest,
            )
            for i, batch in enumerate(batches, start=1)
        ]
        for fut in as_completed(futs):
            job_id, j_ok, j_fail = fut.result()
            ok += j_ok
            fail += j_fail
            print(f"job {job_id} done ok={j_ok} fail={j_fail}", flush=True)
    print()
    print(f"ok={ok} fail={fail} seconds={time.time() - t0:.0f}")
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
