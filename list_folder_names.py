"""List all folder names under a path you give.

Usage:
  python list_folder_names.py
  python list_folder_names.py "D:\\some\\folder"
  python list_folder_names.py "D:\\some\\folder" --top-only
  python list_folder_names.py "D:\\some\\folder" --out folders.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def collect_folders(root: Path, recursive: bool) -> list[Path]:
    if recursive:
        return sorted(
            (p for p in root.rglob("*") if p.is_dir()),
            key=lambda p: str(p).lower(),
        )
    return sorted(
        (p for p in root.iterdir() if p.is_dir()),
        key=lambda p: p.name.lower(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print every folder name under a path."
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Folder to scan. If omitted, the program will ask.",
    )
    parser.add_argument(
        "--top-only",
        action="store_true",
        help="Only immediate subfolders, not nested ones.",
    )
    parser.add_argument(
        "--names-only",
        action="store_true",
        help="Print only the folder name, not the full path.",
    )
    parser.add_argument(
        "--out",
        default="",
        help="Optional output text file. Default: folder_names.txt next to this script.",
    )
    args = parser.parse_args()

    raw = args.path or input("Enter the folder path: ").strip().strip('"')
    if not raw:
        print("No path given.", file=sys.stderr)
        return 1

    root = Path(raw).expanduser()
    try:
        root = root.resolve()
    except OSError as exc:
        print(f"Cannot use that path: {exc}", file=sys.stderr)
        return 1

    if not root.exists():
        print(f"Path does not exist: {root}", file=sys.stderr)
        return 1
    if not root.is_dir():
        print(f"Not a folder: {root}", file=sys.stderr)
        return 1

    folders = collect_folders(root, recursive=not args.top_only)
    lines = [p.name if args.names_only else str(p) for p in folders]

    print(f"Root: {root}")
    print(f"Folders found: {len(lines)}")
    print("-" * 40)
    for line in lines:
        print(line)

    out = Path(args.out) if args.out else Path(__file__).resolve().parent / "folder_names.txt"
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    print("-" * 40)
    print(f"Saved: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
