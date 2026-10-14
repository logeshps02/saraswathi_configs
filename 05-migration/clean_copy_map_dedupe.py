"""Fix 1: drop identical dest+source copy rows.
Fix 2: merge dest company names only for space/punct or 1-letter typos.
         LTD -> LIMITED; P/PVT immediately before LIMITED -> PRIVATE LIMITED.
         Extra/missing/different words stay separate.
Fix 3 skipped: keep (2) dest names."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re

import pandas as pd

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "STRUCTURED_COPY_MAP.xlsx"
OUT = ROOT / "STRUCTURED_COPY_MAP_FINAL.xlsx"
CHECK_CSV = ROOT / "STILL_SEPARATE.csv"
OUT_CSV = ROOT / "STRUCTURED_COPY_MAP_FINAL.csv"
MERGES_CSV = ROOT / "SPELLING_MERGES.csv"
DISC_CSV = ROOT / "DISCREPANCIES_TO_DECIDE.csv"


def norm_src(p) -> str:
    return str(p or "").strip().lower()


LEGAL_SAME = {"LTD": "LIMITED"}


def expand_legal_form(name: str) -> str:
    """LTD -> LIMITED. P/PVT only when they stand for PRIVATE before LIMITED."""
    s = str(name or "")
    s = re.sub(r"\bLTD\b", "LIMITED", s, flags=re.IGNORECASE)
    s = re.sub(r"\bPVT\.?\s*LIMITED\b", "PRIVATE LIMITED", s, flags=re.IGNORECASE)
    s = re.sub(r"\bP\.?\s*LIMITED\b", "PRIVATE LIMITED", s, flags=re.IGNORECASE)
    return s


def tokenize(name) -> list[str]:
    s = str(name or "").upper()
    s = s.replace("'", "").replace("'", "").replace("`", "")
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return []
    return [LEGAL_SAME.get(t, t) for t in s.split()]


def damerau_leq1(a: str, b: str) -> bool:
    """True if a and b differ by at most one insert/delete/replace or adjacent swap."""
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la > lb:
        a, b, la, lb = b, a, lb, la
    if la == lb:
        diffs = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        if len(diffs) == 1:
            return True
        if len(diffs) == 2 and diffs[1] == diffs[0] + 1 and a[diffs[0]] == b[diffs[1]] and a[diffs[1]] == b[diffs[0]]:
            return True
        return False
    # one insert into a to make b
    i = j = 0
    skipped = False
    while i < la and j < lb:
        if a[i] == b[j]:
            i += 1
            j += 1
            continue
        if skipped:
            return False
        skipped = True
        j += 1
    return True


def spelling_only_same(a: str, b: str) -> bool:
    """Merge only space/punct noise, or exactly one real word with a 1-letter typo.

    Extra/missing/different words stay separate (PRIVATE added, place name, etc.).
    Short tokens and numbers are treated as different words, not typos.
    """
    ta, tb = tokenize(a), tokenize(b)
    if not ta or not tb or len(ta) != len(tb):
        return False
    diffs = [(wa, wb) for wa, wb in zip(ta, tb) if wa != wb]
    if not diffs:
        return True
    for wa, wb in diffs:
        if wa.isdigit() or wb.isdigit():
            return False
        if min(len(wa), len(wb)) < 3:
            return False
        if not damerau_leq1(wa, wb):
            return False
    return True


class UnionFind:
    def __init__(self, items: list[str]) -> None:
        self.p = {x: x for x in items}

    def find(self, x: str) -> str:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def canonical_name(names: list[str], freq: dict[str, int]) -> str:
    def score(n: str) -> tuple:
        u = n.upper()
        complete_limited = 1 if u.rstrip().endswith("LIMITED") else 0
        broken_limited = 1 if re.search(r"\bLIMITE\b", u) and "LIMITED" not in u else 0
        missing_space_paren = 1 if re.search(r"\)[A-Z]", n) else 0
        double_space = 1 if "  " in n else 0
        return (
            complete_limited,
            -broken_limited,
            -missing_space_paren,
            -double_space,
            freq.get(n, 0),
            len(n),
        )

    return max(names, key=score)


def build_spelling_map(names: list[str], freq: dict[str, int]) -> dict[str, str]:
    uniq = sorted({n for n in names if n})
    uf = UnionFind(uniq)
    for i, a in enumerate(uniq):
        for b in uniq[i + 1 :]:
            if spelling_only_same(a, b):
                uf.union(a, b)
    groups: dict[str, list[str]] = defaultdict(list)
    for n in uniq:
        groups[uf.find(n)].append(n)
    mapping: dict[str, str] = {}
    for members in groups.values():
        canon = canonical_name(members, freq)
        for n in members:
            mapping[n] = canon
    return mapping


def main() -> None:
    xl = pd.ExcelFile(SRC)
    sheets = {name: pd.read_excel(SRC, sheet_name=name, dtype=object) for name in xl.sheet_names}
    cm = sheets["COPY_MAP"].copy()
    before = len(cm)

    cm["_src_l"] = cm["source_path"].map(norm_src)
    cm["_dest_l"] = cm["dest_relative"].astype(str).str.strip().str.lower()

    # Keep first occurrence of identical dest + source
    dup_mask = cm.duplicated(["_dest_l", "_src_l"], keep="first")
    removed = int(dup_mask.sum())
    cleaned = cm.loc[~dup_mask].copy()

    companies_before = int(cleaned["dest_company"].nunique())
    freq = cleaned["dest_company"].value_counts().to_dict()
    spelling_map = build_spelling_map(list(cleaned["dest_company"].dropna().astype(str)), freq)
    cleaned["dest_company_before"] = cleaned["dest_company"]
    cleaned["dest_company"] = cleaned["dest_company"].map(lambda x: spelling_map.get(str(x), x) if pd.notna(x) else x)
    cleaned["dest_company"] = cleaned["dest_company"].map(lambda x: expand_legal_form(str(x)) if pd.notna(x) else x)
    cleaned["dest_relative"] = (
        cleaned["dest_company"].astype(str)
        + "\\"
        + cleaned["dest_year"].astype(str)
        + "\\"
        + cleaned["dest_folder"].astype(str)
    )
    cleaned["_dest_l"] = cleaned["dest_relative"].astype(str).str.strip().str.lower()

    # After spelling merge, identical dest+source may appear again
    spell_dup = cleaned.duplicated(["_dest_l", "_src_l"], keep="first")
    removed_after_spell = int(spell_dup.sum())
    cleaned = cleaned.loc[~spell_dup].copy()

    merge_rows = []
    seen_from = set()
    for old in sorted({str(x) for x in cleaned["dest_company_before"].dropna()}):
        new2 = expand_legal_form(spelling_map.get(old, old))
        if old == new2 or old in seen_from:
            continue
        seen_from.add(old)
        old_u = old.upper()
        if re.search(r"\bP(VT)?\.?\s*(LTD|LIMITED)\b", old_u) and "PRIVATE LIMITED" in new2.upper() and "PRIVATE" not in re.sub(r"\bP(VT)?\.?\s*(LTD|LIMITED)\b", "", old_u):
            reason = "P_PVT_TO_PRIVATE"
        elif tokenize(expand_legal_form(old)) == tokenize(new2) and "LTD" in old_u and "LIMITED" in new2.upper():
            reason = "LTD_TO_LIMITED"
        else:
            reason = "SPELLING_OR_SPACE"
        merge_rows.append(
            {
                "from_company": old,
                "to_company": new2,
                "rows_moved": int(freq.get(old, 0)),
                "reason": reason,
            }
        )
    merges = pd.DataFrame(merge_rows)
    n_names_merged = int(merges["from_company"].nunique()) if len(merges) else 0
    n_canon = int(merges["to_company"].nunique()) if len(merges) else 0

    def classify_remaining(names: list[str]) -> str:
        toks = [tokenize(n) for n in names if n]
        if not toks:
            return "KEEP_SEPARATE"
        lens = {len(t) for t in toks}
        if lens != {len(toks[0])}:
            return "KEEP_SEPARATE_WORD_COUNT"
        return "KEEP_SEPARATE_DIFFERENT_WORD"

    g = (
        cleaned.groupby("_src_l")
        .agg(
            n_companies=("dest_company", lambda s: s.nunique()),
            companies=("dest_company", lambda s: " | ".join(sorted({str(x) for x in s if pd.notna(x)}))),
            n_rows=("source_path", "size"),
            source_path=("source_path", "first"),
            dest_years=("dest_year", lambda s: " | ".join(sorted({str(x) for x in s if pd.notna(x)}))),
            origins=("origin", lambda s: " | ".join(sorted({str(x) for x in s if pd.notna(x)}))),
        )
        .reset_index(drop=True)
    )
    multi = g[g["n_companies"] > 1].sort_values(["n_companies", "companies"], ascending=[False, True]).copy()
    multi["reason_kept_separate"] = multi["companies"].map(lambda x: classify_remaining(str(x).split(" | ")))
    multi["action"] = "KEEP_SEPARATE"
    multi = multi[
        [
            "action",
            "reason_kept_separate",
            "n_companies",
            "n_rows",
            "companies",
            "dest_years",
            "origins",
            "source_path",
        ]
    ]
    reason_counts = multi["reason_kept_separate"].value_counts().to_dict()

    def pair_kind(names: list[str]) -> str:
        toks = [tokenize(n) for n in names if n]
        if not toks:
            return "OTHER"
        if len({len(t) for t in toks}) != 1:
            shorts = [t for t in toks if len(t) == min(len(x) for x in toks)]
            longs = [t for t in toks if len(t) == max(len(x) for x in toks)]
            if shorts and longs:
                s, l = shorts[0], longs[0]
                extra = [w for w in l if w not in s]
                if extra == ["PRIVATE"] or extra == ["PRIVATE", "LIMITED"] or extra == ["LIMITED"]:
                    return "LEGAL_FORM_PRIVATE_OR_LIMITED_ADDED"
                if any(w in {"DIR", "KYC", "FORM"} for w in extra) or any("DIR" in n.upper() or "KYC" in n.upper() for n in names):
                    return "DIRECTOR_OR_KYC_VS_COMPANY"
                if any(re.search(r"\([^)]+\)", n) for n in names) and not all(re.search(r"\([^)]+\)", n) for n in names):
                    return "PLACE_OR_BRACKET_ADDED"
            return "EXTRA_OR_MISSING_WORD"
        # same word count
        joined_diff = []
        for col in zip(*toks):
            if len(set(col)) > 1:
                joined_diff.append("/".join(sorted(set(col))))
        if joined_diff and all(a in {"PRIVATE", "P"} or b in {"PRIVATE", "P"} for pair in [tuple(x.split("/")) for x in joined_diff] for a, b in [pair if len(pair) == 2 else (pair[0], "")]):
            return "P_VS_PRIVATE"
        if any(re.search(r"\([^)]+\)", n) for n in names):
            places = set()
            for n in names:
                places.update(re.findall(r"\(([^)]+)\)", n.upper()))
            if len(places) > 1:
                return "PLACE_VARIANT"
        return "DIFFERENT_WORD"

    disc_rows = []
    for companies, grp in multi.groupby("companies"):
        names = [x.strip() for x in str(companies).split(" | ") if x.strip()]
        disc_rows.append(
            {
                "decision": "",  # fill MERGE or KEEP
                "merge_to": "",  # if MERGE, type the dest company name to keep
                "kind": pair_kind(names),
                "n_company_names": len(names),
                "n_source_folders": int(grp["source_path"].nunique()),
                "n_copy_rows": int(grp["n_rows"].sum()),
                "company_names": companies,
            }
        )
    discrepancies = pd.DataFrame(disc_rows).sort_values(["kind", "company_names"], kind="stable")
    kind_counts = discrepancies["kind"].value_counts().to_dict() if len(discrepancies) else {}

    dest_dups_left = int((cleaned["_dest_l"].value_counts() > 1).sum())
    paren2 = int(cleaned["dest_folder"].astype(str).str.contains(r"\(\d+\)$", regex=True, na=False).sum())

    cleaned = cleaned.drop(columns=["_src_l", "_dest_l", "dest_company_before"], errors="ignore")
    cleaned = cleaned.sort_values(["dest_company", "dest_year", "dest_folder", "source_path"], kind="stable")

    tree = (
        cleaned.groupby(["dest_company", "dest_year", "dest_folder", "source_path"], dropna=False)
        .size()
        .reset_index(name="n")
        .drop(columns=["n"])
    )

    summary_extra = pd.DataFrame(
        [
            ("fix1_identical_dest_source_removed", removed),
            ("fix2_rule", "merge space/punct, 1-letter typo, and LTD->LIMITED; extra/missing word kept separate"),
            ("fix2_company_names_renamed", n_names_merged),
            ("fix2_canonical_names_received", n_canon),
            ("fix2_rows_dropped_after_rename_identical", removed_after_spell),
            ("copy_rows_after_fix1_fix2", len(cleaned)),
            ("unique_companies_before_spelling", companies_before),
            ("unique_companies_after_spelling", int(cleaned["dest_company"].nunique())),
            ("unique_company_year_after", int(cleaned.groupby(["dest_company", "dest_year"]).ngroups)),
            ("from_final_after", int((cleaned["origin"] == "FINAL").sum())),
            ("from_review_true_after", int((cleaned["origin"] == "REVIEW_TRUE").sum())),
            ("dest_relative_still_listed_twice", dest_dups_left),
            ("dest_folders_with_2_suffix_kept", paren2),
            ("multi_company_sources_still_separate", len(multi)),
            ("kept_word_count_diff", reason_counts.get("KEEP_SEPARATE_WORD_COUNT", 0)),
            ("kept_different_word", reason_counts.get("KEEP_SEPARATE_DIFFERENT_WORD", 0)),
            ("unique_discrepancy_groups", len(discrepancies)),
            ("disc_LEGAL_FORM_PRIVATE_OR_LIMITED_ADDED", kind_counts.get("LEGAL_FORM_PRIVATE_OR_LIMITED_ADDED", 0)),
            ("disc_DIRECTOR_OR_KYC_VS_COMPANY", kind_counts.get("DIRECTOR_OR_KYC_VS_COMPANY", 0)),
            ("disc_PLACE_OR_BRACKET_ADDED", kind_counts.get("PLACE_OR_BRACKET_ADDED", 0)),
            ("disc_PLACE_VARIANT", kind_counts.get("PLACE_VARIANT", 0)),
            ("disc_P_VS_PRIVATE", kind_counts.get("P_VS_PRIVATE", 0)),
            ("disc_EXTRA_OR_MISSING_WORD", kind_counts.get("EXTRA_OR_MISSING_WORD", 0)),
            ("disc_DIFFERENT_WORD", kind_counts.get("DIFFERENT_WORD", 0)),
            ("fix3_status", "SKIPPED per user — (2) suffixes kept"),
        ],
        columns=["metric", "value"],
    )
    old_sum = sheets.get("SUMMARY", pd.DataFrame(columns=["metric", "value"]))
    sum_df = pd.concat([old_sum, summary_extra], ignore_index=True)

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        discrepancies.to_excel(writer, sheet_name="DISCREPANCIES_TO_DECIDE", index=False)
        cleaned.to_excel(writer, sheet_name="COPY_MAP", index=False)
        sum_df.to_excel(writer, sheet_name="SUMMARY", index=False)
        if "WARNINGS" in sheets:
            sheets["WARNINGS"].to_excel(writer, sheet_name="WARNINGS", index=False)
        if "UNRESOLVED_NOT_FOUND" in sheets:
            sheets["UNRESOLVED_NOT_FOUND"].to_excel(writer, sheet_name="UNRESOLVED_NOT_FOUND", index=False)
        tree.to_excel(writer, sheet_name="FOLDER_TREE", index=False)
        merges.to_excel(writer, sheet_name="SPELLING_MERGES", index=False)
        multi.to_excel(writer, sheet_name="STILL_SEPARATE", index=False)

        ws = writer.sheets["COPY_MAP"]
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        ws.column_dimensions["A"].width = 70
        ws.column_dimensions["B"].width = 40
        ws.column_dimensions["E"].width = 90

        ws2 = writer.sheets["STILL_SEPARATE"]
        ws2.freeze_panes = "A2"
        ws2.auto_filter.ref = ws2.dimensions
        ws2.column_dimensions["A"].width = 18
        ws2.column_dimensions["B"].width = 32
        ws2.column_dimensions["E"].width = 70
        ws2.column_dimensions["H"].width = 90

        ws3 = writer.sheets["SPELLING_MERGES"]
        ws3.freeze_panes = "A2"
        ws3.auto_filter.ref = ws3.dimensions
        ws3.column_dimensions["A"].width = 70

        ws4 = writer.sheets["DISCREPANCIES_TO_DECIDE"]
        ws4.freeze_panes = "A2"
        ws4.auto_filter.ref = ws4.dimensions
        ws4.column_dimensions["A"].width = 12
        ws4.column_dimensions["B"].width = 50
        ws4.column_dimensions["C"].width = 36
        ws4.column_dimensions["G"].width = 90

    cleaned.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    multi.to_csv(CHECK_CSV, index=False, encoding="utf-8-sig")
    merges.to_csv(MERGES_CSV, index=False, encoding="utf-8-sig")
    discrepancies.to_csv(DISC_CSV, index=False, encoding="utf-8-sig")
    print(f"before={before} removed_identical={removed} after_spell_dups={removed_after_spell} after={len(cleaned)}")
    print(f"names_renamed={n_names_merged} canonical={n_canon} still_separate_sources={len(multi)}")
    print(f"still_separate_reasons={reason_counts}")
    print(f"unique_discrepancies={len(discrepancies)} kinds={kind_counts}")
    print(f"wrote {OUT}")
    print(f"wrote {CHECK_CSV}")
    print(f"wrote {MERGES_CSV}")
    print(f"wrote {DISC_CSV}")


if __name__ == "__main__":
    main()
