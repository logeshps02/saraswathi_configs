# U6 — Feature UAT that needs extra users

**Who:** `saraswathi.admin` + `partner1` + `trainee1` (two browsers / private windows)
**When:** After U2. SMTP optional.
**Do not:** video without HPB. Do not full-text A8 without indexer. Do not File → Export PDF. Do not sign production PDFs. Do not impersonate without recording it.

Do these as **batches**. One paste each into RESULTS_SHEET. Stop a batch if a **security** fail (wrong user sees Partners).

---

## Batch U6-A — Sharing leftovers

| Code | Clicks                                                                                               | Pass                   |
| ---- | ---------------------------------------------------------------------------------------------------- | ---------------------- |
| C1   | Already in U2 partner write                                                                          | yes recorded           |
| C2   | Already in U2 group share                                                                            | yes recorded           |
| C10  | Already revoke test                                                                                  | yes recorded           |
| C12  | Partner: Files left**Shares** / avatar → **Sharing** overview if present                | list of shares visible |
| N5   | Admin: comment`@partner1` on `_restore-drill.txt` (Comments tab). Partner bell or comment thread | mention visible        |
| N6   | Partner: Settings →**Notifications**. Toggle one item off/on                                  | page saves             |

**Skip:** C3–C8 unless U3 done. C9 mail unless U4 done. C11 federated (another Nextcloud) — skip forever unless CS has one.

```
U6-A share overview: yes/
U6-A @mention: yes
U6-A notification prefs: yes
```

---

## Batch U6-B — Co-authoring (B5 B6 B7)

Use a **copy**, not the only original.

1. Admin: Files Templates → copy `_uat-office` to `_uat-coauthor.docx`.
2. Confirm Templates is **Edit** for Firm-Partners.
3. Admin opens `_uat-coauthor.docx` in Collabora (window 1).
4. Partner opens the **same file** (window 2).
5. Admin types `A`. Partner types `B` in another paragraph.
6. Each should see the other’s cursor or text within ~10s.
7. Partner: Insert **Comment** `partner-c`. Admin sees it.
8. If **Track changes** exists, Partner types `z` with it on; Admin sees mark.
9. Both close.

**Pass:** both can type; text from both remains on reopen.
**Fail:** second user read-only / CODE crash / one session kicks the other. Record; Collabora on t3a.medium may struggle (known hardware warnings).

```
U6-B both edit same doc: yes
U6-B other cursor or live text: yes
U6-B in-doc comment: yes
U6-B track changes: yes
```

---

## Batch U6-C — Deck / Calendar / Talk with two users

### Deck (F3 F6 F7 F9)

1. Admin Deck `_uat-board` → **Share board** → group Firm-Partners or user partner1. Edit.
2. Partner: Apps → Deck → `_uat-board` visible.
3. Partner: open `_uat-card` → **Assign** partner1. Add comment `p`. Attach a file from Templates if **Attach** exists.
4. Admin sees assign + comment.

### Calendar (E2 E7 E8 E9)

1. Admin Calendar → **New calendar** `Firm-Deadlines` → Share with Firm-Partners **Edit** or View.
2. Partner: calendar appears. Create event `_partner-cal` on it (if Edit) or admin creates and partner views.
3. Event: **attach** a small file if UI allows.
4. **Talk room from event** if button exists — create. Do **not** start video.
5. Attendees: add partner1. Skip if it requires mail and SMTP is down.

### Talk (D1 D2 D6)

1. Admin Talk: 1:1 chat with partner1. Message `uat-d1`.
2. Partner replies.
3. Attach a small file in chat.
4. Do **not** Call.

```
U6-C deck share+assign+comment: yes/no
U6-C shared calendar: yes/no
U6-C talk 1:1: yes/no
U6-C talk file drop: yes/no
```

---

## Batch U6-D — Admin user ops (K)

1. **Quota (K4):** Users → trainee1 → quota 1 GB. Save. (Raise again after test.)
2. **Password reset (K6):** reset trainee1 in admin UI. Trainee logs in with new password (password manager). Then set a final password CS keeps.
3. **Impersonation (K8):** Users → partner1 → **Impersonate** if present. Banner “impersonating”. Open Files. **Switch back**. Administration → **Logging** / Activity: impersonation event if shown (J14).
4. **Disable (K5):** already in U1; skip if done.
5. **Apps (K10):** Administration → **Apps**. Do **not** disable `files`, `richdocuments`, `dav`. Look only.
6. **Logging (K12):** Administration → **Logging**. Page opens. Do not rotate/download huge logs into git.

```
U6-D quota set: yes
U6-D password reset login: yes
U6-D impersonate + switch back: yes
U6-D logging page: yes
```

---

## Batch U6-E — Audit (J) light

1. As partner: download one file.
2. Admin: **Activity** app (top) filter user partner1 if filter exists (J6).
3. File sidebar Activity on that file (J9).
4. Administration **Logging** or Activity **CSV** if **Export** exists (J10). Save CSV **locally**. Do not commit CSV with names if CS objects — then record “export yes, not stored in git”.

CloudTrail (J11/J12) already enabled — do not change.

```
U6-E activity by user: yes
U6-E file activity: yes
U6-E CSV export: yes
```

---

## Batch U6-F — LibreSign sample (B13) not production

1. Copy a **blank** 1-page PDF to Templates `_uat-sign.pdf` (not MCA forms).
2. Apps → **LibreSign**.
3. Request signature as admin on that PDF. Draw signature. Complete if the wizard allows.
4. If accounts/certificates missing: record **UI only** (N in L–P already did UI). Do not generate keys into git.

```
U6-F sample PDF signed: yes 
```

---

## Stop U6 — still later (see 15)

Video D3–D5 D14 D15, full-text A8, ClamAV H11, E2E folders H3, Glacier I9, branding M1–M3, Talk HPB.

**Phase U exit:** U1 users exist, U2 matrix verified both sides, U5 partner client selective sync, U6-B attempted, known defects listed.

Handover (training) is **after** U, not in these files. DR: [../02-architecture/DR_RUNBOOK.md](../02-architecture/DR_RUNBOOK.md).
