# From Home — Phase 7 admin UAT batch 2 (one paste)

G–K are **done**. Extra users still deferred. Do **L–P** as `saraswathi.admin`. One reply. Do not share. Do not Apply RDS OS.

## L. Copy / move (A16)

1. Files → home → `_restore-drill.txt`.
2. **…** → **Copy** → destination **Firm/Templates**.
3. Confirm a copy exists in Templates (name may be `_restore-drill (copy).txt` or similar).
4. Do **not** delete the original in home.

## M. Preview (A6)

1. Open **Firm/Templates** → `_uat-office` (the Office file).
2. Confirm it opens in Office (already proven) **or** Files preview thumbnail is visible.
3. Also click `_restore-drill.txt` and confirm the text preview / editor opens.

Either thumbnail or open-to-read is a pass.

## N. PDF (B13 path, open only)

1. **Firm/Templates** → **New** → **New file** / upload is not required.
2. If **New** has no PDF: skip create. Instead open **LibreSign** app from the top apps menu.
3. Confirm LibreSign page loads (no need to sign a document).

Pass = LibreSign UI opens. Do not generate a CA. Do not sign.

## O. Calendar event (E1)

1. Open **Calendar**.
2. New event `_uat-event` today (any 30 min slot) → Save.
3. Confirm it appears on the calendar.

Do not add attendees (no extra users / no SMTP).

## P. Deck board (F1) — clicks

1. Top app menu (grid / more apps) → **Deck**. URL becomes `/apps/deck/`.
2. If you see an empty intro: **Create a new board** / **+** / **Add board**.
3. Title: `_uat-board`. Colour: any. **Create** / **Add**.
4. Click the board name `_uat-board` so the columns view opens.
5. If there is no column: **Add stack** / **+ Add list** / empty column title box. Type `Todo`. Enter.
6. In the **Todo** column: **Add card** / **+**. Title `_uat-card`. Enter.
7. Confirm `_uat-board` is in the left board list and `_uat-card` sits under **Todo**.

Do not share the board. Do not add members.

## Paste once

- L copy in Templates yes/no
- M preview/open yes/no
- N LibreSign UI yes/no
- O calendar event yes/no
- P Deck board + card yes/no

### Observed (2026-08-26)

| Item | Result |
|---|---|
| L copy | **working** |
| M preview/open | **working** |
| N LibreSign UI | **working** |
| O calendar event | **working** |
| P Deck | operator asked for clicks |

### Confirmed P (2026-08-26)

P **yes** — `_uat-board` / `Todo` / `_uat-card`. L–P complete.

## Stop

Batch 2 is complete. Do not create users. Do not share. Do not invite attendees. Do not Apply RDS OS. Leave `_uat-*` objects. Next is `FROM_HOME_NEXT_STEP_PHASE7_ADMIN_UAT3.md`.
