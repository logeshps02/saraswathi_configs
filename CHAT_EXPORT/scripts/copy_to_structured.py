r"""
copy_to_structured.py
=====================

Read the augmented Excel workbook (WITH PATHS (5).xlsx) and copy each
matched folder into a structured tree:

    E:\Structured_data\<COMPANY NAME>\<YEAR>\<original folder name>\...

For rows tagged MULTIPLE MATCHES ..., each candidate folder is copied.

USAGE
-----
1) Copy this .py AND the (5).xlsx to the PC that has E:\ and F:\ drives.
2) In cmd:
       py copy_to_structured.py                # DRY RUN - writes a plan
       py copy_to_structured.py --copy         # actually copy files
       py copy_to_structured.py --copy --limit 50   # copy only first 50 items
                                                     (good for a test)

The script:
* Uses robocopy under the hood - handles long paths, resumes safely, is very
  fast for the "nothing to do" case if you re-run it.
* Skips rows whose STATUS is NOT FOUND / SKIPPED / blank.
* Sanitises company names so they are valid Windows folder names.
* De-duplicates (source, destination) pairs so identical copies are only
  attempted once even if 20 Excel rows point at the same folder.
* Live progress every few items (percent, elapsed, ETA, throughput, and the
  current company/year being copied).
* Writes three files next to this script:
      Structured_data_copy_plan.txt      what will/would be copied
      Structured_data_copy_log.txt       one line per copy attempt
      Structured_data_copy_failures.txt  ONLY the failures - easy to review
* Can be safely interrupted with Ctrl+C - progress made so far is kept,
  and a partial summary is printed / written.
"""

import openpyxl
import os
import re
import sys
import time
import signal
import subprocess
from collections import defaultdict

# ---- settings you can change ----
WORKBOOK       = r"C:\Users\logsarav\Downloads\BACKUP WORK - FINAL SHEET - WITH PATHS (5).xlsx"
DEST_ROOT      = r"E:\Structured_data"
LOG_FILE       = "Structured_data_copy_log.txt"
FAILURES_FILE  = "Structured_data_copy_failures.txt"
PLAN_FILE      = "Structured_data_copy_plan.txt"
PROGRESS_EVERY = 10           # print a progress line every N items
# ----------------------------------

YEAR_RE = re.compile(r"^\d{4}-(\d{2}|\d{4})$")

INVALID_STATUS_PREFIXES = ("NOT FOUND", "NOT ON BACKUP", "SKIPPED")


# ---------------------------------------------------------------- helpers
def sanitize(name):
    """Make a string safe to use as a Windows folder name."""
    if name is None:
        return "(unknown)"
    s = str(name).strip()
    # replace illegal chars
    s = re.sub(r'[<>:"/\\|?*\r\n\t]', " ", s)
    # collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    # strip trailing dots/spaces (illegal at end of Windows names)
    s = s.rstrip(". ")
    # Windows max component length is 255 chars; keep some headroom
    if len(s) > 180:
        s = s[:180].rstrip(". ")
    return s or "(unknown)"


def canonical_year(y):
    m = re.match(r"^(\d{4})-(\d{2,4})$", str(y or "").strip())
    if not m:
        return None
    start, end = m.group(1), m.group(2)
    if len(end) == 4:
        return f"{start}-{end[-2:]}"
    return f"{start}-{end}"


def year_from_combine(combine):
    if not combine:
        return None
    parts = re.split(r"\s*>\s*", str(combine))
    for p in parts:
        y = canonical_year(p)
        if y:
            return y
    return None


def to_long(p):
    r"""Add \\?\ so long paths work with os.makedirs."""
    if os.name != "nt":
        return p
    p = os.path.abspath(p)
    if p.startswith("\\\\?\\"):
        return p
    if p.startswith("\\\\"):
        return "\\\\?\\UNC\\" + p[2:]
    return "\\\\?\\" + p


def run_robocopy(src, dst):
    """Return (ok, exit_code, stdout, stderr).
    robocopy exit codes 0..7 are all successes."""
    args = [
        "robocopy", src, dst,
        "/E", "/COPY:DAT", "/R:1", "/W:1",
        "/NP", "/NDL", "/NC", "/NS", "/NJH", "/NJS", "/XJ",
    ]
    try:
        r = subprocess.run(args, capture_output=True, text=True,
                           encoding="mbcs", errors="replace",
                           timeout=None)
        return (r.returncode < 8), r.returncode, r.stdout or "", r.stderr or ""
    except Exception as e:
        return False, -1, "", f"exception: {e}"


def fmt_time(seconds):
    seconds = int(max(0, seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m{s:02d}s"
    if m:
        return f"{m}m{s:02d}s"
    return f"{s}s"


# ---------------------------------------------------------------- workbook
def collect_pairs(wb):
    """Walk all sheets and return list of (source_folder, dest_folder) tuples,
    de-duplicated, along with a lookup back to Excel context for logging."""
    pairs = {}   # dict: (src_lower, dst_lower) -> (src, dst, context_row_desc)

    def status_ok(status):
        s = str(status or "")
        if not s.strip():
            return False
        return not any(s.startswith(p) for p in INVALID_STATUS_PREFIXES)

    def add(source_paths, company, year, ctx):
        if not source_paths or not company or not year:
            return
        clean_company = sanitize(company)
        year_norm = canonical_year(year)
        if not year_norm:
            return
        # destination structure:  <root>\<COMPANY>\<YEAR>\<original folder>
        for src in source_paths:
            src = src.strip()
            if not src:
                continue
            base = os.path.basename(src.rstrip("\\"))
            dst = os.path.join(DEST_ROOT, clean_company, year_norm, base)
            key = (src.lower(), dst.lower())
            if key in pairs:
                continue
            pairs[key] = (src, dst, ctx)

    # ---- Sheet 1: UPLOADED FORMS - COMPANY NAME
    ws = wb["UPLOADED FORMS - COMPANY NAME"]
    status_col = ws.max_column
    path_col   = status_col - 1
    print(f"  scanning 'UPLOADED FORMS - COMPANY NAME' ({ws.max_row-1:,} rows) ...", flush=True)
    for r in range(2, ws.max_row + 1):
        status = ws.cell(row=r, column=status_col).value
        if not status_ok(status):
            continue
        matched = ws.cell(row=r, column=path_col).value or ""
        matched = str(matched)
        if not matched:
            continue
        company = ws.cell(row=r, column=2).value
        year    = ws.cell(row=r, column=3).value
        add([p for p in matched.split(" ; ") if p.strip()],
            company, year,
            f"UPLOADED r{r}")

    # ---- Sheet 2: COMPANY WISE
    ws = wb["COMPANY WISE"]
    status_col = ws.max_column
    path_col   = status_col - 1
    current_company = None
    print(f"  scanning 'COMPANY WISE' ({ws.max_row-1:,} rows) ...", flush=True)
    for r in range(2, ws.max_row + 1):
        c = ws.cell(row=r, column=2).value
        if c:
            current_company = c
        status = ws.cell(row=r, column=status_col).value
        if not status_ok(status):
            continue
        matched = ws.cell(row=r, column=path_col).value or ""
        matched = str(matched)
        if not matched:
            continue
        combine = ws.cell(row=r, column=3).value
        year = year_from_combine(combine)
        add([p for p in matched.split(" ; ") if p.strip()],
            current_company, year,
            f"COMPANY WISE r{r}")

    # ---- Sheet 3: DIN FORMS
    if "DIN FORMS" in wb.sheetnames:
        ws = wb["DIN FORMS"]
        status_col = ws.max_column
        path_col   = status_col - 1
        print(f"  scanning 'DIN FORMS' ({ws.max_row-2:,} rows) ...", flush=True)
        for r in range(3, ws.max_row + 1):
            status = ws.cell(row=r, column=status_col).value
            if not status_ok(status):
                continue
            matched = ws.cell(row=r, column=path_col).value or ""
            matched = str(matched)
            if not matched:
                continue
            name = ws.cell(row=r, column=2).value
            combine = ws.cell(row=r, column=3).value
            year = year_from_combine(combine)
            add([p for p in matched.split(" ; ") if p.strip()],
                name, year, f"DIN r{r}")

    # ---- Sheet 4: LEI AND OTHERS
    if "LEI AND OTHERS" in wb.sheetnames:
        ws = wb["LEI AND OTHERS"]
        status_col = ws.max_column
        path_col   = status_col - 1
        print(f"  scanning 'LEI AND OTHERS' ({ws.max_row-1:,} rows) ...", flush=True)
        for r in range(2, ws.max_row + 1):
            status = ws.cell(row=r, column=status_col).value
            if not status_ok(status):
                continue
            matched = ws.cell(row=r, column=path_col).value or ""
            matched = str(matched)
            if not matched:
                continue
            name = ws.cell(row=r, column=2).value
            combine = ws.cell(row=r, column=3).value
            year = year_from_combine(combine)
            add([p for p in matched.split(" ; ") if p.strip()],
                name, year, f"LEI r{r}")

    return list(pairs.values())


# ---------------------------------------------------------------- main
def main():
    do_copy = "--copy" in sys.argv
    limit = None
    if "--limit" in sys.argv:
        i = sys.argv.index("--limit")
        try:
            limit = int(sys.argv[i + 1])
        except (IndexError, ValueError):
            print("--limit requires an integer, e.g.  --limit 50")
            return

    if not os.path.isfile(WORKBOOK):
        print(f"ERROR: workbook not found: {WORKBOOK}")
        print("Edit the WORKBOOK path at the top of this script.")
        return

    print(f"Loading workbook ...  {WORKBOOK}")
    # NOTE: openpyxl's read_only mode is much slower than the default when we do
    # random cell access with ws.cell(row=r, column=c).value.  Use the default
    # mode - the workbook is small (< 1 MB) so RAM is a non-issue.
    wb = openpyxl.load_workbook(WORKBOOK, data_only=True)

    print("Collecting (source -> destination) pairs ...")
    pairs = collect_pairs(wb)
    print(f"  {len(pairs):,} unique copies to perform")

    if limit is not None:
        pairs = pairs[:limit]
        print(f"  --limit applied: only {len(pairs):,} will be processed")

    # Group by destination company\year folder for a nicer plan output
    grouped = defaultdict(list)
    for src, dst, ctx in pairs:
        cy_folder = os.path.dirname(dst)   # <root>\<COMPANY>\<YEAR>
        grouped[cy_folder].append((src, dst, ctx))

    # Write the plan file (always)
    plan_path = os.path.join(os.path.dirname(os.path.abspath(__file__)) or ".", PLAN_FILE)
    with open(plan_path, "w", encoding="utf-8") as f:
        f.write(f"COPY PLAN generated {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Workbook: {WORKBOOK}\n")
        f.write(f"Destination root: {DEST_ROOT}\n")
        f.write(f"Total unique copies: {len(pairs):,}\n")
        f.write(f"Total destination company/year folders: {len(grouped):,}\n\n")
        for cy_folder in sorted(grouped.keys()):
            f.write(f"[{cy_folder}]\n")
            for src, dst, ctx in grouped[cy_folder]:
                f.write(f"    {ctx}\n")
                f.write(f"      SRC: {src}\n")
                f.write(f"      DST: {dst}\n")
            f.write("\n")
    print(f"Plan written to: {plan_path}")

    if not do_copy:
        print()
        print("DRY RUN (no files copied).")
        print("Review the plan above, then run with  --copy  to actually copy.")
        return

    # ---------------- actual copy ----------------
    script_dir = os.path.dirname(os.path.abspath(__file__)) or "."
    log_path       = os.path.join(script_dir, LOG_FILE)
    failures_path  = os.path.join(script_dir, FAILURES_FILE)

    ok_count      = 0
    fail_count    = 0
    missing_src   = 0
    started       = time.time()
    last_progress = started

    interrupted = {"flag": False}

    def _sigint(_sig, _frame):
        interrupted["flag"] = True
        print("\n  !! Ctrl+C received - finishing current item then stopping ...")

    try:
        signal.signal(signal.SIGINT, _sigint)
    except Exception:
        pass

    log      = open(log_path,      "w", encoding="utf-8")
    failures = open(failures_path, "w", encoding="utf-8")
    log.write(f"COPY LOG {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    failures.write(f"FAILURES / MISSING SOURCES  {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    failures.write(f"(re-check paths that show up here after the run)\n\n")

    try:
        for idx, (src, dst, ctx) in enumerate(pairs, 1):
            if interrupted["flag"]:
                break

            # "current item" line, always printed - overwrites itself
            cur_label = os.path.relpath(dst, DEST_ROOT)
            print(f"  [{idx}/{len(pairs)}] {cur_label[:110]}", flush=True)

            if not os.path.isdir(src):
                missing_src += 1
                failures.write(f"[MISSING SRC]  {ctx}\n    {src}\n\n")
                failures.flush()
                log.write(f"[{idx}] MISSING_SRC  {ctx}\n     {src}\n")
                continue

            try:
                os.makedirs(to_long(os.path.dirname(dst)), exist_ok=True)
            except Exception as e:
                fail_count += 1
                failures.write(f"[MKDIR FAIL]  {ctx}\n    dst: {dst}\n    err: {e}\n\n")
                failures.flush()
                log.write(f"[{idx}] MKDIR_FAIL  {ctx}  err={e}\n")
                continue

            ok, rc, out, err = run_robocopy(src, dst)
            if ok:
                ok_count += 1
                log.write(f"[{idx}] OK   rc={rc}  {ctx}\n     {src}\n  -> {dst}\n")
            else:
                fail_count += 1
                # keep only last few lines of robocopy output to keep it readable
                tail = "\n".join(
                    ln for ln in (out + "\n" + err).splitlines()[-8:]
                    if ln.strip()
                )
                failures.write(
                    f"[ROBOCOPY FAIL rc={rc}]  {ctx}\n"
                    f"    SRC: {src}\n"
                    f"    DST: {dst}\n"
                    f"    {tail}\n\n"
                )
                failures.flush()
                log.write(f"[{idx}] FAIL rc={rc}  {ctx}\n     {src}\n  -> {dst}\n")

            # detailed progress line every PROGRESS_EVERY items or every 5 seconds
            now = time.time()
            if idx % PROGRESS_EVERY == 0 or (now - last_progress) >= 5.0 \
                    or idx == len(pairs):
                elapsed = now - started
                rate    = idx / elapsed if elapsed > 0 else 0
                remaining = (len(pairs) - idx) / rate if rate > 0 else 0
                pct = idx * 100.0 / len(pairs)
                print(
                    f"  progress: {idx}/{len(pairs)} ({pct:5.1f}%)  "
                    f"ok={ok_count} fail={fail_count} missing={missing_src}  "
                    f"{rate:5.1f} items/s  elapsed={fmt_time(elapsed)}  "
                    f"eta={fmt_time(remaining)}",
                    flush=True,
                )
                last_progress = now

    finally:
        log.close()
        failures.close()

    elapsed = time.time() - started
    print()
    print("=" * 60)
    if interrupted["flag"]:
        print("STOPPED EARLY (Ctrl+C).  Progress so far:")
    else:
        print(f"Done in {fmt_time(elapsed)}.")
    processed = ok_count + fail_count + missing_src
    print(f"  copies attempted : {processed:,} / {len(pairs):,}")
    print(f"  succeeded        : {ok_count:,}")
    print(f"  failed           : {fail_count:,}")
    print(f"  source missing   : {missing_src:,}")
    print(f"  full log         : {log_path}")
    if fail_count or missing_src:
        print(f"  failure details  : {failures_path}  <-- open this to see what needs attention")
    else:
        print("  no failures - failures file is empty.")


if __name__ == "__main__":
    main()
