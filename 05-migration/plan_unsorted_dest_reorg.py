"""Plan dest-only reorg of _UNSORTED using SAFE companies + all-files lists.

Does not copy from E:/F:. Does not touch dest unless --apply is used via reorg_unsorted_dest.py.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"c:\Users\U.lalitha navya sri\Downloads\Logesh files")
SAFE = ROOT / "05-migration" / "STRUCTURED_COPY_MAP_SAFE.csv"
LISTS = [
    ROOT / "CHAT_EXPORT" / "source_lists" / "all_files_list (2).txt",
    ROOT / "CHAT_EXPORT" / "source_lists" / "all_files_list_2025_26.txt",
]
OUT_TXT = ROOT / "05-migration" / "UNSORTED_DEST_REORG_PLAN.txt"
OUT_CSV = ROOT / "05-migration" / "UNSORTED_DEST_REORG_PLAN.csv"

DATE_PREFIX = re.compile(
    r"^(?:UPLOADED(?:\s+ON)?\s+)?\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\s*[-_]?\s*",
    re.I,
)
FILE_EXT = re.compile(r"\.(xlsx|xls|pdf|docx|doc|zip|db|txt|csv|jpg|jpeg|png)$", re.I)
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
    return s


def norm(p: str) -> str:
    return (p or "").strip().strip('"').replace("/", "\\").rstrip("\\").upper()


def first_child(parent_n: str, file_n: str) -> str | None:
    if file_n == parent_n:
        return None
    prefix = parent_n + "\\"
    if not file_n.startswith(prefix):
        return None
    return file_n[len(prefix) :].split("\\", 1)[0]


def strip_to_company_guess(folder: str) -> str:
    s = folder.strip()
    s = DATE_PREFIX.sub("", s)
    s = re.sub(r"^UPLOADED ON\s+", "", s, flags=re.I)
    s = re.sub(r"[\s_-]+(?:DIR[-\s]?3(?:\s?KYC)?|WEB KYC)\s*$", "", s, flags=re.I)
    s = re.sub(r"[\s_-]+MGT[-\s]?8\s*$", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip(" -_")
    return s


def looks_like_file(name: str) -> bool:
    if FILE_EXT.search(name):
        return True
    if COMPANYISH.search(name):
        return False
    return False


def load_companies(safe_rows: list[dict]) -> tuple[dict[str, str], dict[str, str]]:
    exact: dict[str, str] = {}
    by_key: dict[str, str] = {}
    for r in safe_rows:
        co = (r.get("dest_company") or "").strip()
        if not co or co.startswith("_UNSORTED"):
            continue
        exact[co.upper()] = co
        k = key(co)
        if k and k not in by_key:
            by_key[k] = co
        old = (r.get("old_dest_company") or "").strip()
        if old and not old.startswith("_UNSORTED"):
            exact.setdefault(old.upper(), co)
            ok = key(old)
            if ok and ok not in by_key:
                by_key[ok] = co
        raw = (r.get("company") or "").strip()
        if raw:
            exact.setdefault(raw.upper(), co)
            rk = key(raw)
            if rk and rk not in by_key:
                by_key[rk] = co
    return exact, by_key


def match_company(folder: str, exact: dict[str, str], by_key: dict[str, str]) -> tuple[str | None, str]:
    guess = strip_to_company_guess(folder)
    if not guess:
        return None, "empty_guess"
    if guess.upper() in exact:
        return exact[guess.upper()], "exact_folder"
    kg = key(guess)
    if kg in by_key:
        return by_key[kg], "key_guess"
    if folder.upper() in exact:
        return exact[folder.upper()], "exact_full"
    kf = key(folder)
    if kf in by_key:
        return by_key[kf], "key_full"
    # longest key contained in folder key
    best = ""
    best_co = None
    for k, co in by_key.items():
        if len(k) < 12:
            continue
        if k in kf or kf in k:
            if len(k) > len(best):
                best = k
                best_co = co
    if best_co:
        return best_co, "contains_key"
    if COMPANYISH.search(guess or folder):
        return sanitize(guess or folder), "folder_as_company"
    return None, "unmatched"


# dest_relative of unsorted parents from SAFE
PILES = [
    {
        "id": "ARUNKUMAR",
        "dest_rel": r"_UNSORTED\ARUNKUMAR CASES\2023-24\ARUNKUMAR CASES",
        "year": "2023-24",
        "source": r"E:\NOT IN BACKUP\ARUNKUMAR CASES",
        "mode": "split_named_then_drop_if_empty",
    },
    {
        "id": "CERTIFIED_FORMS",
        "dest_rel": r"_UNSORTED\CERTIFIED FORMS\2023-24\CERTIFIED FORMS",
        "year": "2023-24",
        "source": r"E:\BACK UP FOLDER\2023-2024\UPLOADED EFORMS\1. APRIL\CERTIFIED FORMS",
        "mode": "split_named",
    },
    {
        "id": "CERTIFIED_FORMS_UPLOADED",
        "dest_rel": r"_UNSORTED\CERTIFIED FORMS UPLOADED\2022-23\CERTIFIED FORMS UPLOADED",
        "year": "2022-23",
        "source": r"E:\BACK UP FOLDER\2022-2023\UPLOADED FORMS\8.NOVEMBER 2022\CERTIFIED FORMS UPLOADED",
        "mode": "delete_pile",
    },
    {
        "id": "CFSS_NEOMAX",
        "dest_rel": r"_UNSORTED\CFSS - NEOMAX\2021-22\CFSS - NEOMAX",
        "year": "2021-22",
        "source": r"F:\2021-2022\UPLOADED FORMS\CFSS\CFSS  - NEOMAX",
        "mode": "split_named",
    },
    {
        "id": "CFSS_OTHER",
        "dest_rel": r"_UNSORTED\CFSS FORMS - OTHER COMPANIES\2021-22\CFSS FORMS - OTHER COMPANIES",
        "year": "2021-22",
        "source": r"F:\2021-2022\UPLOADED FORMS\CFSS\CFSS FORMS - OTHER COMPANIES",
        "mode": "split_named",
    },
    {
        "id": "CHINNIAIH",
        "dest_rel": r"_UNSORTED\CHINNIAIH CASES - KYC\2024-25\CHINNIAIH CASES - KYC",
        "year": "2024-25",
        "source": r"F:\2024-2025\UPLOADED FORMS\6. SEPTEMBER 2024\CHINNIAIH CASES - KYC",
        "mode": "delete_pile",  # already under Chess Gaja + children
    },
    {
        "id": "CLSS_2014",
        "dest_rel": r"_UNSORTED\CLSS 2014 FOR 8 COMPANIES\2014-15\Uploaded on 17-10-2014 CLSS 2014 FOR 8 COMPANIES",
        "year": "2014-15",
        "source": r"F:\2014-15\UPLOADED FORMS\OCTOBER 2014\Uploaded on 17-10-2014 CLSS 2014 FOR 8 COMPANIES",
        "mode": "delete_pile",
    },
    {
        "id": "LIST_PREPARED_CFSS",
        "dest_rel": r"_UNSORTED\LIST PREPARED\2021-22\LIST PREPARED",
        "year": "2021-22",
        "source": r"F:\2021-2022\UPLOADED FORMS\CFSS\LIST PREPARED",
        "mode": "delete_pile",
    },
    {
        "id": "LIST_PREPARED_KULUMAI",
        "dest_rel": r"_UNSORTED\LIST PREPARED\2021-22\PREPARED DOCS FOR List of Shareholders",
        "year": "2021-22",
        "source": r"F:\2021-2022\UPLOADED FORMS\DECEMBER 2021\UPLOADED ON 28.12.2021 KULUMAI MILK PRODUCER COMPANY LIMITED- AOC-4, MGT-7A, ADT-1\BACK UP\PREPARED DOCS FOR List of Shareholders",
        "mode": "delete_pile",
    },
    {
        "id": "MAHARAJ_LIST",
        "dest_rel": r"_UNSORTED\MAHARAJ SIR LIST\2020-21\MAHARAJ SIR LIST",
        "year": "2020-21",
        "source": r"E:\BACK UP FOLDER\2020-2021\UPLOADED FORMS\JUNE 2020\MAHARAJ SIR LIST",
        "mode": "delete_pile",
    },
    {
        "id": "MAHARAJA_CLIENTS",
        "dest_rel": r"_UNSORTED\MAHARAJA SIR CLIENTS DIR-3 KYC AND WEB KY\2019-20\UPLOADED ON 14.10.2019 MAHARAJA SIR CLIENTS DIR-3 KYC AND WEB KYC",
        "year": "2019-20",
        "source": r"F:\2019-2020\UPLOADED FORMS\October 2019\UPLOADED ON 14.10.2019 MAHARAJA SIR CLIENTS DIR-3 KYC AND WEB KYC",
        "mode": "split_named_force",
        "force": {
            "BHAIRAVAR FARMS AND FOODS PRIVATE LIMITED": "BHAIRAVAR FARMS AND FOODS PRIVATE LIMITED",
        },
    },
    {
        "id": "SURRENDER_DIN",
        "dest_rel": r"_UNSORTED\SURRENDER OF DIN\2015-16\SURRENDER OF DIN",
        "year": "2015-16",
        "source": r"F:\2015-16\UPLOADED FORMS\MAY 2015\SURRENDER OF DIN",
        "mode": "delete_pile",
    },
]


def already_mapped_children(safe_rows: list[dict], parent: str) -> set[str]:
    pn = norm(parent)
    out = set()
    for r in safe_rows:
        dest = (r.get("dest_company") or "").strip()
        if dest.startswith("_UNSORTED"):
            continue
        sp = norm(r.get("source_path") or "")
        if sp == pn or sp.startswith(pn + "\\"):
            ch = first_child(pn, sp) if sp != pn else None
            if ch:
                out.add(ch)
            elif sp == pn:
                out.add("__WHOLE_PARENT__")
    return out


def main() -> None:
    with SAFE.open(encoding="utf-8-sig", newline="") as f:
        safe_rows = list(csv.DictReader(f))
    exact, by_key = load_companies(safe_rows)

    parents = {norm(p["source"]): {**p, "children": defaultdict(int), "files_at_parent": 0} for p in PILES}

    for lp in LISTS:
        with lp.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("====="):
                    continue
                if not (len(s) >= 3 and s[1] == ":" and s[2] == "\\"):
                    continue
                sn = norm(s)
                for rec in parents.values():
                    pn = norm(rec["source"])
                    if sn == pn:
                        rec["files_at_parent"] += 1
                    elif sn.startswith(pn + "\\"):
                        ch = first_child(pn, sn)
                        if ch:
                            rec["children"][ch] += 1

    # ARUNKUMAR not in lists — still plan from SAFE child names
    csv_rows = []
    lines = [
        "DEST-ONLY reorg plan. No E:/F: recopy.",
        "Run reorg_unsorted_dest.py --dest F:\\f --dry-run  then  --apply",
        f"known_companies {len(set(by_key.values()))}",
        "",
    ]

    for pile in PILES:
        rec = parents[norm(pile["source"])]
        mapped = already_mapped_children(safe_rows, pile["source"])
        year = pile["year"]
        lines.append(f"=== {pile['id']}  mode={pile['mode']}  year={year} ===")
        lines.append(f"dest {pile['dest_rel']}")
        kids = rec["children"]
        if pile["id"] == "ARUNKUMAR" and not kids:
            # from SAFE mapped children names
            for r in safe_rows:
                sp = (r.get("source_path") or "").strip()
                if norm(sp).startswith(norm(pile["source"]) + "\\"):
                    ch = first_child(norm(pile["source"]), norm(sp))
                    if ch and ch not in kids:
                        kids[ch] = 0
            lines.append("NOTE ARUNKUMAR parent not in all-files lists; children from SAFE map only")

        if pile["mode"] == "delete_pile":
            csv_rows.append(
                {
                    "action": "DELETE_UNSORTED_DEST",
                    "pile": pile["id"],
                    "src_dest_rel": pile["dest_rel"],
                    "child": "",
                    "company": "",
                    "target_rel": "",
                    "skip_if_exists": "n",
                    "note": "user_delete_or_already_under_company",
                }
            )
            lines.append("ACTION DELETE entire dest folder (no split)")
            lines.append("")
            continue

        force = pile.get("force") or {}
        for ch, cnt in sorted(kids.items(), key=lambda x: x[0]):
            is_file = looks_like_file(ch)
            ch_display = ch
            matched = None
            how = ""
            for fk, co in force.items():
                if key(fk) == key(ch) or key(fk) in key(ch):
                    matched, how = co, "user_force"
                    break
            if not matched and not is_file:
                matched, how = match_company(ch, exact, by_key)
            already = False
            chk = key(ch)
            gk = key(strip_to_company_guess(ch))
            mapped_keys = {key(x) for x in mapped}
            if chk in mapped_keys or gk in mapped_keys or ch.upper() in mapped:
                already = True
            if "__WHOLE_PARENT__" in mapped and pile["mode"] == "delete_pile":
                already = True
            if pile["mode"] == "split_named_force" and how != "user_force" and already:
                action = "DELETE_DEST_CHILD"
                note = "duplicate under unsorted; child already copied under a company"
                target = ""
            elif matched:
                folder_name = sanitize(ch)
                target = f"{matched}\\{year}\\{folder_name}"
                if already and how != "user_force":
                    action = "DELETE_DEST_CHILD"
                    note = f"matched {how} but child already mapped; delete unsorted duplicate"
                    target = ""
                else:
                    action = "MOVE_DEST_CHILD"
                    note = f"match={how} listing_files={cnt}"
            elif is_file:
                action = "LEAVE_FILE"
                note = "loose file in parent; no company in name"
                target = ""
            else:
                action = "UNMATCHED_CHILD"
                note = f"no dest_company for folder listing_files={cnt}"
                target = ""
            csv_rows.append(
                {
                    "action": action,
                    "pile": pile["id"],
                    "src_dest_rel": pile["dest_rel"],
                    "child": ch_display,
                    "company": matched or "",
                    "target_rel": target,
                    "skip_if_exists": "y" if action == "MOVE_DEST_CHILD" else "n",
                    "note": note,
                }
            )
            lines.append(f"  {action} | {ch} -> {matched or '-'} | {note}")

        # after splits, delete leftover unsorted dest if empty
        csv_rows.append(
            {
                "action": "DELETE_UNSORTED_IF_EMPTY",
                "pile": pile["id"],
                "src_dest_rel": pile["dest_rel"],
                "child": "",
                "company": "",
                "target_rel": "",
                "skip_if_exists": "n",
                "note": "after moves; leftover unmatched stay until office names them",
            }
        )
        lines.append("")

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "action",
                "pile",
                "src_dest_rel",
                "child",
                "company",
                "target_rel",
                "skip_if_exists",
                "note",
            ],
        )
        w.writeheader()
        w.writerows(csv_rows)
    print(OUT_CSV)
    acts = defaultdict(int)
    for r in csv_rows:
        acts[r["action"]] += 1
    print(dict(acts))
    print("unmatched", acts.get("UNMATCHED_CHILD", 0), "moves", acts.get("MOVE_DEST_CHILD", 0))


if __name__ == "__main__":
    main()
