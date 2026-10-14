"""Map 2026-27 Uploaded Forms folders onto the final company list.

Uses STRUCTURED_COPY_MAP_SAFE companies + staff aliases + spelling merges.
Does not guess nil. Unmatched non-company piles -> _UNSORTED.
Does not copy files.
"""
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SAFE = HERE / "STRUCTURED_COPY_MAP_SAFE.csv"
FINAL_LIST = HERE / "COMPANY_FOLDERS_IN_FINAL.csv"
FF_LIST = HERE / "F_F_COMPANY_FOLDERS.txt"
ALIASES = ROOT / "UPDATED COMPANY_FOLDERS_IN_FINAL_csv.csv"
MERGES = HERE / "SPELLING_MERGES.csv"
OUT = HERE / "STRUCTURED_COPY_MAP_2026_27.csv"
REPORT = HERE / "MAP_2026_27_REPORT.txt"
UNSORTED_CSV = HERE / "MAP_2026_27_UNSORTED.csv"

SOURCES = [
    (
        "OS",
        Path(r"D:\OFFICE SARASWATHI\2026-27\UPLOADED FORMS"),
    ),
    (
        "CHENNAI",
        Path(r"D:\OFFICE SARASWATHI\CHENNAI OFFICE BACK UP\2026-2027\UPLOADED FORMS"),
    ),
]

YEAR = "2026-27"
UNSORTED = "_UNSORTED"

STOP = {
    "PRIVATE",
    "PVT",
    "LIMITED",
    "LTD",
    "COMPANY",
    "THE",
    "AND",
    "OF",
    "FOR",
    "OPC",
    "LLP",
    "PRODUCER",
}

DATE_PREFIX = re.compile(
    r"^(?:UPLOADED(?:\s+ON)?\s+)?(?:\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\s*(?:&\s*\d{1,2}[./-]\d{1,2}[./-]\d{2,4})?\s*[-_]?\s*)+",
    re.I,
)

FORM_TAIL = re.compile(
    r"[\s,_-]+(?:"
    r"F\s+)?"
    r"(?:"
    r"DIR[-\s]?\d+(?:\s*(?:KYC|WEB|MR\.?\s*\w+|APPOINTMENT|2\s*NOS))?"
    r"|WEB\s*KYC|KYC(?:\s+AND)?"
    r"|DIN(?:\s+APPLICATION(?:\s+FORMS)?)?"
    r"|INC[-\s]?\d+[A-Z]?"
    r"|CHG[-\s]?\d+"
    r"|PAS[-\s]?\d+"
    r"|ADT[-\s]?\d+"
    r"|DPT[-\s]?\d+"
    r"|MGT[-\s]?\d+[A-Z]?"
    r"|AOC[-\s]?\d+(?:\s*XBRL)?"
    r"|SH[-\s]?\d+"
    r"|STK[-\s]?\d+"
    r"|CSR[-\s]?\d+(?:[-\s]?\d{2}[-\s]?\d{2})?"
    r"|SK[-\s]?\d+"
    r"|SPICE(?:\s*[AB&]+)?"
    r"|RUN(?:\s+FORM)?"
    r"|AF(?:[-\s]?\d{2,4}[-\s]?\d{2,4})?"
    r"|ANNUAL\s+FILING(?:\s+\d{4}[-\s]?\d{2,4})?"
    r"|CS\s+APPOINTMENT"
    r"|SHARE\s+TRANSFER"
    r"|FORM\s+ADT[-\s]?\d+"
    r"|APPOINTMENT"
    r"|2\s*NOS"
    r")(?:\s*[&,/].*)?$",
    re.I,
)

# Folder / guess text -> canonical dest_company from final list (or new legal name).
EXPLICIT = {
    "SHIVANAYAHI SOLAR": "SHIVANAYAHI SOLAR POWER DEVELOPER PRIVATE LIMITED",
    "SHIVANAYAHI SOLAR ANNUAL FILING 2024 2025": "SHIVANAYAHI SOLAR POWER DEVELOPER PRIVATE LIMITED",
    "MTURN TOURISM PRIVATE": "MTURN TOURISM PRIVATE LIMITED",
    "LAADLALADLI": "LAADLALAADLI.INDIA PRIVATE LIMITED",
    "LAADLALAADLI INDIA PRIVATE LIMITED": "LAADLALAADLI.INDIA PRIVATE LIMITED",
    "PUNAM MULLICK": "LAADLALAADLI.INDIA PRIVATE LIMITED",
    "PUNAM MULLICK LAADLALADLI": "LAADLALAADLI.INDIA PRIVATE LIMITED",
    "DIR 3 PUNAM MULLICK LAADLALADLI": "LAADLALAADLI.INDIA PRIVATE LIMITED",
    "DIR 12 SHARE TRANSFER PUNAM MULLICK LAADLALADLI": "LAADLALAADLI.INDIA PRIVATE LIMITED",
    "AR A S APPLIANCES PRIVATE LIMITED": "AR A S APPLIANCE PRIVATE LIMITED",
    "AR.A.S APPLIANCES PRIVATE LIMITED": "AR A S APPLIANCE PRIVATE LIMITED",
    "RIO CHILDRENS HOSPITAL PRIVATE LIMITED": "RIO CHILDREN'S HOSPITAL PRIVATE LIMITED",
    "RIO CHILDREN S HOSPITAL PRIVATE LIMITED": "RIO CHILDREN'S HOSPITAL PRIVATE LIMITED",
    "RIO CHILDREN HOSPITAL PRIVATE LIMITED": "RIO CHILDREN'S HOSPITAL PRIVATE LIMITED",
    "RIO CHILDRENS HOSPITAL DINDIGUL PRIVATE LIMITED": "RIO CHILDREN'S HOSPITAL (DINDIGUL ) PRIVATE LIMITED",
    "RIO CHILDREN S HOSPITAL DINDIGUL PRIVATE LIMITED": "RIO CHILDREN'S HOSPITAL (DINDIGUL ) PRIVATE LIMITED",
    "RIO CHILDRENS HOSPITAL TANJORE PRIVATE LIMITED": "RIO CHILDRENS HOSPITAL (TANJORE) PRIVATE LIMITED",
    "SEL JEGAT PRINTERS PRIVATE LIMITED": "SEL JEGAT PRINTERS PRIVATE LIMITED",
    "SELJEGAT PRINTERS PRIVATE LIMITED": "SEL JEGAT PRINTERS PRIVATE LIMITED",
    "SEL JEGAT PRINTER PRIVATE LIMITED": "SEL JEGAT PRINTERS PRIVATE LIMITED",
    "PALANIAPPA MOTOR PRIVATE LIMITED": "PALANIAPPA’S MOTORS PRIVATE LIMITED",
    "PALANIAPPA MOTORS PRIVATE LIMITED": "PALANIAPPA’S MOTORS PRIVATE LIMITED",
    "PALANIAPPA S MOTORS PRIVATE LIMITED": "PALANIAPPA’S MOTORS PRIVATE LIMITED",
    "PALANIAPPA'S MOTORS PRIVATE LIMITED": "PALANIAPPA’S MOTORS PRIVATE LIMITED",
    "SEL JEGAT PRINT PACK PRIVATE LIMITED": "SEL JEGAT PRINT-PACK PRIVATE LIMITED",
    "SEL JEGAT PRINTPACK PRIVATE LIMITED": "SEL JEGAT PRINT-PACK PRIVATE LIMITED",
    "VISIONARY IMPRESSION PRIVATE LIMITED": "VISIONARY IMPRESSIONS PRIVATE LIMITED",
    "BRILLYTICS TECHNOLOGY SOLUTIONS PRIVATE LIMITED 24 25": "BRILLYTICS TECHNOLOGY SOLUTIONS PRIVATE LIMITED",
    "BRILLYTICS TECHNOLOGY SOLUTIONS PRIVATE LIMITED": "BRILLYTICS TECHNOLOGY SOLUTIONS PRIVATE LIMITED",
    "ADR PLASTICS PRIVATE LIMITED": "ADR PLASTIC PRIVATE LIMITED",
    "SOUTHFIELD CONSULTANTS PRIVATE LIMITED": "SOUTHFIELD CONSULTANT PRIVATE LIMITED",
    "ORIGINAL HOMOEO MEDICALS PRIVATE LIMITED": "ORIGINAL HOMEO MEDICALS PRIVATE LIMITED",
    "STATFIN GLOBAL SERVICES PRIVATE LIMITED": "STATFIN GLOABL SERVICES PRIVATE LIMITED",
    "CHARLIE ENGG CO PRIVATE LIMITED": "CHARLIE ENGG CO PRIVATE LIMITED",
    "AARAVERSE PRIVATE LIMITED KYC AND": "AARAVERSE PRIVATE LIMITED",
    "DANIYA DIR 3 KB GRID LLP": "KB GRID LLP",
    "KB GRID LLP": "KB GRID LLP",
    "SPS TRUST LLP CSR 1": "SPS TRUST LLP",
    "SIVAG GRAND TECHNOLOGIES PRIVATE LIMITED SK 2": "SIVAG GRAND TECHNOLOGIES PRIVATE LIMITED",
}

COMPANYISH = re.compile(
    r"\b(PRIVATE LIMITED|PVT\.?\s*LTD\.?|LIMITED|LTD\.?|LLP|OPC|PRODUCER COMPANY)\b",
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
    s = re.sub(r"\bLTD\b", "LIMITED", s)
    s = re.sub(r"\bPVT\.?\s*LIMITED\b", "PRIVATE LIMITED", s)
    s = re.sub(r"\bP\.?\s*LIMITED\b", "PRIVATE LIMITED", s)
    return s


def token_core(name: object) -> str:
    toks = [t for t in key(name).split() if t not in STOP and len(t) >= 2]
    return " ".join(toks)


def expand_legal(name: str) -> str:
    s = str(name or "")
    s = re.sub(r"\bLTD\b", "LIMITED", s, flags=re.IGNORECASE)
    s = re.sub(r"\bPVT\.?\s*LIMITED\b", "PRIVATE LIMITED", s, flags=re.IGNORECASE)
    s = re.sub(r"\bP\.?\s*LIMITED\b", "PRIVATE LIMITED", s, flags=re.IGNORECASE)
    return sanitize(s)


def strip_guess(folder: str) -> str:
    s = folder.strip()
    s = re.sub(r"^UPLOADED(?:\s+ON)?\s+", "", s, flags=re.I)
    s = DATE_PREFIX.sub("", s)
    s = s.strip(" -_")
    prev = None
    while prev != s:
        prev = s
        s = FORM_TAIL.sub("", s).strip(" -_")
    s = re.sub(r"\s+", " ", s).strip(" -_")
    s = re.sub(r"\s+\d{2}-\d{2,4}$", "", s).strip(" -_")
    return s


def load_aliases() -> tuple[dict[str, str], set[str]]:
    exact: dict[str, str] = {}
    nils: set[str] = set()
    if not ALIASES.is_file():
        return exact, nils
    with ALIASES.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            src = (r.get("company_folder_in_Final") or "").strip()
            dst = (r.get("company it shold be") or "").strip()
            if not src:
                continue
            if dst.lower() == "nil":
                nils.add(key(src))
                continue
            if not dst:
                continue
            dest = sanitize(dst)
            exact[key(src)] = dest
    return exact, nils


def load_merges() -> dict[str, str]:
    out: dict[str, str] = {}
    if not MERGES.is_file():
        return out
    with MERGES.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            src = (r.get("from_company") or "").strip()
            dst = (r.get("to_company") or "").strip()
            if src and dst:
                out[key(src)] = sanitize(dst)
    return out


def follow(
    name: str,
    alias: dict[str, str],
    merges: dict[str, str],
    ff_keys: set[str] | None = None,
) -> str:
    cur = sanitize(name)
    seen = {key(cur)}
    for _ in range(8):
        k = key(cur)
        if ff_keys and k in ff_keys:
            return cur
        nxt = alias.get(k) or merges.get(k)
        if not nxt or key(nxt) in seen:
            break
        cur = sanitize(nxt)
        seen.add(key(cur))
    return cur


def register_company(
    co: str, exact: dict[str, str], by_key: dict[str, str], by_core: dict[str, str]
) -> None:
    co = sanitize(co)
    if not co or co.startswith("_UNSORTED"):
        return
    exact.setdefault(co.upper(), co)
    k = key(co)
    if k:
        by_key.setdefault(k, co)
    c = token_core(co)
    if c:
        by_core.setdefault(c, co)


def load_ff_names() -> list[str]:
    if not FF_LIST.is_file():
        return []
    return [
        ln.strip()
        for ln in FF_LIST.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]


def load_companies() -> tuple[dict[str, str], dict[str, str], dict[str, str], set[str]]:
    exact: dict[str, str] = {}
    by_key: dict[str, str] = {}
    by_core: dict[str, str] = {}
    ff_names = load_ff_names()
    for co in ff_names:
        register_company(co, exact, by_key, by_core)
    if FINAL_LIST.is_file():
        with FINAL_LIST.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                co = (r.get("company_folder_in_Final") or r.get("company") or "").strip()
                register_company(co, exact, by_key, by_core)
    with SAFE.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            for col in ("dest_company", "old_dest_company", "company"):
                register_company(r.get(col) or "", exact, by_key, by_core)
    return exact, by_key, by_core, {key(n) for n in ff_names}


def apply_explicit(name: str) -> str | None:
    if not name:
        return None
    k = key(name)
    if k in EXPLICIT:
        return EXPLICIT[k]
    # Longest explicit key contained in the folder wins (Dindigul/Tanjore before generic RIO).
    hits: list[tuple[int, str]] = []
    for ek, dest in EXPLICIT.items():
        if len(ek) < 10:
            continue
        if ek == k or ek in k:
            hits.append((len(ek), dest))
    if hits:
        hits.sort(reverse=True)
        return hits[0][1]
    return None


def apply_known(name: str, exact: dict[str, str], by_key: dict[str, str], by_core: dict[str, str]) -> str | None:
    if not name:
        return None
    exp = apply_explicit(name)
    if exp:
        hit = None
        if exp.upper() in exact:
            hit = exact[exp.upper()]
        elif key(exp) in by_key:
            hit = by_key[key(exp)]
        elif token_core(exp) in by_core:
            hit = by_core[token_core(exp)]
        return hit or exp
    if name.upper() in exact:
        return exact[name.upper()]
    k = key(name)
    if k in by_key:
        return by_key[k]
    c = token_core(name)
    if c in by_core:
        return by_core[c]
    return None


def best_contains(folder_key: str, by_key: dict[str, str]) -> tuple[str | None, str]:
    best = ""
    best_co = None
    ties: list[str] = []
    for k, co in by_key.items():
        if len(k) < 12:
            continue
        if k in folder_key:
            if len(k) > len(best):
                best = k
                best_co = co
                ties = [co]
            elif len(k) == len(best) and co not in ties:
                ties.append(co)
    if best_co and len(ties) == 1:
        return best_co, "contains_key"
    return None, ""


def match_folder(
    folder: str,
    exact: dict[str, str],
    by_key: dict[str, str],
    by_core: dict[str, str],
    alias: dict[str, str],
    merges: dict[str, str],
    nils: set[str],
    ff_keys: set[str] | None = None,
) -> tuple[str, str, str]:
    guess = strip_guess(folder)
    guess = expand_legal(guess)
    if key(guess) in nils or key(folder) in nils:
        return f"{UNSORTED}\\{sanitize(folder)[:80]}", "nil_unsorted", guess

    for candidate in (guess, folder, expand_legal(folder)):
        hit = apply_known(candidate, exact, by_key, by_core)
        if hit:
            if not apply_explicit(candidate):
                hit = follow(hit, alias, merges, ff_keys)
            return hit, "known", guess

    followed = follow(guess, alias, merges, ff_keys) if guess else ""
    if followed and followed != guess:
        hit = apply_known(followed, exact, by_key, by_core)
        if hit:
            return follow(hit, alias, merges, ff_keys), "alias_then_known", guess
        if COMPANYISH.search(followed):
            return follow(followed, alias, merges, ff_keys), "alias_new_company", guess

    fk = key(folder) + " " + key(guess)
    co, how = best_contains(fk, by_key)
    if co:
        return follow(co, alias, merges, ff_keys), how, guess

    if COMPANYISH.search(guess or folder):
        new_co = follow(expand_legal(guess or folder), alias, merges, ff_keys)
        hit = apply_known(new_co, exact, by_key, by_core)
        if hit:
            return follow(hit, alias, merges, ff_keys), "new_then_known", guess
        return new_co, "new_company", guess

    pile = sanitize(guess or folder)
    return f"{UNSORTED}\\{pile[:80]}", "unmatched", guess


def iter_jobs(root: Path):
    if not root.is_dir():
        return
    for month in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if not month.is_dir() or month.name.startswith("."):
            continue
        for job in sorted(month.iterdir(), key=lambda p: p.name.lower()):
            if job.is_dir() and not job.name.startswith("."):
                yield month.name, job


def main() -> None:
    exact, by_key, by_core, ff_keys = load_companies()
    alias, nils = load_aliases()
    merges = load_merges()
    for k, v in list(merges.items()):
        if k in ff_keys:
            continue
        by_key.setdefault(k, v)
        exact.setdefault(v.upper(), v)

    rows: list[dict] = []
    stats = Counter()
    unsorted_rows: list[dict] = []
    collisions: dict[str, list[str]] = defaultdict(list)

    for office, root in SOURCES:
        if not root.is_dir():
            raise SystemExit(f"Missing source: {root}")
        for month, job in iter_jobs(root):
            folder = job.name
            company, how, guess = match_folder(
                folder, exact, by_key, by_core, alias, merges, nils, ff_keys
            )
            dest_folder = sanitize(folder)
            dest_relative = f"{company}\\{YEAR}\\{dest_folder}"
            collisions[dest_relative.lower()].append(str(job))
            rows.append(
                {
                    "dest_relative": dest_relative,
                    "dest_company": company,
                    "dest_year": YEAR,
                    "dest_folder": dest_folder,
                    "source_path": str(job),
                    "office": office,
                    "month": month,
                    "match_how": how,
                    "guess": guess,
                    "origin": "HDD_2026_27",
                }
            )
            stats[how] += 1
            stats["rows"] += 1
            if company.startswith(UNSORTED):
                unsorted_rows.append(
                    {
                        "office": office,
                        "month": month,
                        "folder": folder,
                        "guess": guess,
                        "how": how,
                        "source_path": str(job),
                    }
                )

    # Chennai suffix when dest_relative collides across offices
    seen: dict[str, int] = {}
    for r in rows:
        rel = r["dest_relative"]
        k = rel.lower()
        if len(collisions[k]) <= 1:
            continue
        n = seen.get(k, 0)
        seen[k] = n + 1
        if n == 0:
            continue
        suffix = "_CHENNAI" if r["office"] == "CHENNAI" else f"_{r['office']}_{n}"
        folder = sanitize(r["dest_folder"] + suffix)
        r["dest_folder"] = folder
        r["dest_relative"] = f"{r['dest_company']}\\{YEAR}\\{folder}"
        r["match_how"] = r["match_how"] + "+collision_suffix"

    fields = [
        "dest_relative",
        "dest_company",
        "dest_year",
        "dest_folder",
        "source_path",
        "office",
        "month",
        "match_how",
        "guess",
        "origin",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    with UNSORTED_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["office", "month", "folder", "guess", "how", "source_path"]
        )
        w.writeheader()
        w.writerows(unsorted_rows)

    companies = sorted({r["dest_company"] for r in rows if not r["dest_company"].startswith(UNSORTED)})
    new_cos = sorted(
        {
            r["dest_company"]
            for r in rows
            if r["match_how"].startswith("new_company") or r["match_how"].startswith("alias_new")
        }
    )
    lines = [
        f"rows {stats['rows']}",
        f"known_companies_in_safe {len(by_key)}",
        f"mapped_companies {len(companies)}",
        f"unsorted {len(unsorted_rows)}",
        "",
        "match_how:",
    ]
    for k, v in stats.most_common():
        if k == "rows":
            continue
        lines.append(f"  {k} {v}")
    lines.append("")
    lines.append("new_company names:")
    lines.extend(f"  {c}" for c in new_cos)
    lines.append("")
    lines.append("unsorted folders:")
    for u in unsorted_rows:
        lines.append(f"  [{u['office']}] {u['month']} | {u['folder']} | guess={u['guess']} | {u['how']}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {OUT}")
    print(f"wrote {REPORT}")
    print(f"wrote {UNSORTED_CSV}")


if __name__ == "__main__":
    main()
