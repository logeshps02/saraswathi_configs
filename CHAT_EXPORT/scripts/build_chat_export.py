"""Build a complete export of everything created and used in this chat.

Produces:
    C:\\Users\\logsarav\\Downloads\\CHAT_EXPORT\\
        ALL PROGRAMS.docx      - all Python scripts consolidated
        CHAT SUMMARY.docx      - narrative of the whole chat
        README.txt             - index of what's in the folder
        scripts\\               - copy of every .py file
        workbooks\\             - Excel input + latest output + review
        pdfs\\                  - final quotation + feature PDFs
        source_lists\\          - the two folder-listing text files
"""
import os
import shutil
import glob
import subprocess
import sys
from datetime import datetime

DL = r"C:\Users\logsarav\Downloads"
OUT = os.path.join(DL, "CHAT_EXPORT")

# Ensure python-docx installed
try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    print("Installing python-docx ...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx",
                           "--quiet", "--disable-pip-version-check"])
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

os.makedirs(OUT, exist_ok=True)
for sub in ("scripts", "workbooks", "pdfs", "source_lists"):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)


def safe_copy(src, dst_dir):
    if not os.path.exists(src):
        return False
    name = os.path.basename(src)
    dst = os.path.join(dst_dir, name)
    try:
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print(f"  [SKIP] {name}: {e}")
        return False


print("=" * 70)
print("Collecting files ...")
print("=" * 70)

# 1) SCRIPTS -- every .py in Downloads
print("\n[1/4] Python scripts:")
scripts_copied = []
for py in sorted(glob.glob(os.path.join(DL, "*.py"))):
    if safe_copy(py, os.path.join(OUT, "scripts")):
        scripts_copied.append(os.path.basename(py))
        print(f"  ok  {os.path.basename(py)}")

# 2) WORKBOOKS -- original + final version + review
print("\n[2/4] Excel workbooks:")
workbook_files = [
    "BACKUP WORK - FINAL SHEET.xlsx",              # original input
    "BACKUP WORK - FINAL SHEET - WITH PATHS.xlsx",  # v1
    "BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx",  # latest
    "NOT FOUND - REVIEW.xlsx",
]
# Also copy every intermediate version we still have
for xl in sorted(glob.glob(os.path.join(DL, "BACKUP WORK - FINAL SHEET*.xlsx"))):
    workbook_files.append(os.path.basename(xl))
workbooks_copied = []
for name in dict.fromkeys(workbook_files):  # unique, preserve order
    src = os.path.join(DL, name)
    if safe_copy(src, os.path.join(OUT, "workbooks")):
        workbooks_copied.append(name)
        print(f"  ok  {name}")

# 3) PDFs
print("\n[3/4] PDFs:")
pdf_files = [
    "Quotation for Secure Cloud Document Management System.pdf",
    "Secure Cloud Document Management & Collaboration Platform Feature Document.pdf",
]
pdfs_copied = []
for name in pdf_files:
    src = os.path.join(DL, name)
    if safe_copy(src, os.path.join(OUT, "pdfs")):
        pdfs_copied.append(name)
        print(f"  ok  {name}")

# Also copy the .md sources if present
for md in glob.glob(os.path.join(DL, "*Cloud Document*.md")):
    if safe_copy(md, os.path.join(OUT, "pdfs")):
        pdfs_copied.append(os.path.basename(md))
        print(f"  ok  {os.path.basename(md)}")
for md in glob.glob(os.path.join(DL, "Quotation*.md")) + glob.glob(os.path.join(DL, "Feature*.md")):
    if safe_copy(md, os.path.join(OUT, "pdfs")):
        pdfs_copied.append(os.path.basename(md))
        print(f"  ok  {os.path.basename(md)}")

# 4) SOURCE LISTINGS (the folder inventories)
print("\n[4/4] Source folder listings:")
list_files = [
    "all_files_list (2).txt",
    "all_files_list_2025_26.txt",
]
lists_copied = []
for name in list_files:
    src = os.path.join(DL, name)
    if safe_copy(src, os.path.join(OUT, "source_lists")):
        lists_copied.append(name)
        print(f"  ok  {name}  ({os.path.getsize(src)/(1024*1024):.1f} MB)")


# =============================================================
# Build ALL PROGRAMS.docx
# =============================================================
print("\n\nBuilding ALL PROGRAMS.docx ...")

# Order scripts logically -- fix sequence first, then supporting utils
FIX_ORDER = [
    "fix_mismatches.py",       # v6 - A.M.N. JEWELLERS
    "fix_group_leaks.py",      # v7 - ARAS group leaks
    "fix_extras_scope.py",     # v8 - deep-path scoping
    "fix_drive_filter.py",     # v9 - strict CO/OS filter
    "recheck_nf.py",           # v12 - fuzzy NF recheck
    "build_review.py",         # NOT FOUND review workbook
]
# Then anything else
tail = [s for s in scripts_copied if s not in FIX_ORDER]
ordered_scripts = [s for s in FIX_ORDER if s in scripts_copied] + sorted(tail)


def set_run_font(run, name="Consolas", size=8.5, color=None, bold=False):
    run.font.name = name
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor(*color)
    run.bold = bold
    # East Asia font
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:cs"), name)
    rPr.append(rFonts)


doc = Document()
# Cover
h = doc.add_heading("Backup-Sheet Path Matching — All Programs", level=0)
p = doc.add_paragraph()
r = p.add_run(f"Consolidated Python source code for every script created in the chat.\n")
r.font.size = Pt(11)
r = p.add_run(f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}\n")
r.font.size = Pt(10)
r.font.color.rgb = RGBColor(0x60, 0x60, 0x60)
r = p.add_run(f"Total scripts: {len(ordered_scripts)}")
r.font.size = Pt(10)
r.font.color.rgb = RGBColor(0x60, 0x60, 0x60)

doc.add_heading("Table of contents", level=1)
for i, name in enumerate(ordered_scripts, 1):
    doc.add_paragraph(f"{i}.  {name}", style="List Number")

doc.add_page_break()

for name in ordered_scripts:
    src = os.path.join(OUT, "scripts", name)
    doc.add_heading(name, level=1)
    # Short description block
    src_bytes = os.path.getsize(src)
    p = doc.add_paragraph()
    r = p.add_run(f"File size: {src_bytes:,} bytes\n")
    r.font.size = Pt(9); r.font.color.rgb = RGBColor(0x60, 0x60, 0x60)
    # Code content
    try:
        with open(src, "r", encoding="utf-8", errors="replace") as f:
            code = f.read()
    except Exception as e:
        code = f"[Could not read file: {e}]"
    for line in code.splitlines() or [""]:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(line if line else " ")
        set_run_font(r, size=8.5)
    doc.add_page_break()

doc.save(os.path.join(OUT, "ALL PROGRAMS.docx"))
print(f"  saved: ALL PROGRAMS.docx")


# =============================================================
# Build CHAT SUMMARY.docx - narrative of the whole session
# =============================================================
print("\nBuilding CHAT SUMMARY.docx ...")

sdoc = Document()
sdoc.add_heading("Backup-Sheet Path Matching + Cloud Migration Proposal", level=0)
p = sdoc.add_paragraph()
r = p.add_run(f"Session summary\n")
r.font.size = Pt(11); r.bold = True
r = p.add_run(f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}")
r.font.size = Pt(10); r.font.color.rgb = RGBColor(0x60, 0x60, 0x60)

# ---- Section 1: Path-matching workstream ----
sdoc.add_heading("1. Excel path-matching workstream", level=1)

p = sdoc.add_paragraph(
    "Goal: match ~11,000 rows in BACKUP WORK - FINAL SHEET.xlsx (a CS/CA "
    "audit firm's records) to actual folder paths on drives E: and F:."
)

p = sdoc.add_paragraph(
    "Approach: (1) index every folder in the client's two source listings "
    "(all_files_list (2).txt = 43 MB CO drive listing; all_files_list_2025_26.txt "
    "= 6.6 MB current-FY listing); (2) parse each row's combine (Year > Month > "
    "CO/OS > optional extras); (3) tokenise the company name; (4) match tokens "
    "against child-folder names within the year+month scope; (5) filter by drive."
)

sdoc.add_heading("Iterations delivered", level=2)
iters = [
    ("(6).xlsx  — fix_mismatches.py",
     "Fixed A.M.N. JEWELLERS bug: dot-separated initials A.M.N. were being "
     "dropped by a <3-char filter, leaving only 'JEWELLERS', which then matched "
     "every jewellery company. Solution: canonicalize() collapses A.M.N. -> AMN "
     "before tokenisation."),
    ("(7).xlsx  — fix_group_leaks.py",
     "Fixed ARAS group cross-contamination. Sister companies (ARAS ENTERPRISES, "
     "ARAS AUTOMOTIVE, ARAS LOGISTICS, ARAS PVPV MOTORI) were leaking into each "
     "other via first-token fallback on the shared 'ARAS' prefix. Solution: "
     "disable first-token fallback for multi-token companies, and remove the "
     "4-char prefix loose match."),
    ("(8).xlsx  — fix_extras_scope.py",
     "Fixed deep-path scoping. Combines like '2025-26>CO>OTHER WORKS>CERTIFIED "
     "FORMS>ARUNKUMAR SIR' were returning every A.M.N. folder in the year. "
     "Solution: parse extras into distinctive tokens (CERTIFIED, ARUNKUMAR) "
     "skipping COMMON_EXTRAS (OTHER, WORKS, FORMS, SIR, CS, CASES, ...), and "
     "require every distinctive token to appear in the candidate path."),
    ("(9).xlsx  — fix_drive_filter.py",
     "Enforced strict CO/OS drive filtering. Rows marked CO must live under "
     "E:\\BACK UP FOLDER\\... or E:\\2025-26\\co\\...; rows marked OS must live "
     "under F:\\... or E:\\2025-26\\os\\.... Any path on the wrong drive is "
     "dropped. Verified zero mixed-drive leaks after the pass."),
    ("(10)/(11)/(12).xlsx  — recheck_nf.py",
     "Re-checked every NOT FOUND row against ONLY its specific month/drive "
     "folder using: (a) expanded stopwords (LLP, LLC, PARTNERS, INDIA, YOU, "
     "P, L); (b) compound-token splitter (PRIVATELIMITED -> PRIVATE LIMITED, "
     "PVTLTD, INDIAPRIVATE); (c) Damerau-Levenshtein typo tolerance (catches "
     "DAIRY vs DIARY adjacent-swap typos, and DESING vs DESIGN); "
     "(d) tightened initials-glue to 1-2 letter tokens only, so 'AND YOU LLP' "
     "(three 3-letter English words) no longer gets merged into a single token. "
     "Result: 346 of 964 NOT FOUND rows recovered."),
]
for title, body in iters:
    sdoc.add_heading(title, level=3)
    sdoc.add_paragraph(body)

sdoc.add_heading("Final counts (workbook (12))", level=2)
table = sdoc.add_table(rows=1, cols=3)
hdr = table.rows[0].cells
hdr[0].text = "Sheet"
hdr[1].text = "Rows"
hdr[2].text = "NOT FOUND remaining"
for c in hdr:
    for p in c.paragraphs:
        for r in p.runs:
            r.bold = True
for row in [
    ("UPLOADED FORMS - COMPANY NAME", "5,467", "122"),
    ("COMPANY WISE", "5,792", "496"),
    ("LEI AND OTHERS", "24", "0"),
    ("Total NOT FOUND rows for review",  "-",  "618"),
]:
    cells = table.add_row().cells
    for i, v in enumerate(row):
        cells[i].text = v

sdoc.add_heading("Review workbook (NOT FOUND - REVIEW.xlsx)", level=2)
sdoc.add_paragraph(
    "For every remaining NOT FOUND row we generated a review workbook that "
    "lists every folder inside the row's specific (year > month > CO/OS) path. "
    "13,994 candidate rows across the 618 NOT FOUND source rows. The client "
    "puts an 'X' in the SELECT column for correct matches; those selections are "
    "then merged back into the main workbook."
)

# ---- Section 2: Cloud proposal workstream ----
sdoc.add_page_break()
sdoc.add_heading("2. Cloud Document Management proposal", level=1)

sdoc.add_paragraph(
    "Second workstream: drafted a full commercial proposal to migrate the firm "
    "from local hard drives to a secure cloud-hosted document platform."
)

sdoc.add_heading("Solution shape", level=2)
sdoc.add_paragraph(
    "Nextcloud (open-source enterprise document platform) hosted on Amazon Web "
    "Services in the Mumbai region (ap-south-1). 10 user accounts, 150 GB "
    "migrated, browser + desktop + mobile access, full per-user audit trail, "
    "3-layer backup (Trash + S3 versioning + Glacier archive). All data resident "
    "in India."
)

sdoc.add_heading("Commercial summary", level=2)
table = sdoc.add_table(rows=1, cols=2)
hdr = table.rows[0].cells
hdr[0].text = "Line item"
hdr[1].text = "Amount"
for c in hdr:
    for p in c.paragraphs:
        for r in p.runs:
            r.bold = True
for row in [
    ("One-time professional services (to Logesh P S)", "Rs 40,000"),
    ("Domain registration (annual, to registrar)", "Rs 1,000"),
    ("Monthly AWS infrastructure (pass-through)", "Rs 5,200 - 6,200"),
    ("Month 1 total outlay", "Rs 47,200"),
    ("Month 2 onwards (with 1-year Reserved Instance)", "Rs 5,200/month"),
    ("5-year total (approximate)", "Rs 3,57,000"),
]:
    cells = table.add_row().cells
    for i, v in enumerate(row):
        cells[i].text = v

sdoc.add_heading("Documents delivered", level=2)
sdoc.add_paragraph("Quotation for Secure Cloud Document Management System.pdf  (17 pages)", style="List Bullet")
sdoc.add_paragraph("Secure Cloud Document Management & Collaboration Platform Feature Document.pdf  (14 pages, 166 features across 15 categories)", style="List Bullet")

sdoc.add_heading("Alternatives evaluated on request", level=2)
alts = [
    ("Cyberduck",
     "Free S3/WebDAV desktop transfer client. Fine for admin bulk-migration; "
     "not a document platform — no browser editing, no mobile, no client "
     "sharing links with expiry/password, no per-user audit."),
    ("Mountain Duck",
     "Paid (~Rs 3,300/user one-time) sibling of Cyberduck that mounts S3 as "
     "a drive letter. Nicer UX for staff but same platform gaps."),
    ("rclone",
     "Free CLI tool. Best-in-class for migration, backup, and Glacier archives — "
     "already planned as an internal tool during delivery. Not a user-facing "
     "platform."),
    ("Google Workspace Business Standard",
     "Rs 736/user/mo + 18% GST = ~Rs 8,140/mo for 10 users; ~Rs 34,000/year more "
     "than Nextcloud from Year 2. Wins on real-time co-authoring, Meet video "
     "calls, Gmail included. Loses on data residency (India-only guarantee only "
     "at Enterprise tier ~Rs 2,340/user/mo), audit-log retention (only 6 months "
     "without paid Vault), long-term archive, file-request links, and vendor "
     "lock-in via Google Docs proprietary format."),
    ("S3 folder URLs",
     "S3 has no real folders — only object keys with shared prefixes. Object "
     "URLs work for a single file; there is no folder URL. That gap is exactly "
     "why the proposal wraps S3 with Nextcloud."),
]
for title, body in alts:
    sdoc.add_heading(title, level=3)
    sdoc.add_paragraph(body)

# ---- Section 3: Docs reviewed / other help ----
sdoc.add_page_break()
sdoc.add_heading("3. Other assistance provided", level=1)
for pt in [
    "Reviewed both PDFs cover-to-cover before dispatch. Flagged: "
    "(a) Section 6.3 Reserved-Instance math off by Rs 300/mo (savings should "
    "be Rs 1,330/mo, not Rs 1,000); "
    "(b) feature-count mismatch — Quotation says 150+, Feature Doc says 130+, "
    "actual = 166; "
    "(c) Section 7 numbering skips 7.5 (goes 7.4 -> 7.6).",
    "Drafted a polite 4-day follow-up email to the client (with a shorter "
    "2-line variant and a WhatsApp variant).",
    "Confirmed both IOS-XR router login sessions (Black-Bolt-BNG on "
    "10.127.60.41:2049, superluminal-BNG on 10.127.59.20:2043).",
]:
    sdoc.add_paragraph(pt, style="List Bullet")

# ---- Section 4: File inventory ----
sdoc.add_page_break()
sdoc.add_heading("4. Files in this export folder", level=1)
sdoc.add_paragraph(f"Location: {OUT}")

sdoc.add_heading("scripts\\", level=2)
for name in ordered_scripts:
    sdoc.add_paragraph(name, style="List Bullet")

sdoc.add_heading("workbooks\\", level=2)
for name in workbooks_copied:
    sdoc.add_paragraph(name, style="List Bullet")

sdoc.add_heading("pdfs\\", level=2)
for name in pdfs_copied:
    sdoc.add_paragraph(name, style="List Bullet")

sdoc.add_heading("source_lists\\", level=2)
for name in lists_copied:
    sdoc.add_paragraph(name, style="List Bullet")

sdoc.save(os.path.join(OUT, "CHAT SUMMARY.docx"))
print(f"  saved: CHAT SUMMARY.docx")


# =============================================================
# README.txt
# =============================================================
readme = f"""CHAT EXPORT — {datetime.now().strftime('%d %B %Y, %H:%M')}
================================================================

This folder contains a complete export of the work done in the chat
session: source scripts, input & output Excel workbooks, PDFs of the
cloud-migration proposal, and the original folder-inventory files.

Contents
--------

ALL PROGRAMS.docx
    Every Python script consolidated into one Word document, in the
    order of the fix-sequence:  fix_mismatches -> fix_group_leaks ->
    fix_extras_scope -> fix_drive_filter -> recheck_nf -> build_review.

CHAT SUMMARY.docx
    Narrative summary of the whole session — what problem each script
    solved, iteration outputs, review workbook design, cloud proposal
    commercials, alternatives evaluated (Cyberduck / Mountain Duck /
    rclone / Google Workspace), and the file inventory.

scripts\\
    Copy of every .py file created in Downloads ({len(scripts_copied)} files).

workbooks\\
    - BACKUP WORK - FINAL SHEET.xlsx                        (original input)
    - BACKUP WORK - FINAL SHEET - WITH PATHS.xlsx           (first pass)
    - BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx      (latest / recommended)
    - NOT FOUND - REVIEW.xlsx                               (tick 'X' to select)
    - Every intermediate version (5-9) kept for audit trail

pdfs\\
    - Quotation for Secure Cloud Document Management System.pdf
    - Secure Cloud Document Management & Collaboration Platform Feature Document.pdf
    - Original .md source files if present

source_lists\\
    - all_files_list (2).txt          43 MB CO-drive folder listing
    - all_files_list_2025_26.txt      6.6 MB current-FY folder listing

Statistics
----------
Scripts copied     : {len(scripts_copied)}
Workbooks copied   : {len(workbooks_copied)}
PDFs / MDs copied  : {len(pdfs_copied)}
Source lists       : {len(lists_copied)}
"""
with open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8") as f:
    f.write(readme)
print(f"  saved: README.txt")

print("\n" + "=" * 70)
print(f"DONE.  Export folder: {OUT}")
print("=" * 70)
