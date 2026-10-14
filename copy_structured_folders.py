"""Copy mapped folders to DEST\\Company\\Year\\folder with live progress.

Stdlib only (no pandas). Uses robocopy when available (Windows, large files).
Resume-safe: existing dest files of the same size are skipped.

Examples:
  python copy_structured_folders.py --dest D:\\SARASWATHI_DOCS --dry-run
  python copy_structured_folders.py --dest D:\\SARASWATHI_DOCS
  python copy_structured_folders.py --dest D:\\SARASWATHI_DOCS --limit 5
"""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_MAP = HERE / "STRUCTURED_COPY_MAP_FINAL.csv"
ROBOCOPY_OK = set(range(0, 8))  # 0-7 = success / extra files


def fmt_bytes(n: int) -> str:
    x = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if x < 1024 or unit == "TB":
            return f"{x:.1f} {unit}" if unit != "B" else f"{int(x)} B"
        x /= 1024
    return f"{n} B"


def fmt_eta(seconds: float) -> str:
    if seconds < 0 or seconds > 48 * 3600:
        return "?"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m:02d}m"
    return f"{m}m {s:02d}s"


def load_rows(map_path: Path) -> list[dict]:
    with map_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    needed = ("dest_relative", "dest_company", "dest_year", "dest_folder", "source_path")
    missing = [c for c in needed if c not in (rows[0] if rows else {})]
    if missing:
        raise SystemExit(f"Map is missing columns: {missing}")
    return rows


def robocopy_available() -> bool:
    return shutil.which("robocopy") is not None


def run_robocopy(src: Path, dst: Path) -> tuple[int, str]:
    dst.mkdir(parents=True, exist_ok=True)
    cmd = [
        "robocopy",
        str(src),
        str(dst),
        "/E",
        "/COPY:DAT",
        "/DCOPY:DAT",
        "/R:2",
        "/W:3",
        "/MT:4",
        "/XO",  # skip dest files that are newer or same date
        "/FFT",
        "/NP",  # per-file % is too noisy across thousands of folders
        "/NFL",
        "/NDL",
        "/NJH",
        "/BYTES",
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def copy_tree_python(src: Path, dst: Path) -> tuple[int, int, int]:
    """Return (files_copied, files_skipped, bytes_copied)."""
    copied = skipped = nbytes = 0
    dst.mkdir(parents=True, exist_ok=True)
    for path in src.rglob("*"):
        rel = path.relative_to(src)
        target = dst / rel
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
        nbytes += size
    return copied, skipped, nbytes


def parse_robocopy_bytes(text: str) -> int | None:
    # With /BYTES, summary lines include Bytes : n
    for line in reversed(text.splitlines()):
        if "Bytes" in line or "bytes" in line:
            nums = [t.replace(",", "") for t in line.split() if t.replace(",", "").isdigit()]
            if nums:
                return int(nums[-1])
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Copy mapped folders to Company\\Year\\folder")
    ap.add_argument("--map", default=str(DEFAULT_MAP), help="STRUCTURED_COPY_MAP_FINAL.csv")
    ap.add_argument("--dest", required=True, help="Destination root, e.g. D:\\SARASWATHI_DOCS")
    ap.add_argument("--dry-run", action="store_true", help="List what would be copied; do not copy")
    ap.add_argument("--limit", type=int, default=0, help="Copy only first N mapped folders (test)")
    ap.add_argument("--start", type=int, default=1, help="1-based row to start from (resume)")
    args = ap.parse_args()

    map_path = Path(args.map)
    if not map_path.is_file():
        raise SystemExit(f"Map not found: {map_path}")
    dest_root = Path(args.dest)
    rows = load_rows(map_path)
    if args.limit:
        rows = rows[: args.limit]
    start_i = max(1, args.start)
    rows = rows[start_i - 1 :]
    total = len(rows)
    use_robo = robocopy_available() and sys.platform.startswith("win")

    log_path = dest_root / "_COPY_LOG.csv" if not args.dry_run else HERE / "COPY_DRY_RUN_LOG.csv"
    miss_path = dest_root / "_COPY_MISSING.csv" if not args.dry_run else HERE / "COPY_DRY_RUN_MISSING.csv"
    if not args.dry_run:
        dest_root.mkdir(parents=True, exist_ok=True)

    print(f"map      : {map_path}")
    print(f"dest     : {dest_root}")
    print(f"folders  : {total} (from row {start_i})")
    print(f"engine   : {'robocopy' if use_robo else 'python shutil'}")
    print(f"dry-run  : {args.dry_run}")
    print()

    t0 = time.time()
    ok = missing = failed = 0
    log_f = log_path.open("a", encoding="utf-8-sig", newline="")
    miss_f = miss_path.open("a", encoding="utf-8-sig", newline="")
    log_w = csv.writer(log_f)
    miss_w = csv.writer(miss_f)
    if log_path.stat().st_size == 0:
        log_w.writerow(["ok", "source_path", "dest_relative", "rc_or_note", "seconds"])
    if miss_path.stat().st_size == 0:
        miss_w.writerow(["source_path", "dest_relative", "reason"])

    try:
        for i, row in enumerate(rows, start=start_i):
            src = Path(str(row["source_path"]).strip())
            rel = str(row["dest_relative"]).strip()
            dst = dest_root / rel
            pct = (i - start_i + 1) / total * 100
            elapsed = time.time() - t0
            done = i - start_i + 1
            eta = elapsed / done * (total - done) if done else 0
            print(
                f"[{done}/{total} {pct:5.1f}%  eta {fmt_eta(eta)}] {rel}",
                flush=True,
            )
            if args.dry_run:
                exists = src.exists()
                print(f"    {'OK' if exists else 'MISSING'}  {src}", flush=True)
                if exists:
                    ok += 1
                else:
                    missing += 1
                    miss_w.writerow([str(src), rel, "source_not_found"])
                continue
            if not src.exists():
                missing += 1
                miss_w.writerow([str(src), rel, "source_not_found"])
                print(f"    MISSING  {src}", flush=True)
                log_w.writerow([0, str(src), rel, "source_not_found", 0])
                continue
            t1 = time.time()
            try:
                if use_robo:
                    rc, out = run_robocopy(src, dst)
                    secs = time.time() - t1
                    if rc in ROBOCOPY_OK:
                        ok += 1
                        log_w.writerow([1, str(src), rel, f"robocopy:{rc}", f"{secs:.1f}"])
                    else:
                        failed += 1
                        log_w.writerow([0, str(src), rel, f"robocopy:{rc}", f"{secs:.1f}"])
                        print(f"    FAIL robocopy rc={rc}", flush=True)
                else:
                    copied, skipped, nbytes = copy_tree_python(src, dst)
                    secs = time.time() - t1
                    ok += 1
                    log_w.writerow(
                        [1, str(src), rel, f"copied={copied} skipped={skipped} {fmt_bytes(nbytes)}", f"{secs:.1f}"]
                    )
                    print(f"    copied {copied} skipped {skipped} {fmt_bytes(nbytes)} in {secs:.0f}s", flush=True)
            except Exception as exc:
                failed += 1
                log_w.writerow([0, str(src), rel, repr(exc), 0])
                print(f"    FAIL  {exc}", flush=True)
            if done % 20 == 0:
                log_f.flush()
                miss_f.flush()
    finally:
        log_f.close()
        miss_f.close()

    elapsed = time.time() - t0
    print()
    print(f"done     : ok={ok} missing={missing} failed={failed}  time={fmt_eta(elapsed)}")
    print(f"log      : {log_path}")
    print(f"missing  : {miss_path}")
    if failed or missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
