"""Backtrace each client-nil dest to Final (12), every split path, SAFE map, latest copy log."""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"c:\Users\U.lalitha navya sri\Downloads\Logesh files")
OUT = ROOT / "05-migration" / "NIL_BACKTRACE_COPY_STATUS.txt"


def split_paths(cell: str) -> list[str]:
    if not cell:
        return []
    return [p.strip().strip('"') for p in re.split(r"\s*;\s*", cell) if p.strip()]


def norm(p: str) -> str:
    return (p or "").strip().strip('"').replace("/", "\\").rstrip("\\").upper()


def load_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def find_one(glob: str) -> Path:
    hits = list(ROOT.glob(glob))
    if not hits:
        raise SystemExit(f"missing {glob}")
    return hits[0]


def main() -> None:
    nils = []
    with (ROOT / "UPDATED COMPANY_FOLDERS_IN_FINAL_csv.csv").open(
        encoding="utf-8-sig", newline=""
    ) as f:
        for r in csv.DictReader(f):
            if (r.get("company it shold be") or "").strip().lower() == "nil":
                nils.append(
                    (
                        (r.get("sno") or "").strip(),
                        (r.get("company_folder_in_Final") or "").strip(),
                    )
                )

    cw_csv = find_one("**/BACKUP WORK - FINAL SHEET - WITH PATHS (12)-COMPANY WISE.csv")
    uf_csv = find_one(
        "**/BACKUP WORK - FINAL SHEET - WITH PATHS (12)-UPLOADED FORMS - COMPANY NAME.csv"
    )
    lei_csv = find_one("**/BACKUP WORK - FINAL SHEET - WITH PATHS (12)-LEI AND OTHERS.csv")
    safe_csv = ROOT / "05-migration" / "STRUCTURED_COPY_MAP_SAFE.csv"
    log_csv = ROOT / "_COPY_LOG.csv"
    miss_csv = ROOT / "_COPY_MISSING.csv"

    cw = load_rows(cw_csv)
    uf = load_rows(uf_csv)
    lei = load_rows(lei_csv)
    safe = load_rows(safe_csv)

    log_by_src: dict[str, list[dict]] = defaultdict(list)
    with log_csv.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            log_by_src[norm(r.get("source_path") or "")].append(r)

    missing_srcs = set()
    with miss_csv.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            missing_srcs.add(norm(r.get("source_path") or ""))

    safe_by_src: dict[str, list[dict]] = defaultdict(list)
    for r in safe:
        safe_by_src[norm(r.get("source_path") or "")].append(r)

    def needle_variants(name: str) -> list[str]:
        n = name.upper()
        out = [n]
        if n == "CFSS - NEOMAX":
            out.append("CFSS  - NEOMAX")
        if "MAHARAJA SIR CLIENTS" in n:
            out.append("MAHARAJA SIR CLIENTS DIR-3 KYC AND WEB KY")
            out.append("MAHARAJA SIR CLIENTS DIR-3 KYC AND WEB KYC")
        return list(dict.fromkeys(out))

    def row_text(r: dict) -> str:
        return " | ".join((v or "") for v in r.values()).upper()

    def match_name(hay: str, name: str) -> bool:
        hay_u = (hay or "").upper()
        for v in needle_variants(name):
            if v in hay_u:
                return True
        return False

    lines: list[str] = []
    w = lines.append
    w("NIL BACKTRACE vs FINAL (12) + SAFE + LATEST _COPY_LOG.csv")
    w(f"nils={len(nils)}  safe={len(safe)}  copy_log={sum(len(v) for v in log_by_src.values())}  missing={len(missing_srcs)}")
    w("")

    summary_rows = []

    for sno, name in nils:
        w("=" * 88)
        w(f"NIL sno={sno}  dest_name={name}")
        w("=" * 88)

        uf_hits = []
        for i, r in enumerate(uf, start=2):
            company = (r.get("COMPANY NAME") or "").strip()
            if match_name(company, name) and company.upper().replace("  ", " ").startswith(
                name.upper()[:12]
            ) or company.upper().replace("  ", " ") == name.upper().replace("  ", " ") or company.upper() in {
                v.upper() for v in needle_variants(name)
            }:
                uf_hits.append((i, r))

        # tighter UF match: company cell equals a variant (not substring of other companies)
        uf_hits = []
        variants = {v.upper().replace("  ", " ") for v in needle_variants(name)}
        variants.add(name.upper().replace("  ", " "))
        for i, r in enumerate(uf, start=2):
            company = re.sub(r"\s+", " ", (r.get("COMPANY NAME") or "").strip().upper())
            if company in variants or company.replace(" - ", "-") in {
                v.replace(" - ", "-") for v in variants
            }:
                uf_hits.append((i, r))

        lei_hits = []
        for i, r in enumerate(lei, start=2):
            nm = re.sub(r"\s+", " ", (r.get("NAME") or "").strip().upper())
            if nm in variants or nm.replace(" - ", "-") in {v.replace(" - ", "-") for v in variants}:
                lei_hits.append((i, r))

        cw_hits = []
        for i, r in enumerate(cw, start=2):
            company = (r.get("COMPANY NAME") or "").strip()
            combine = (r.get("COMBINE") or "").strip()
            path = (r.get("MATCHED PATH") or "").strip()
            if match_name(company, name) and company:
                # only if company cell itself is the pile name
                cu = re.sub(r"\s+", " ", company.upper())
                if cu in variants:
                    cw_hits.append((i, r, "company_cell"))
                    continue
            if match_name(combine, name) or match_name(path, name):
                # context mention: keep if combine suffix or path contains pile
                cw_hits.append((i, r, "combine_or_path"))

        w(f"  UF exact company-cell hits: {len(uf_hits)}")
        master_paths: list[tuple[str, str, int, str, str]] = []
        # origin, path, excel_row, status, sheet

        for i, r in uf_hits:
            status = (r.get("STATUS") or "").strip()
            combine = (r.get("COMBINE") or "").strip()
            paths = split_paths(r.get("MATCHED PATH") or "")
            w(f"    UF excel_row={i} company={r.get('COMPANY NAME')!r} combine={combine!r} status={status!r} n_paths={len(paths)}")
            if not paths:
                w("      PATH=<empty>")
                master_paths.append(("UF", "", i, status, "UPLOADED FORMS - COMPANY NAME"))
            for p in paths:
                w(f"      PATH={p}")
                master_paths.append(("UF", p, i, status, "UPLOADED FORMS - COMPANY NAME"))

        w(f"  LEI exact name-cell hits: {len(lei_hits)}")
        for i, r in lei_hits:
            status = (r.get("STATUS") or "").strip()
            folder = (r.get("FOLDER") or "").strip()
            paths = split_paths(r.get("MATCHED PATH") or "")
            w(f"    LEI excel_row={i} name={r.get('NAME')!r} folder={folder!r} status={status!r} n_paths={len(paths)}")
            for p in paths:
                w(f"      PATH={p}")
                master_paths.append(("LEI", p, i, status, "LEI AND OTHERS"))

        # COMPANY WISE: split company-cell vs context
        cw_company = [x for x in cw_hits if x[2] == "company_cell"]
        cw_ctx = [x for x in cw_hits if x[2] == "combine_or_path"]
        w(f"  COMPANY WISE company-cell hits: {len(cw_company)}  combine/path context hits: {len(cw_ctx)}")
        for i, r, kind in cw_company:
            status = (r.get("STATUS") or "").strip()
            paths = split_paths(r.get("MATCHED PATH") or "")
            w(f"    CW excel_row={i} company={r.get('COMPANY NAME')!r} combine={r.get('COMBINE')!r} status={status!r} n_paths={len(paths)}")
            if not paths:
                master_paths.append(("CW", "", i, status, "COMPANY WISE"))
            for p in paths:
                w(f"      PATH={p}")
                master_paths.append(("CW", p, i, status, "COMPANY WISE"))

        # context children: unique companies that mention this pile
        ctx_companies = []
        seen_co = set()
        last_co = ""
        # walk CW with carry-forward company
        carried = ""
        ctx_detail = []
        for i, r in enumerate(cw, start=2):
            co = (r.get("COMPANY NAME") or "").strip()
            if co:
                carried = co
            combine = (r.get("COMBINE") or "").strip()
            path = (r.get("MATCHED PATH") or "").strip()
            if match_name(combine, name) or match_name(path, name):
                ctx_detail.append((i, carried, combine, r.get("STATUS") or "", split_paths(path)))
                if carried and carried.upper() not in seen_co:
                    seen_co.add(carried.upper())
                    ctx_companies.append(carried)

        w(f"  COMPANY WISE context rows (combine/path mention pile): {len(ctx_detail)} unique companies={len(ctx_companies)}")
        for co in ctx_companies:
            w(f"    context_company={co}")

        # SAFE rows whose source is under any master path OR dest is this unsorted OR company_col is this name
        name_key = name.upper().replace("  ", " ")
        related_safe = []
        for r in safe:
            src = r.get("source_path") or ""
            dest = r.get("dest_relative") or ""
            dest_co = r.get("dest_company") or ""
            old = r.get("old_dest_company") or ""
            company_col = r.get("company") or ""
            if name_key in dest_co.upper() or name_key in old.upper() or name_key in company_col.upper():
                related_safe.append(("name_match", r))
                continue
            nsrc = norm(src)
            for origin, p, excel_row, status, sheet in master_paths:
                if not p:
                    continue
                np = norm(p)
                if nsrc == np or nsrc.startswith(np + "\\"):
                    related_safe.append((f"under_master:{sheet}:{excel_row}", r))
                    break

        # unique by dest+source
        uniq = {}
        for tag, r in related_safe:
            k = (r.get("source_path"), r.get("dest_relative"))
            if k not in uniq:
                uniq[k] = (tag, r)
        related_safe = list(uniq.values())

        w(f"  SAFE related rows: {len(related_safe)}")

        path_status = []
        # check every master path
        w("  -- MASTER PATH CHECK --")
        seen_p = set()
        for origin, p, excel_row, status, sheet in master_paths:
            key = (origin, norm(p), excel_row)
            if key in seen_p:
                continue
            seen_p.add(key)
            np = norm(p)
            safe_hits = safe_by_src.get(np, [])
            # also children mapped separately
            child_hits = []
            if np:
                for srcn, rows in safe_by_src.items():
                    if srcn != np and srcn.startswith(np + "\\"):
                        child_hits.extend(rows)
            log_hits = log_by_src.get(np, [])
            in_missing = np in missing_srcs if np else False
            avail = "EMPTY_MASTER_PATH" if not p else (
                "MISSING_IN_COPY" if in_missing else (
                    "COPIED" if log_hits else (
                        "MAPPED_NOT_IN_LOG" if safe_hits else "NOT_IN_SAFE"
                    )
                )
            )
            # if parent not copied but children are, mark
            child_copied = 0
            child_ok = 0
            for ch in child_hits:
                chsrc = norm(ch.get("source_path") or "")
                chlog = log_by_src.get(chsrc, [])
                if chlog:
                    child_copied += 1
                    notes = " ".join((x.get("rc_or_note") or "") for x in chlog)
                    if notes.startswith("ok") or "robocopy:0" in notes or "robocopy:1" in notes or "robocopy:2" in notes or "robocopy:3" in notes:
                        child_ok += 1
            w(f"    [{origin} row {excel_row} status={status!r}] {p or '<empty>'}")
            w(f"      result={avail}  safe_exact={len(safe_hits)}  child_safe={len(child_hits)}  log_exact={len(log_hits)}  child_copied={child_copied}")
            for sh in safe_hits:
                w(
                    f"      SAFE dest={sh.get('dest_relative')} action={sh.get('remap_action')} origin={sh.get('origin')} kind={sh.get('review_kind')} sheet={sh.get('source_sheet')} excel={sh.get('excel_row')} review={sh.get('review_row')}"
                )
            for lh in log_hits:
                w(f"      LOG dest={lh.get('dest_relative')} note={lh.get('rc_or_note')} sec={lh.get('seconds')}")
            path_status.append((p, avail, len(safe_hits), len(child_hits), len(log_hits), child_copied))

        w("  -- ALL RELATED SAFE ROWS vs COPY LOG --")
        n_ok = n_miss = n_nolog = 0
        for tag, r in related_safe:
            src = r.get("source_path") or ""
            dest = r.get("dest_relative") or ""
            action = r.get("remap_action") or ""
            nsrc = norm(src)
            logs = log_by_src.get(nsrc, [])
            # dest-specific
            dest_logs = [x for x in logs if norm(x.get("dest_relative") or "") == norm(dest)]
            if not dest_logs:
                dest_logs = logs
            in_miss = nsrc in missing_srcs
            if in_miss:
                state = "MISSING"
                n_miss += 1
            elif dest_logs:
                notes = " | ".join((x.get("rc_or_note") or "") for x in dest_logs)
                state = f"IN_LOG:{notes}"
                n_ok += 1
            else:
                state = "NOT_IN_LOG"
                n_nolog += 1
            w(
                f"    {state} action={action} origin={r.get('origin')} sheet={r.get('source_sheet')} excel={r.get('excel_row')} review={r.get('review_row')}"
            )
            w(f"      SRC  {src}")
            w(f"      DEST {dest}")

        summary_rows.append(
            {
                "sno": sno,
                "name": name,
                "uf": len(uf_hits),
                "lei": len(lei_hits),
                "cw_company": len(cw_company),
                "cw_ctx_rows": len(ctx_detail),
                "cw_ctx_companies": len(ctx_companies),
                "master_paths": len(seen_p),
                "related_safe": len(related_safe),
                "related_in_log": n_ok,
                "related_missing": n_miss,
                "related_nolog": n_nolog,
                "ctx_companies": "; ".join(ctx_companies),
            }
        )
        w("")

    w("=" * 88)
    w("SUMMARY")
    w("=" * 88)
    for s in summary_rows:
        w(
            f"{s['sno']:>4} {s['name']}"
            f" | UF={s['uf']} LEI={s['lei']} CW_cell={s['cw_company']}"
            f" CW_ctx_rows={s['cw_ctx_rows']} CW_ctx_cos={s['cw_ctx_companies']}"
            f" master_paths={s['master_paths']} safe={s['related_safe']}"
            f" log_ok={s['related_in_log']} missing={s['related_missing']} nolog={s['related_nolog']}"
        )
        if s["ctx_companies"]:
            w(f"      ctx: {s['ctx_companies']}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} lines={len(lines)}")
    print("\n".join(lines[-40:]))


if __name__ == "__main__":
    main()
