"""Reorganize already-copied dest tree. No E:/F: recopy.

Reads UNSORTED_DEST_REORG_PLAN.csv and moves/deletes under DEST only.

  python reorg_unsorted_dest.py --dest F:\\f --dry-run
  python reorg_unsorted_dest.py --dest F:\\f --apply
"""
from __future__ import annotations

import argparse
import csv
import shutil
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN = HERE / "UNSORTED_DEST_REORG_PLAN.csv"


def load_plan(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def nonempty(p: Path) -> bool:
    try:
        next(p.iterdir())
        return True
    except StopIteration:
        return False
    except OSError:
        return False


def move_dir(src: Path, dst: Path) -> str:
    if dst.exists():
        return "SKIP_TARGET_EXISTS"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return "MOVED"


def rmtree(p: Path) -> str:
    if not p.exists():
        return "SKIP_MISSING"
    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink()
    return "DELETED"


def main() -> None:
    ap = argparse.ArgumentParser(description="Dest-only unsorted reorg (no source recopy)")
    ap.add_argument("--dest", required=True, help="Copied tree root, e.g. F:\\f")
    ap.add_argument("--plan", default=str(PLAN))
    ap.add_argument("--dry-run", action="store_true", help="Print actions only (default if --apply omitted)")
    ap.add_argument("--apply", action="store_true", help="Actually move/delete on dest")
    args = ap.parse_args()

    dest = Path(args.dest)
    apply = bool(args.apply) and not args.dry_run
    if not apply:
        args.dry_run = True
    if not dest.exists():
        raise SystemExit(f"DEST not found: {dest}\nRun this on the laptop that has the copied tree.")
    rows = load_plan(Path(args.plan))
    log_path = dest / "_UNSORTED_REORG_LOG.csv"
    print(f"dest   : {dest}")
    print(f"plan   : {args.plan}")
    print(f"mode   : {'APPLY' if apply else 'DRY-RUN'}")
    print(f"rows   : {len(rows)}")
    print()

    counts: dict[str, int] = {}
    log_rows: list[list[str]] = []

    def rec(action: str, src: str, dst: str, result: str) -> None:
        counts[result] = counts.get(result, 0) + 1
        print(f"  {result:22} {action} | {src} -> {dst}")
        log_rows.append([action, src, dst, result])

    for r in rows:
        action = (r.get("action") or "").strip()
        src_rel = (r.get("src_dest_rel") or "").strip()
        child = (r.get("child") or "").strip()
        target_rel = (r.get("target_rel") or "").strip()
        src = dest / src_rel
        child_path = src / child if child else src
        target = dest / target_rel if target_rel else None

        if action == "MOVE_DEST_CHILD":
            if not child_path.exists():
                rec(action, str(child_path), str(target), "SKIP_SOURCE_MISSING")
                continue
            if target is None:
                rec(action, str(child_path), "", "SKIP_NO_TARGET")
                continue
            if target.exists():
                rec(action, str(child_path), str(target), "SKIP_TARGET_EXISTS")
                if apply:
                    rmtree(child_path)
                    rec("DELETE_DUP_AFTER_SKIP", str(child_path), "", "DELETED")
                continue
            if apply:
                result = move_dir(child_path, target)
                rec(action, str(child_path), str(target), result)
            else:
                rec(action, str(child_path), str(target), "DRY_MOVE")

        elif action == "DELETE_DEST_CHILD":
            if not child_path.exists():
                rec(action, str(child_path), "", "SKIP_SOURCE_MISSING")
                continue
            if apply:
                rec(action, str(child_path), "", rmtree(child_path))
            else:
                rec(action, str(child_path), "", "DRY_DELETE_CHILD")

        elif action == "DELETE_UNSORTED_DEST":
            if not src.exists():
                rec(action, str(src), "", "SKIP_SOURCE_MISSING")
                continue
            if apply:
                rec(action, str(src), "", rmtree(src))
            else:
                rec(action, str(src), "", "DRY_DELETE_PILE")

        elif action == "DELETE_UNSORTED_IF_EMPTY":
            if not src.exists():
                rec(action, str(src), "", "SKIP_SOURCE_MISSING")
                continue
            leftover = []
            try:
                leftover = [p.name for p in src.iterdir()]
            except OSError as e:
                rec(action, str(src), "", f"ERROR:{e}")
                continue
            if leftover:
                rec(action, str(src), "", "KEEP_HAS_LEFTOVER:" + "|".join(leftover[:20]))
            elif apply:
                rec(action, str(src), "", rmtree(src))
            else:
                rec(action, str(src), "", "DRY_DELETE_EMPTY")

        elif action in {"UNMATCHED_CHILD", "LEAVE_FILE"}:
            rec(action, str(child_path), "", "NO_OP_" + action)

        else:
            rec(action, str(child_path), str(target or ""), "UNKNOWN_ACTION")

    # prune empty _UNSORTED company folders
    unsorted = dest / "_UNSORTED"
    if unsorted.exists():
        for p in sorted(unsorted.rglob("*"), key=lambda x: len(str(x)), reverse=True):
            if p.is_dir() and not nonempty(p):
                if apply:
                    p.rmdir()
                    rec("PRUNE_EMPTY", str(p), "", "DELETED")
                else:
                    rec("PRUNE_EMPTY", str(p), "", "DRY_PRUNE")
        if unsorted.is_dir() and not nonempty(unsorted):
            if apply:
                unsorted.rmdir()
                rec("PRUNE_EMPTY", str(unsorted), "", "DELETED")
            else:
                rec("PRUNE_EMPTY", str(unsorted), "", "DRY_PRUNE")

    print()
    print("counts", dict(sorted(counts.items())))
    if apply:
        with log_path.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["action", "src", "dst", "result"])
            w.writerows(log_rows)
        print("log", log_path)
    else:
        print("dry-run only; pass --apply on the laptop that has dest")


if __name__ == "__main__":
    main()
