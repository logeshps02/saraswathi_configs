# T1 — Admin UAT batch 5 (AA–AE)

**Who:** `saraswathi.admin` in Chrome/Edge at https://files.t-saraswathi.in  
**When:** First. No AWS changes. No users. No 132 GB.  
**Do not:** File → Export → PDF. Do not share. Do not Apply RDS OS.

If AA–AE were already done on 2026-08-30, tick RESULTS_SHEET and skip to T2.

---

## AA. Presentation (B3)

1. Top bar: **Files**.
2. Open **Firm** → **Templates**.
3. Click **+ New** (or **+**).
4. Click **New presentation** / Presentation.
5. Name it exactly `_uat-slides` (no extra spaces). Confirm/Enter.
6. Wait for Collabora to open. If it spins > 2 minutes, close and retry once. If still stuck, record **AA fail: Office hang** and skip to AC (Files still works).
7. Click the first slide. Type `uat`.
8. Close the editor (X). Wait until Files list is back.
9. Click `_uat-slides` again. Confirm the first slide still shows `uat`.

**Pass:** reopen shows `uat`.  
**Fail:** blank, error, or will not open.

---

## AB. Save as ODT (B11) — use filename bar, not File → Export

1. Files → **Firm** → **Templates**.
2. Open `_uat-office` (the Word document from earlier UAT).
3. At the **top**, near the **filename**, find **Save as** / **Save As** (same control that worked for PDF).
4. Do **not** open **File → Export → PDF**.
5. Choose **ODT** / **OpenDocument Text** if listed.
6. If ODT is missing, choose the next **office** format (ODT, DOCX, or DOC). Not PDF for this test (PDF already passed).
7. Confirm. Close the editor.
8. Back in **Templates**, look for a new file e.g. `_uat-office.odt` (name may include “copy”).

**Pass:** new office file visible in Templates. Write the **format** (ODT / DOCX / other).  
**Fail:** only PDF listed, or save never finishes (wait 3 minutes max, then close).

---

## AC. Metadata sidebar (A13)

1. Files → click **Home** / your user home (not Templates).
2. Find `_restore-drill.txt`. Click the **row** once (do not download, do not open).
3. Right sidebar: if closed, click the **info / Details** icon (usually top-right of the file view).
4. Open tab **Details** (or **Activity** then back to Details).
5. Confirm you see **size** and/or **modified** date. Owner may show `saraswathi.admin`.
6. Optional: **Sharing**, **Activity**, **Comments**, **Tags** tabs exist — do not change shares.

**Pass:** size and/or date visible.  
**Fail:** sidebar empty or missing.

---

## AD. File lock (A15)

1. Still on `_restore-drill.txt`.
2. Click **⋯** on that row (three dots).
3. Look for **Lock** / **Lock file**.
4. If **present:** click **Lock**. Confirm a padlock / “Locked by you”. Then **⋯** → **Unlock**. Confirm lock gone. Leave **unlocked**.
5. If **absent:** do not hunt in Settings. Record **no lock menu**.

**Pass:** lock then unlock, **or** honest **no lock menu**.  
**Fail:** lock stuck on (try Unlock again; if still stuck, ask).

---

## AE. Recurring calendar (E4)

1. Top bar app menu (grid) → **Calendar**.
2. Find event `_uat-event`. Click it. If missing, **New event** titled `_uat-recur`, date = tomorrow, time any 1 hour block.
3. In the event editor find **Repeat** / **Does not repeat**.
4. Set **Daily** (or **Weekly** if Daily missing).
5. Do **not** add attendees.
6. **Save**.
7. Confirm the event shows a repeating / recurrence icon or “Every day/week” text. Close.

**Pass:** recurrence visible.  
**Fail:** no Repeat control, or save error.

---

## Paste / record

```
T1 AA slides reopen: yes/no
T1 AB save-as format: ODT / DOCX / none
T1 AC details size/date: yes/no
T1 AD lock: lock+unlock / no lock menu / stuck
T1 AE recurring: yes/no
```

Copy into [RESULTS_SHEET.md](RESULTS_SHEET.md). Next: [02_T2_ADMIN_UAT_OPTIONAL.md](02_T2_ADMIN_UAT_OPTIONAL.md) or skip T2 and go [03_M0_FREEZE_SOURCE.md](03_M0_FREEZE_SOURCE.md).
