"""End-to-end verification of STRUCTURED_COPY_MAP_SAFE.csv vs used map + staff aliases.

Does not copy. Does not touch Nextcloud.
"""
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAFE = Path(__file__).resolve().parent / "STRUCTURED_COPY_MAP_SAFE.csv"
USED = ROOT / "STRUCTURED_COPY_MAP_FINAL_used.csv"
UPDATED = ROOT / "UPDATED COMPANY_FOLDERS_IN_FINAL_csv.csv"
OUT = Path(__file__).resolve().parent / "E2E_MAP_VERIFY_REPORT.txt"
CSV_FAIL = Path(__file__).resolve().parent / "E2E_MAP_VERIFY_FAILURES.csv"

PERSONISH = re.compile(
    r"\b(DIR[-\s]?3|DIR[-\s]?6|DIR[-\s]?12|DIN\s?\d|KYC|WEB KYC|FORM KYC)\b",
    re.I,
)


def sanitize(name: object) -> str:
    s = str(name or "").strip()
    s = re.sub(r'[<>:"/\\|?*\r\n\t]', " ", s)
    s = re.sub(r"\s+", " ", s).strip().rstrip(". ")
    if len(s) > 180:
        s = s[:180].rstrip(". ")
    return s or "(unknown)"


def key(name: object) -> str:
    s = str(name or "").upper()
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    used = load_csv(USED)
    safe = load_csv(SAFE)
    updated = load_csv(UPDATED)

    keep_names: set[str] = set()
    remap: dict[str, str] = {}
    nil_names: set[str] = set()
    updated_src: list[str] = []
    for r in updated:
        src = (r.get("company_folder_in_Final") or "").strip()
        dst = (r.get("company it shold be") or "").strip()
        if not src:
            continue
        updated_src.append(src)
        if not dst:
            keep_names.add(src)
        elif dst.lower() == "nil":
            nil_names.add(src)
        else:
            remap[src] = sanitize(dst)

    fails: list[dict] = []

    def fail(kind: str, **kw) -> None:
        row = {"kind": kind}
        row.update({k: str(v) for k, v in kw.items()})
        fails.append(row)

    lines: list[str] = []
    def out(*a) -> None:
        lines.append(" ".join(str(x) for x in a))

    out("=== COUNTS ===")
    out("used_rows", len(used))
    out("safe_rows", len(safe))
    out("updated_rows", len(updated_src), "keep", len(keep_names), "remap", len(remap), "nil", len(nil_names))
    if len(used) != len(safe):
        fail("ROW_COUNT", used=len(used), safe=len(safe))
    if len(used) != 6863:
        fail("USED_NOT_6863", n=len(used))
    if len(safe) != 6863:
        fail("SAFE_NOT_6863", n=len(safe))
    if len(updated_src) != 1322:
        fail("UPDATED_NOT_1322", n=len(updated_src))
    if len(keep_names) != 851:
        fail("KEEP_COUNT", n=len(keep_names))
    if len(remap) != 460:
        fail("REMAP_COUNT", n=len(remap))
    if len(nil_names) != 11:
        fail("NIL_COUNT", n=len(nil_names), names=" | ".join(sorted(nil_names)))

    needed = (
        "dest_relative",
        "dest_company",
        "dest_year",
        "dest_folder",
        "source_path",
        "remap_action",
        "old_dest_company",
    )
    if safe:
        miss_cols = [c for c in needed if c not in safe[0]]
        if miss_cols:
            fail("SAFE_MISSING_COLS", cols=",".join(miss_cols))

    # Pair by position AND by (old dest, source_path)
    if len(used) == len(safe):
        for i, (u, s) in enumerate(zip(used, safe), start=1):
            us = (u.get("source_path") or "").strip()
            ss = (s.get("source_path") or "").strip()
            if us != ss:
                fail("SOURCE_PATH_DRIFT", row=i, used=us, safe=ss)
            u_dest = (u.get("dest_company") or "").strip()
            old = (s.get("old_dest_company") or "").strip()
            if u_dest != old:
                fail("OLD_DEST_NE_USED", row=i, used_dest=u_dest, old=old, src=us)

    actions = Counter((r.get("remap_action") or "").strip() for r in safe)
    out("actions", dict(actions))
    unexpected = set(actions) - {
        "keep",
        "remap_alias",
        "remap_alias_key",
        "remap_alias_chain",
        "nil_unsorted",
    }
    if unexpected:
        fail("UNEXPECTED_ACTION", actions=",".join(sorted(unexpected)))
    if actions.get("nil_from_12"):
        fail("NIL_FROM_12_PRESENT", n=actions["nil_from_12"])

    # Every used dest_company must appear in updated sheet
    used_dests = {(r.get("dest_company") or "").strip() for r in used}
    updated_set = set(updated_src)
    extra_used = sorted(used_dests - updated_set - {""})
    missing_updated = sorted(updated_set - used_dests)
    out("used unique dest_company", len(used_dests))
    out("updated names not in used dest", len(missing_updated))
    out("used dest not in updated sheet", len(extra_used))
    for n in extra_used[:50]:
        fail("USED_DEST_NOT_IN_UPDATED", dest=n)
    for n in missing_updated[:50]:
        fail("UPDATED_NAME_NOT_IN_USED", dest=n)

    # Per-row staff rule
    applied_remap_names: set[str] = set()
    nil_rows = 0
    keep_wrong = remap_wrong = nil_wrong = 0
    dest_rel_wrong = 0
    empty_src = 0
    form_only = 0
    h_drive = 0
    FORM_ONLY = {"ADT-1", "MGT-7", "STK-2", "SH-7", "AOC-4"}

    for i, s in enumerate(safe, start=1):
        dest = (s.get("dest_company") or "").strip()
        old = (s.get("old_dest_company") or "").strip()
        act = (s.get("remap_action") or "").strip()
        year = (s.get("dest_year") or "").strip()
        folder = (s.get("dest_folder") or "").strip()
        rel = (s.get("dest_relative") or "").strip()
        src = (s.get("source_path") or "").strip()
        expect_rel = f"{dest}\\{year}\\{folder}"
        if rel != expect_rel:
            dest_rel_wrong += 1
            if dest_rel_wrong <= 30:
                fail("DEST_RELATIVE_MISMATCH", row=i, got=rel, expect=expect_rel)
        if not src:
            empty_src += 1
            fail("EMPTY_SOURCE", row=i, dest=dest)
        if src in FORM_ONLY:
            form_only += 1
        if src.upper().startswith("H:\\"):
            h_drive += 1

        if old in nil_names:
            nil_rows += 1
            if act != "nil_unsorted":
                nil_wrong += 1
                fail("NIL_BAD_ACTION", row=i, old=old, act=act, dest=dest, src=src)
            expect_co = f"_UNSORTED\\{sanitize(old)}"
            if dest != expect_co:
                nil_wrong += 1
                fail("NIL_NOT_UNSORTED", row=i, old=old, dest=dest, expect=expect_co)
            if dest in remap.values() or (not dest.startswith("_UNSORTED\\")):
                fail("NIL_ASSIGNED_COMPANY", row=i, dest=dest, old=old)
        elif old in remap:
            applied_remap_names.add(old)
            expect = remap[old]
            hops = 0
            seen = {old}
            while expect in remap and remap[expect] != expect and expect not in seen and hops < 8:
                seen.add(expect)
                expect = remap[expect]
                hops += 1
            if dest == old:
                if act != "keep":
                    remap_wrong += 1
                    fail("IDENTITY_NOT_KEEP", row=i, old=old, act=act, dest=dest)
            else:
                if act not in {"remap_alias", "remap_alias_key", "remap_alias_chain"}:
                    remap_wrong += 1
                    fail("REMAP_BAD_ACTION", row=i, old=old, act=act, dest=dest)
                if dest != expect:
                    remap_wrong += 1
                    fail("REMAP_WRONG_TARGET", row=i, old=old, dest=dest, expect=expect, src=src)
        elif old in keep_names:
            if act != "keep":
                keep_wrong += 1
                fail("KEEP_BAD_ACTION", row=i, old=old, act=act, dest=dest)
            if dest != old:
                keep_wrong += 1
                fail("KEEP_CHANGED", row=i, old=old, dest=dest, src=src)
        else:
            fail("OLD_DEST_UNKNOWN_TO_UPDATED", row=i, old=old, dest=dest, src=src)

    out("nil_rows", nil_rows, "remap names applied", len(applied_remap_names), "of", len(remap))
    out("form_only_paths", form_only, "h_drive", h_drive, "empty_src", empty_src)
    unapplied = sorted(set(remap) - applied_remap_names)
    if unapplied:
        for n in unapplied:
            fail("REMAP_NAME_ZERO_ROWS", name=n, target=remap[n])

    # After remap: leftover person/form dest companies (excluding _UNSORTED)
    leftover_person = Counter()
    companies = Counter()
    for s in safe:
        dest = (s.get("dest_company") or "").strip()
        companies[dest] += 1
        if dest.startswith("_UNSORTED\\"):
            continue
        if PERSONISH.search(dest):
            leftover_person[dest] += 1
    out("unique dest_company after", len(companies))
    out("leftover DIR/KYC dest_company", len(leftover_person))
    for n, c in leftover_person.most_common(40):
        fail("LEFTOVER_PERSONISH_DEST", dest=n, rows=c)

    # Staff remap target should not be nil
    for src, dst in remap.items():
        if dst.lower() == "nil" or dst.startswith("_UNSORTED"):
            fail("REMAP_TARGET_IS_NIL", src=src, dst=dst)

    # Collision: different source_path same dest_relative
    by_rel: dict[str, set[str]] = defaultdict(set)
    for s in safe:
        rel = (s.get("dest_relative") or "").strip().lower()
        src = (s.get("source_path") or "").strip().replace("/", "\\").lower()
        by_rel[rel].add(src)
    same = diff = 0
    for rel, srcs in by_rel.items():
        if len(srcs) <= 1:
            continue
        # actually count rows not unique srcs
        pass
    n_same = n_diff = 0
    by_rel_items: dict[str, list[str]] = defaultdict(list)
    for s in safe:
        rel = (s.get("dest_relative") or "").strip().lower()
        src = (s.get("source_path") or "").strip()
        by_rel_items[rel].append(src)
    for rel, srcs in by_rel_items.items():
        if len(srcs) < 2:
            continue
        uniq = {x.replace("/", "\\").lower() for x in srcs}
        if len(uniq) == 1:
            n_same += 1
        else:
            n_diff += 1
    out("dest_relative collisions same-source", n_same, "diff-source", n_diff)

    # Source path listed twice with DIFFERENT dest_company (real conflict)
    by_src: dict[str, set[str]] = defaultdict(set)
    by_src_rows: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for s in safe:
        src = (s.get("source_path") or "").strip().replace("/", "\\").lower()
        dest = (s.get("dest_company") or "").strip()
        by_src[src].add(dest)
        by_src_rows[src].append((dest, (s.get("remap_action") or "")))
    src_multi_company = {k: v for k, v in by_src.items() if len(v) > 1 and k}
    out("source_path mapping to >1 dest_company", len(src_multi_company))
    for src, dests in list(src_multi_company.items())[:40]:
        fail(
            "SOURCE_TO_MULTI_COMPANY",
            src=src[:240],
            dests=" | ".join(sorted(dests)),
        )

    remap_sources_as_dest = 0
    for dest in companies:
        if dest.startswith("_UNSORTED\\"):
            continue
        if dest in remap and remap[dest] != dest:
            remap_sources_as_dest += 1
            fail(
                "REMAP_SOURCE_STILL_DEST",
                dest=dest,
                should_be=remap[dest],
                rows=companies[dest],
            )
    out(
        "remap source names still appearing as dest_company (non-identity)",
        remap_sources_as_dest,
    )

    # nil names still appearing as top-level dest (not under _UNSORTED)
    for n in sorted(nil_names):
        if n in companies:
            fail("NIL_NAME_STILL_TOP_DEST", dest=n, rows=companies[n])

    out("")
    out("=== FAILURES", len(fails), "===")
    kinds = Counter(f["kind"] for f in fails)
    for k, n in kinds.most_common():
        out(f"  {n:5d}  {k}")

    with CSV_FAIL.open("w", encoding="utf-8-sig", newline="") as f:
        fields = ["kind"] + sorted({k for r in fails for k in r if k != "kind"})
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(fails)

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("failures_csv", CSV_FAIL, "n", len(fails))
    print("report", OUT)


if __name__ == "__main__":
    main()
