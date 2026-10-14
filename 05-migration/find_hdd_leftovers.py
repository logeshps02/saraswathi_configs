"""Find previous COPY_FAILED_AND_MISSING sources on D:\\OFFICE SARASWATHI."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(r"D:\OFFICE SARASWATHI")

EXACT = [
    ROOT / r"2024-25\SEARCH AND STATUS REPORT\ADR PLASTICS PRIVATE LIMITED-03.06.2024",
    ROOT / r"2017-18\UPLOADED FORMS\MARCH-18\Uploaded on 28 & 29.03.2018 CONCRETIA ROCK PRODUCTS PRIVATE LIMITED- MGT-14 & SH-7",
    ROOT / r"2017-18\UPLOADED FORMS\OCTOBER-17\Uploaded on 10.10.17 GEOMEO INFORMATICS PRIVATE LIMITED-AOC-4",
    ROOT / r"2024-25\RESOLUTIONS\1.BANK ACCOUNT OPENING RESOLUTIONS\MYSTEVA SOLAR GREEN ENERGY PRIVATE LIMITED",
    ROOT / r"2024-25\RESOLUTIONS\2.GST RESOLUTIONS\MYSTEVA SOLAR GREEN ENERGY PRIVATE LIMITED-GST RESOLUTION",
    ROOT / r"2017-18\UPLOADED FORMS\SEPTEMBER-17\Uploaded on 04.09.2017 ONDEOS TECHNOLOGIES PRIVATE LIMITED-MGT-14",
    ROOT / r"2022-23\UPLOADED FORMS\4.JULY\UPLOADED ON 07.07.2022- PALANIYAPPAN  MURUGESAN FOR KIRUBA SUSTAINABLE AGRICULTURE FARMERS PRODUCER COMPANY LIMITED- DIR-3",
    ROOT / r"2017-18\UPLOADED FORMS\FEBRUARY-18\Uploaded on 23.02.2018 P S N SPINNERS PRIVATE LIMITED-RUN FORM-RAJANARAYANA CORPORATE SERVICES PRIVATE LIMITED-RUN Form",
    ROOT / r"2024-25\UPLOADED FORMS\2.MAY 2024\UPLOADED ON 03.05.2024 PRIDE INDIA PROPERTIES PRIVATE LIMITED &AMBIKA WOODS PRIVATE LIMITED&UMIYA TIMBER PRIVATE LIMITED WEB KYC",
    ROOT / r"2025-26\UPLOADED FORMS\4. JULY 2025\UPLOADED ON 03.07.2025 PRIDE INDIA PROPERTIES PRIVATE LIMITED &AMBIKA WOODS PRIVATE LIMITED&UMIYA TIMBER PRIVATE LIMITED KYC WEB",
    ROOT / r"2017-18\UPLOADED FORMS\AUGUEST-17\Uploaded on 24.08.2017QUADRATIC STRUCTURE INDIA PRIVATE LIMITED-MGT-14",
    ROOT / r"2017-18\UPLOADED FORMS\SEPTEMBER-17\Uploaded on 01.09.2017 SKYWING HOLIDAYS PRIVATE LIMITED-AOC-4",
    ROOT / r"2017-18\UPLOADED FORMS\AUGUEST-17\Uploaded on 18.08.2017 SKYWING HOLIDAYS PRIVATE LIMITED AOC-4",
    ROOT / r"2017-18\UPLOADED FORMS\OCTOBER-17\Uploaded on 06.10.17&07.10.17 SRI YANNARKAY SERVICERS LTD-MGT-7",
    ROOT / r"2024-25\UPLOADED FORMS\3.JUNE 2024\UPLOADED ON 14.06.2024 SWAMIYARMADAM RATHNA MEMORIAL HOSPITAL PRIVATE LIMITED AND RATHNA FERTILITY CENTRE INDIA PRIVATE LIMITED",
    ROOT / r"2024-25\UPLOADED FORMS\5.AUGUST 2024\UPLOADED ON 23.08.2024 SWAMIYARMADAM RATHNA MEMORIAL HOSPITAL PRIVATE LIMITED AND RATHNA FERTILITY CENTRE INDIA PRIVATE LIMITED",
]

KEYWORDS = [
    "ADR PLASTICS PRIVATE LIMITED-03.06.2024",
    "CONCRETIA ROCK PRODUCTS",
    "GEOMEO INFORMATICS",
    "GREEN WEALTH AGRO",
    "PALANIYAPPAN",
    "KIRUBA SUSTAINABLE",
    "MYSTEVA SOLAR",
    "ONDEOS TECHNOLOGIES",
    "P S N SPINNERS",
    "RAJANARAYANA",
    "PRIDE INDIA PROPERTIES",
    "UMIYA TIMBER",
    "QUADRATIC STRUCTURE",
    "SKYWING HOLIDAYS",
    "YANNARKAY",
    "SWAMIYARMADAM RATHNA",
    "RATHNA FERTILITY",
]


def likely_trees() -> list[Path]:
    trees: list[Path] = []
    if not ROOT.is_dir():
        return trees
    for year in ROOT.iterdir():
        if not year.is_dir():
            continue
        try:
            children = list(year.iterdir())
        except OSError:
            continue
        for child in children:
            if not child.is_dir():
                continue
            n = child.name.upper()
            if any(x in n for x in ("UPLOADED", "SEARCH", "STATUS", "RESOLUTION")):
                trees.append(child)
    chennai = ROOT / "CHENNAI OFFICE BACK UP"
    if chennai.is_dir():
        try:
            years = list(chennai.iterdir())
        except OSError:
            years = []
        for year in years:
            if not year.is_dir():
                continue
            try:
                children = list(year.iterdir())
            except OSError:
                continue
            for child in children:
                if child.is_dir() and "UPLOADED" in child.name.upper():
                    trees.append(child)
    return trees


def main() -> None:
    print("EXACT PATHS:")
    for p in EXACT:
        print(("  OK  " if p.is_dir() else "  --  ") + str(p))

    trees = likely_trees()
    print(f"\nLIKELY TREES ({len(trees)}):")
    for t in trees:
        print(" ", t)

    hits: dict[str, list[str]] = {k: [] for k in KEYWORDS}
    for tree in trees:
        try:
            walker = tree.rglob("*")
        except OSError:
            continue
        for p in walker:
            if not p.is_dir():
                continue
            name = p.name.upper()
            for k in KEYWORDS:
                if k.upper() in name and len(hits[k]) < 15:
                    hits[k].append(str(p))
    print("\nKEYWORD HITS:")
    for k, paths in hits.items():
        print(f"\n== {k} ({len(paths)}) ==")
        for x in paths:
            print(" ", x)


if __name__ == "__main__":
    main()

