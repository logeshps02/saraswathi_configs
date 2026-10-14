r"""
recheck_missed.py
=================

Retry every folder that was reported under

    ----- FOLDERS SKIPPED (could not be read even with fallback) -----

in an existing all_files_list.txt, and APPEND any files that are recovered
to the SAME txt.

Why this exists
---------------
When list_files.py runs against an external / USB drive, the drive can
briefly stop responding while scandir is enumerating the root, which makes
Windows return WinError 3 ("system cannot find the path") for folders that
actually exist. Simply retrying after a small pause almost always succeeds.

Strategy per failed folder
--------------------------
1. Sleep briefly, then try a Python recursive walk (os.scandir + \\?\ prefix).
2. If that still fails, try   cmd /c dir /s /b /a-d "<folder>".
3. If that also fails, try   robocopy "<folder>" NUL_DEST /L /E /FP ...
   which uses different Win32 APIs and is very tolerant of external-drive
   hiccups.

All results are appended to the same txt under a clearly-labelled RECHECK
section so you can see what was recovered. A final "STILL SKIPPED" list at
the bottom names anything that failed even after all three strategies.

Usage
-----
    python recheck_missed.py
    python recheck_missed.py "C:\Users\logsarav\Downloads\all_files_list (1).txt"
"""

import os
import re
import sys
import time
import subprocess

# ---- settings ----
DEFAULT_LIST     = r"C:\Users\logsarav\Downloads\all_files_list (1).txt"
MAX_ATTEMPTS     = 4         # scandir retries per folder (soft errors only)
INITIAL_SLEEP    = 2.0       # first sleep between attempts; doubles each retry
PROGRESS_EVERY   = 500
FLUSH_EVERY      = 2000
ROBOCOPY_TIMEOUT = 1800
DIR_TIMEOUT      = 1800

# WinError codes that mean the folder is genuinely corrupt / broken on disk.
# Retrying these just re-triggers the Windows "scan and fix drive" toast.
# 1392 - the file or directory is corrupted and unreadable
#   23 - data error (cyclic redundancy check)
#   22 - the device does not recognize the command
#   87 - invalid parameter
#   50 - request not supported
# 1393 - disk structure is corrupted
HARD_WIN_ERRORS = {1392, 23, 22, 87, 50, 1393}
# ------------------


# ---------------------------------------------------------------- helpers
def to_long(p):
    if os.name != "nt":
        return p
    p = os.path.abspath(p)
    if p.startswith("\\\\?\\"):
        return p
    if p.startswith("\\\\"):
        return "\\\\?\\UNC\\" + p[2:]
    return "\\\\?\\" + p


def strip_long(p):
    if p.startswith("\\\\?\\UNC\\"):
        return "\\\\" + p[len("\\\\?\\UNC\\"):]
    if p.startswith("\\\\?\\"):
        return p[len("\\\\?\\"):]
    return p


def scandir_walk(root):
    r"""Recursive walk of root using os.scandir + \\?\ prefix.
    Yields file paths.  Raises OSError if the root itself cannot be opened."""
    long_root = to_long(root)
    # sanity check first - let the caller catch OSError
    with os.scandir(long_root) as _:
        pass

    stack = [long_root]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                entries = list(it)
        except OSError:
            continue
        for entry in entries:
            try:
                if entry.is_dir(follow_symlinks=False):
                    stack.append(entry.path)
                else:
                    yield strip_long(entry.path)
            except OSError:
                # record whatever path we know
                try:
                    yield strip_long(entry.path)
                except Exception:
                    pass


def cmd_dir_listing(folder):
    """`cmd /c dir /s /b /a-d "<folder>"` - returns list of file paths (may be empty)."""
    try:
        r = subprocess.run(
            ["cmd", "/c", "dir", "/s", "/b", "/a-d", folder],
            capture_output=True, text=True,
            encoding="mbcs", errors="replace",
            timeout=DIR_TIMEOUT,
        )
        return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    except Exception as e:
        print(f"     cmd dir failed: {e}")
        return []


def robocopy_listing(folder):
    """`robocopy "<folder>" NUL_DEST /L /E /FP ...` - returns list of file paths."""
    try:
        # /L    list only (dry run)
        # /E    include all subdirs (even empty)
        # /FP   full path in output
        # /NDL  no dir list
        # /NC   no class column
        # /NS   no size column
        # /NP   no progress
        # /NJH /NJS  no header/summary
        # /BYTES  keeps sizes as bytes (not used because /NS drops the column)
        # /R:2 /W:1  2 retries, 1s wait  (avoid default 1_000_000 x 30s)
        r = subprocess.run(
            ["robocopy", folder, r"C:\__nul_dst_recheck__",
             "/L", "/E", "/FP", "/NDL", "/NC", "/NS",
             "/NP", "/NJH", "/NJS", "/R:2", "/W:1"],
            capture_output=True, text=True,
            encoding="mbcs", errors="replace",
            timeout=ROBOCOPY_TIMEOUT,
        )
        # robocopy line format after /L: "    New File  <path>"
        paths = []
        for ln in r.stdout.splitlines():
            s = ln.strip()
            if not s:
                continue
            # keep only lines that look like an absolute Windows path
            m = re.search(r"([A-Za-z]:\\.*|\\\\[^\s].*)$", s)
            if m:
                paths.append(m.group(1))
        return paths
    except Exception as e:
        print(f"     robocopy failed: {e}")
        return []


# ---------------------------------------------------------------- parse existing txt
SECTION_HEADERS = (
    "----- EMPTY DIRECTORIES -----",
    "----- FOLDERS LISTED VIA FALLBACK",
    "----- FOLDERS SKIPPED",
    "----- INDIVIDUAL ITEMS WITH ERRORS",
    "----- RECHECK",
    "----- STILL SKIPPED AFTER RECHECK",
)


def parse_skipped_folders(txt_path):
    """Return list of (folder, error_str) pulled from every
    '----- FOLDERS SKIPPED ...' block in the txt."""
    skipped = []
    section = None
    with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("-----") or line.startswith("====="):
                if line.startswith("----- FOLDERS SKIPPED") or line.startswith("----- STILL SKIPPED"):
                    section = "skipped"
                else:
                    section = None
                continue
            if section == "skipped" and line.strip():
                parts = line.split("\t", 1)
                path = parts[0].strip()
                err  = parts[1].strip() if len(parts) > 1 else ""
                if path:
                    skipped.append((path, err))
    # dedup preserving order
    seen, out = set(), []
    for p, e in skipped:
        if p not in seen:
            seen.add(p)
            out.append((p, e))
    return out


def load_existing_paths(txt_path):
    """Return the set of file paths already present in the txt (so re-runs
    don't add duplicates)."""
    existing = set()
    section_ok = True
    with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.rstrip("\n")
            if s.startswith("-----") or s.startswith("====="):
                # anything after a section header may be metadata, treat with care
                section_ok = not s.startswith("----- FOLDERS SKIPPED") \
                             and not s.startswith("----- INDIVIDUAL ITEMS") \
                             and not s.startswith("----- STILL SKIPPED")
                continue
            if section_ok and s.strip():
                existing.add(s.strip())
    return existing


# ---------------------------------------------------------------- main
def _err_is_hard(err_text):
    """Return True if the error text mentions a WinError we should not retry."""
    m = re.search(r"WinError\s+(\d+)", err_text or "")
    if not m:
        return False
    return int(m.group(1)) in HARD_WIN_ERRORS


def main():
    txt_path = None
    skip_hard = False
    for arg in sys.argv[1:]:
        if arg == "--skip-hard":
            skip_hard = True
        elif not arg.startswith("--"):
            txt_path = arg
    if txt_path is None:
        txt_path = DEFAULT_LIST
    if not os.path.isfile(txt_path):
        print(f"ERROR: txt file not found: {txt_path}")
        return

    print(f"Reading: {txt_path}")
    skipped = parse_skipped_folders(txt_path)
    print(f"  {len(skipped)} skipped folder(s) to retry")

    print("Loading existing paths (for dedup) ...")
    existing = load_existing_paths(txt_path)
    print(f"  {len(existing):,} paths already in file")

    if not skipped:
        print("Nothing to retry.  Done.")
        return

    recovered = 0
    per_folder_recovered = []   # (folder, count, method)
    still_failed = []           # (folder, error)

    started    = time.time()
    next_flush = FLUSH_EVERY

    with open(txt_path, "a", encoding="utf-8") as out:
        out.write(f"\n----- RECHECK PASS - {time.strftime('%Y-%m-%d %H:%M:%S')} -----\n")
        out.flush()

        for idx, (folder, orig_err) in enumerate(skipped, 1):
            print(f"[{idx}/{len(skipped)}] retrying: {folder}")
            print(f"     original error: {orig_err}")

            hard = _err_is_hard(orig_err)
            if hard:
                print("     >>> hard error (corruption/CRC) - one attempt only, "
                      "no aggressive retry")
                if skip_hard:
                    print("     --skip-hard set: skipping entirely")
                    still_failed.append((folder, orig_err + "  [skipped: --skip-hard]"))
                    continue

            attempts_allowed = 1 if hard else MAX_ATTEMPTS
            paths_found = []
            method = None

            # ---- 1) os.scandir with retries (soft) or single attempt (hard)
            sleep_s = INITIAL_SLEEP
            for attempt in range(1, attempts_allowed + 1):
                try:
                    paths_found = list(scandir_walk(folder))
                    if paths_found:
                        method = f"scandir (attempt {attempt})"
                        break
                    if attempt == attempts_allowed:
                        method = f"scandir (empty, attempt {attempt})"
                    else:
                        time.sleep(sleep_s)
                        sleep_s *= 2       # 2s -> 4s -> 8s -> 16s ...
                except OSError as e:
                    winerr = getattr(e, "winerror", None)
                    print(f"     attempt {attempt} scandir: WinError {winerr}"
                          f" - {e.strerror or e}")
                    if winerr in HARD_WIN_ERRORS:
                        # hard mid-walk error - stop retrying scandir
                        print("     hard error hit mid-walk - skipping further scandir retries")
                        break
                    if attempt < attempts_allowed:
                        time.sleep(sleep_s)
                        sleep_s *= 2

            # ---- 2) cmd /c dir /s /b /a-d (skip for hard errors - they will just re-fire the toast)
            if not paths_found and not hard:
                print("     trying cmd dir fallback ...")
                paths_found = cmd_dir_listing(folder)
                if paths_found:
                    method = "cmd dir"

            # ---- 3) robocopy /L /E /FP (skip for hard errors)
            if not paths_found and not hard:
                print("     trying robocopy fallback ...")
                paths_found = robocopy_listing(folder)
                if paths_found:
                    method = "robocopy"

            if not paths_found:
                still_failed.append((folder, orig_err))
                print(f"     STILL FAILED: {folder}")
                continue

            # write only new paths
            new_paths = 0
            for p in paths_found:
                if p in existing:
                    continue
                existing.add(p)
                out.write(p + "\n")
                new_paths += 1
                recovered += 1

                if recovered >= next_flush:
                    out.flush()
                    next_flush += FLUSH_EVERY

            per_folder_recovered.append((folder, new_paths, method))
            print(f"     recovered {new_paths:,} new files via {method}")

        # -------------------------- appendices
        if per_folder_recovered:
            out.write("\n----- RECHECK RECOVERY SUMMARY -----\n")
            for folder, n, m in per_folder_recovered:
                out.write(f"{folder}\t{n} new files\tvia {m}\n")

        if still_failed:
            out.write("\n----- STILL SKIPPED AFTER RECHECK -----\n")
            for folder, err in still_failed:
                out.write(f"{folder}\t{err}\n")

        out.write(f"\n----- RECHECK FINISHED - {time.strftime('%Y-%m-%d %H:%M:%S')} -----\n")

    elapsed = time.time() - started
    print()
    print(f"Recheck done in {elapsed:.1f}s.")
    print(f"  Folders retried    : {len(skipped)}")
    print(f"  New files added    : {recovered:,}")
    print(f"  Folders still fail : {len(still_failed)}")
    print(f"  Output (appended)  : {os.path.abspath(txt_path)}")

    if still_failed:
        print()
        print("Folders that still failed even after retries + cmd dir + robocopy:")
        for folder, err in still_failed:
            print(f"  {folder}")
        print()
        print("Tips for these:")
        print("  * If Windows kept showing 'Scan and fix drive' notifications,")
        print("    the drive really does have corrupt entries.  In an ADMIN cmd:")
        print("       chkdsk E: /f            (repair filesystem metadata)")
        print("       chkdsk E: /f /r         (also finds and remaps bad sectors)")
        print("    then re-run this recheck script.")
        print("  * Unplug and replug the drive, use a USB 3.0 port directly on")
        print("    the machine (not a hub), and avoid running other heavy I/O")
        print("    on the same drive while the script is walking.")
        print("  * Re-run with  --skip-hard  to skip the corrupt folders")
        print("    entirely (no more 'scan the drive' toasts):")
        print("       python recheck_missed.py --skip-hard")


if __name__ == "__main__":
    main()
