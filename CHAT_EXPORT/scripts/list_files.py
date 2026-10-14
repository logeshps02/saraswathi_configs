r"""
List every individual file (with its full path) under one or more root folders
and write them to a text file, using the most robust approach available on
Windows so nothing gets missed.

This version walks MULTIPLE roots (e.g. one for CO files, one for OS files)
and tags each block in the output txt so you can tell them apart.

WHAT WAS FIXED vs. the previous version
---------------------------------------
1. Overwrites the output file by default. The old script used append mode,
   so re-running it produced duplicated blocks inside the same txt file.
2. Long-path support. All paths are opened with the Windows "\\?\" prefix,
   so files whose full path is longer than 260 characters are no longer
   skipped by Windows.
3. Robust walk. Uses os.scandir in a manual loop instead of os.walk. A
   single unreadable child (permission, reparse point, OneDrive placeholder,
   dangling symlink, ...) no longer aborts the entire subtree.
4. Fallback listing. Whenever Python cannot open a folder, the script
   automatically runs
       cmd /c dir /s /b /a-d "<that folder>"
   which uses different Win32 APIs and usually succeeds on OneDrive
   placeholders, junctions, and long paths that Python's stdlib cannot
   handle.
5. Complete audit trail. Every skipped folder, every skipped file, and
   every fallback listing is logged at the bottom of the txt with its
   full path and Windows error, so you can see exactly what (if anything)
   was not collected.
6. Live progress every 2 000 files (file count, folder count, elapsed
   seconds, current folder) and periodic flushing so nothing is lost if
   you have to stop the script.
7. Multiple roots supported. Add / remove entries in the ROOTS list below.

USAGE
-----
1. Install Python from https://python.org (tick "Add python.exe to PATH").
2. Save this file (e.g. on Desktop) as list_files.py.
3. Open Command Prompt (cmd) in the folder where you saved it, run:
       python list_files.py            (overwrite - default)
       python list_files.py --append   (append to existing txt)

The txt is created next to this .py file (default name: all_files_list.txt).

This script only READS your files. It never deletes, moves, or edits anything.
"""

import os
import sys
import time
import subprocess

# ---- settings you can change ----
# Each entry is (label, root_folder).
# The label is written as a header in the txt so you can tell files apart.
#
# NOTE: The earlier all_files_list already covers E:\BACK UP FOLDER (CO) and
# F:\ (OS).  This run only picks up the newly-copied FY 2025-26 folders.
# To re-scan the older folders too, uncomment the first two entries.
ROOTS = [
    # ("CO",     r"E:\BACK UP FOLDER"),   # already listed in the previous run
    # ("OS",     "F:\\"),                 # already listed in the previous run
    ("CO 25-26", r"E:\2025-26\co"),
    ("OS 25-26", r"E:\2025-26\os"),
]
OUTPUT_FILE       = "all_files_list_2025_26.txt"
PROGRESS_INTERVAL = 2000     # print progress every N files
FLUSH_INTERVAL    = 5000     # flush to disk every N files
FALLBACK_TIMEOUT  = 3600     # seconds a single "dir /s /b" fallback may run
# ----------------------------------


# ---------------------------------------------------------------- helpers
def to_long(p):
    r"""Prefix a Windows path with \\?\ so paths > 260 characters can be read."""
    if os.name != "nt":
        return p
    p = os.path.abspath(p)
    if p.startswith("\\\\?\\"):
        return p
    if p.startswith("\\\\"):
        return "\\\\?\\UNC\\" + p[2:]
    return "\\\\?\\" + p


def strip_long(p):
    r"""Reverse of to_long so the written path looks normal (E:\... instead of \\?\E:\...)."""
    if p.startswith("\\\\?\\UNC\\"):
        return "\\\\" + p[len("\\\\?\\UNC\\"):]
    if p.startswith("\\\\?\\"):
        return p[len("\\\\?\\"):]
    return p


def fallback_dir(folder):
    """Last-resort listing via cmd's dir /s /b /a-d.
    Returns (list_of_file_paths, ok_flag)."""
    try:
        r = subprocess.run(
            ["cmd", "/c", "dir", "/s", "/b", "/a-d", folder],
            capture_output=True, text=True,
            encoding="mbcs", errors="replace",
            timeout=FALLBACK_TIMEOUT,
        )
        paths = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
        # dir prints "File Not Found" etc. to stderr; treat any stdout as usable
        return paths, True
    except Exception as e:
        print(f"    fallback dir failed on {folder}: {e}")
        return [], False


# ---------------------------------------------------------------- main walk
def walk_root(label, root, out, counters):
    r"""Walk one root and stream file paths into `out`. counters is a dict
    that is updated in-place so the caller can print a combined summary."""

    print()
    print(f"=== {label}: {root} ===")
    if not os.path.isdir(root):
        print(f"  !! root not found (skipping): {root}")
        out.write(f"\n\n===== ROOT NOT FOUND [{label}]: {root} =====\n")
        counters["missing_roots"].append((label, root))
        return

    long_root = to_long(root)

    file_count     = 0
    folder_count   = 0
    empty_dirs     = []
    skipped_dirs   = []
    skipped_items  = []
    fallback_used  = []

    started        = time.time()
    next_progress  = PROGRESS_INTERVAL
    next_flush     = FLUSH_INTERVAL

    out.write(f"\n\n===== FILE LIST [{label}] - ROOT: {root} =====\n")
    out.write(f"===== started: {time.strftime('%Y-%m-%d %H:%M:%S')} =====\n")
    out.flush()

    stack = [long_root]
    while stack:
        current     = stack.pop()
        display_cur = strip_long(current)
        folder_count += 1

        # 1) Try Python's own listing
        try:
            with os.scandir(current) as it:
                entries = list(it)
        except OSError as e:
            err = f"{e.__class__.__name__} WinError {getattr(e, 'winerror', '?')}: {e.strerror or e}"
            print(f"  ! scandir failed: {display_cur}  ({err})")

            # 2) Try the cmd-dir fallback for this folder
            paths, ok = fallback_dir(display_cur)
            if paths:
                fallback_used.append(display_cur)
                for p in paths:
                    out.write(p + "\n")
                    file_count += 1
                print(f"    fallback recovered {len(paths):,} files under {display_cur}")
            else:
                skipped_dirs.append((display_cur, err))
            continue

        if not entries:
            empty_dirs.append(display_cur)
            continue

        for entry in entries:
            try:
                is_dir = entry.is_dir(follow_symlinks=False)
            except OSError as e:
                err = f"{e.__class__.__name__} WinError {getattr(e, 'winerror', '?')}: {e.strerror or e}"
                p = strip_long(entry.path)
                skipped_items.append((p, err))
                out.write(p + "\n")
                file_count += 1
                continue

            if is_dir:
                stack.append(entry.path)
            else:
                p = strip_long(entry.path)
                out.write(p + "\n")
                file_count += 1

                if file_count >= next_progress:
                    elapsed = time.time() - started
                    print(f"  [{file_count:>7} files | {folder_count:>6} folders | {elapsed:6.0f}s]  in: {display_cur[:110]}")
                    next_progress += PROGRESS_INTERVAL

                if file_count >= next_flush:
                    out.flush()
                    next_flush += FLUSH_INTERVAL

    # ------------------------------ appendices at the bottom of this root's block
    if empty_dirs:
        out.write(f"\n----- EMPTY DIRECTORIES [{label}] -----\n")
        for d in empty_dirs:
            out.write(d + "\n")

    if fallback_used:
        out.write(f"\n----- FOLDERS LISTED VIA FALLBACK [{label}] (cmd dir /s /b /a-d) -----\n")
        for d in fallback_used:
            out.write(d + "\n")

    if skipped_dirs:
        out.write(f"\n----- FOLDERS SKIPPED [{label}] (could not be read even with fallback) -----\n")
        for d, err in skipped_dirs:
            out.write(f"{d}\t{err}\n")

    if skipped_items:
        out.write(f"\n----- INDIVIDUAL ITEMS WITH ERRORS [{label}] (path was still recorded) -----\n")
        for d, err in skipped_items:
            out.write(f"{d}\t{err}\n")

    elapsed = time.time() - started
    out.write(f"\n===== [{label}] finished: {time.strftime('%Y-%m-%d %H:%M:%S')} "
              f"({file_count:,} files, {folder_count:,} folders, {elapsed:.1f}s) =====\n")

    # per-root console summary
    print()
    print(f"  [{label}] done in {elapsed:.1f}s")
    print(f"    Files listed  : {file_count:,}")
    print(f"    Folders walked: {folder_count:,}")
    print(f"    Empty folders : {len(empty_dirs):,}")
    print(f"    Fallback used : {len(fallback_used):,}")
    print(f"    Skipped dirs  : {len(skipped_dirs):,}")
    print(f"    Skipped items : {len(skipped_items):,}")

    # update combined counters
    counters["files"]         += file_count
    counters["folders"]       += folder_count
    counters["empty"]         += len(empty_dirs)
    counters["fallback"]      += len(fallback_used)
    counters["skipped_dirs"]  += len(skipped_dirs)
    counters["skipped_items"] += len(skipped_items)
    counters["per_root"].append((label, root, file_count, folder_count, elapsed))


def main():
    mode = "a" if "--append" in sys.argv else "w"

    counters = {
        "files": 0, "folders": 0, "empty": 0,
        "fallback": 0, "skipped_dirs": 0, "skipped_items": 0,
        "per_root": [], "missing_roots": [],
    }

    started = time.time()
    with open(OUTPUT_FILE, mode, encoding="utf-8") as out:
        for label, root in ROOTS:
            walk_root(label, root, out, counters)

    elapsed = time.time() - started
    print()
    print("=" * 60)
    print(f"ALL ROOTS DONE in {elapsed:.1f}s.")
    print(f"  Roots walked  : {len(ROOTS) - len(counters['missing_roots'])} / {len(ROOTS)}")
    for label, root, fc, dc, el in counters["per_root"]:
        print(f"    [{label}] {root:<40}  {fc:>8,} files  {dc:>6,} folders  {el:6.0f}s")
    for label, root in counters["missing_roots"]:
        print(f"    [{label}] {root:<40}  NOT FOUND")
    print(f"  Total files   : {counters['files']:,}")
    print(f"  Total folders : {counters['folders']:,}")
    print(f"  Empty folders : {counters['empty']:,}")
    print(f"  Fallback used : {counters['fallback']:,}")
    print(f"  Skipped dirs  : {counters['skipped_dirs']:,}")
    print(f"  Skipped items : {counters['skipped_items']:,}")
    print(f"  Output        : {os.path.abspath(OUTPUT_FILE)}")

    if counters["skipped_dirs"]:
        print()
        print("Some folders could not be read even with the fallback.")
        print("Common reasons for the Windows error codes:")
        print("  * WinError 5    : Access denied - grant your user permission")
        print("                    (folder Properties > Security > Edit > Full control).")
        print("  * WinError 433  : Device not available - usually a OneDrive")
        print("                    'files on-demand' placeholder or a broken junction.")
        print("                    Fix: right-click the folder in Explorer >")
        print("                    'Always keep on this device', then re-run this script.")
        print("  * WinError 3    : Path not found - broken symlink / junction.")
        print("  * WinError 32   : File in use - close programs using that folder.")
        print("  * WinError 1392 : Corrupt directory - run  chkdsk <drive>: /f")
        print("                    from an ADMIN cmd, then re-run this script.")


if __name__ == "__main__":
    main()
