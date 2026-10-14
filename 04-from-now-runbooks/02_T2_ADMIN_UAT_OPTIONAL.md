# T2 — Optional admin tests (still no extra users)

**Who:** `saraswathi.admin`  
**When:** After T1. Skip any row that already passed in G–Z.  
**Do not:** create users, public links, video calls, File → Export PDF, 132 GB.

These close remaining **admin-only** feature codes. Anything that needs a second person is in Phase U.

---

## AF. Print path (B10) — one try

1. Files → Firm/Templates → open `_uat-office`.
2. Near filename: **File** (Collabora) → **Print**.
3. Browser print dialog: **Save as PDF** or **Cancel**. Do not need a physical printer.
4. Close editor.

**Pass:** print dialog appears.  
**Fail:** no Print, or editor freeze (close after 2 min).

---

## AG. Editor comments (B7) — one try

1. Still in `_uat-office` (or reopen).
2. Select the word `uat` if present, or type `uat` and select it.
3. Insert comment (speech-bubble / **Insert** → **Comment**). Text: `uat-doc-comment`.
4. Close and reopen. Confirm comment still there.

**Pass:** comment persists.  
**Fail:** no comment UI (CODE limits). Record and continue.

---

## AH. Track changes (B6) — one try

1. `_uat-office` → **Edit** → **Track Changes** / **Record changes** (wording varies).
2. Type `x` somewhere. See a marked change.
3. If the menu is missing, record **no track-changes**.

**Pass:** redline visible or honest missing. Do not accept/reject if unsure.

---

## AI. Contacts vCard (E12)

1. Apps → **Contacts**.
2. Open `_uat-contact` (created in Q).
3. **⋯** on the contact → **Export** / **Download vCard** if present.
4. Confirm a `.vcf` downloads. Do not import a huge address book.

**Pass:** vcf downloads or **no export**. Continue either way.

---

## AJ. Tasks due/priority (E14)

1. Apps → **Tasks**.
2. Open `_uat-task`.
3. Set **due** tomorrow and **priority** High (or a star).
4. Confirm both show.

**Pass:** due + priority.  
**Fail:** no fields.

---

## AK. Time Manager hours (F10) — only if client exists

1. Apps → **Time Manager**.
2. If `_uat-client` is listed: add **one** time entry 15 minutes, note `uat`.
3. If the page is 500 / blank: record **TM error** (known leftover). Do not vendor-patch.

**Pass:** entry listed **or** known error recorded.

---

## AL. Talk extras without video (D6, D7, D9)

1. Talk → room `_uat-room`.
2. Attach a tiny file (or send `_restore-drill.txt` if attach from Files exists) — skip if attach is hard.
3. Send emoji or react to `uat-talk`.
4. Reply to that message if **Reply** exists.
5. Do **not** start a call.

**Pass:** at least message still works; extras yes/no each.

---

## AM. Dark/light (M4)

1. Click your avatar (top-right) → **Appearance** / **Settings**.
2. Switch **Dark** then back to **Light** (or leave Dark if you prefer).
3. Confirm the Files page restyles.

**Pass:** theme changes.

---

## AN. Health overview (K11) — look only

1. Avatar → **Administration settings** (gear, admin only).
2. **Overview**.
3. Note warnings. Do **not** click suggested “fix” that installs apps or changes PHP.
4. Talk HPB missing = expected. Collabora hardware warnings = expected.

**Pass:** page opens. Write warning count, not a fix.

---

## Skip in T2 (need later phases)

| Code | Why skip |
|---|---|
| A8 full-text | No indexer yet |
| A14 external mount | Not needed |
| B5 co-author | Needs two users |
| C* shares | Needs users / policy |
| D3–D5 calls | No HPB; skip video |
| H4 password policy | Do in U1 before creating users |
| H11 ClamAV | Not installed |
| F9 board share | Needs users |

---

## Paste / record

```
T2 AF print dialog: yes/no
T2 AG doc comment: yes/no
T2 AH track changes: yes/no/missing
T2 AI vCard: yes/no export
T2 AJ task due+priority: yes/no
T2 AK TM hours: yes / TM error
T2 AL talk attach/react/reply: yes/no each
T2 AM theme: yes/no
T2 AN overview warnings: (count or list short)
```

Next: [03_M0_FREEZE_SOURCE.md](03_M0_FREEZE_SOURCE.md)
