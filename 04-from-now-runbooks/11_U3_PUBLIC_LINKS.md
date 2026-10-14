# U3 — Public links (optional, C3–C8)

**Who:** `saraswathi.admin` + a **logged-out** browser
**When:** Only if CS says clients may open links **without** a Nextcloud account.
**Do not:** share real MCA/client PDFs. Use `_uat-*` only. Do not paste full link+token in git (record “link created yes”). Do not enable editable public links on production folders.

If CS says **no public links**, write `U3 skipped policy` and go U4.

---

## 0. Turn links on (admin)

1. Administration → **Sharing**.
2. **Allow users to share via link** → **on**.
3. Optional: **Enforce password** on links → **on** (recommended).
4. Optional: **Default expiry** 7 days → **on** if present.
5. **Allow public uploads** → off except for the file-request test.
6. Save.

---

## 1. View link + password + expiry (C3 C4 C5)

1. Files → home → `_restore-drill.txt` (not the 132 GB tree).
2. **⋯** → **Share**.
3. **Share link** / **+ Create a new share link**.
4. Set **Password** (password manager). Do not use the admin login password.
5. Set **Expiry** = tomorrow.
6. Permission: **View** / read. **Allow editing** **off**. **Hide download** if you will test C6.
7. Copy link to a notepad **locally only**.

**Logged-out window:**

1. Paste link. Must ask **password**.
2. Wrong password → fail. Right password → file visible.
3. Do not stay logged in as admin in that window.

---

## 2. Disable download (C6)

1. Same link: enable **Hide download** / disable download if the toggle exists.
2. Logged-out: can view/preview; **Download** button missing or fails.
3. If the toggle does not exist: record **no hide-download**.

---

## 3. Revoke (C10)

1. Admin Sharing → trash/X on that link.
2. Logged-out: refresh the same URL → **not found** / access denied.

---

## 4. File request (C8) — dummy folder only

1. Create `Firm/Templates/_uat-request`.
2. Share link → **File drop** / **Upload only** / **File request** (wording varies).
3. Password optional.
4. Logged-out: can **upload** a tiny txt. Cannot see other files in Templates.
5. Admin: file arrived in `_uat-request`.
6. Revoke the request link when done.

---

## 5. Editable public link (C7) — skip unless CS insists

If you must: only `_uat-office` copy, expiry 1 day, password on, then revoke. Never on Archive.

---

## 6. Expiry check (C4)

If you cannot wait until tomorrow: set expiry to **today** / 1 hour if the UI allows. After that, logged-out link fails. If the UI only has dates, record “expiry set; not yet elapsed” and re-check next day.

**If the date is stuck on today:** that is often the picker, not a broken share.

1. Open **⋯ → Share** → the link → **Expiration date**.
2. Click the **> ** month arrow (or year) — today is the **minimum**, not the only day.
3. Pick **tomorrow** or a date next week. Do not only click today’s number.
4. If a clock/time exists, set a future time today (e.g. +2 hours).
5. Administration → **Sharing**: if **Default expiration** / **Enforce expiration** is **0 days**, the UI cannot move past today. Set default **7** (or 30). Save. Open the share again.
6. Timezone is **Asia/Kolkata**. Do not dump `config.php`.

Record `U3 expiry set: yes` only after the field shows a **future** date. `no` = picker still today after the 7-day default.

S3 files: if Share on Backup_data has no expiry/permissions, that is section 6 of U2 (Enable sharing), not this date picker.

---

## Paste / record

```
U3 skipped policy: yes
U3 password gate: yes
U3 expiry set: no 
U3 hide download: yes
U3 revoke: yes
U3 file request upload-only: yes
```

Next: [12_U4_SMTP.md](12_U4_SMTP.md)
