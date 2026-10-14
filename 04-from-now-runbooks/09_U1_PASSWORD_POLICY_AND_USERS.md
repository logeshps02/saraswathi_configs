# U1 — Password policy + create users

**Who:** `saraswathi.admin` in the browser.
**When:** After **M1** proven. Prefer after M2. Do **not** wait for 132 GB if you only need accounts.
**Do not:** email passwords in chat/git. Do not create users on a 30 GB disk if they will sync the full tree. Do not Apply RDS OS. Do not SMTP yet (U4). Extra users were deferred until groups existed — groups **already exi	st**.

Quotation: **10 accounts** (5 permanent + 5 rotating trainees). Adjust names with CS. Do not invent personal data in git.

Suggested IDs (change if CS already named them):

| Username             | Group                |
| -------------------- | -------------------- |
| `saraswathi.admin` | Firm-Admins (exists) |
| partner1, partner2   | Firm-Partners        |
| senior1              | Firm-Seniors         |
| junior1              | Firm-Juniors         |
| trainee1 … trainee5 | Firm-Trainees        |

Use real usernames CS provides. **Never** put real passwords in RESULTS_SHEET.

---

**Wrong place:** Personal settings (only your profile). You need **Administration settings** (gear, whole-server).
**Users are not** under Administration → Security. They are a **separate app**.

---

## 1. Password policy (H4) before creating users

1. Login `saraswathi.admin`.
2. Avatar (top-right) → **Administration settings** (not Personal).
3. Left column under **Administration**: **Security**.
4. Scroll to **Password policy** (app `password_policy`). Set if present:
   - Minimal length **10** (or 12)
   - Enforce upper / lower / numeric if checkboxes exist
   - Forbid common passwords if listed
5. **Brute-force / Session** may **not** appear as those words on Hub 26. That is OK.
   - Brute-force protection is usually **already on** (built-in). Do not hunt for “H5”. Do not disable any “Brute-force” / “Password reset” switch if you do see it.
   - Session idle timeout is often **not** on this page. Do **not** set anything to 1 minute. Skip if missing.
6. Click **Save** only if a button is shown; many fields auto-save.

**Verify:** refresh Security; length still 10+. If **Password policy** block is missing entirely: Apps → search `Password policy` → enable → return here. Do not invent extra security apps.

---

## 2. Sharing policy (defaults, before users share)

Still **Administration settings** (same gear).

1. Left: **Sharing** (under Administration, near Security / Additional). If the left list is long, scroll. Not “Share” inside Files.
2. You will **not** see every old label. Match **meaning**:

| Old runbook text                                          | What Hub 26 often shows                                 | Set                                     |
| --------------------------------------------------------- | ------------------------------------------------------- | --------------------------------------- |
| Allow apps to use the Share API                           | Allow apps to use the Share API                         | leave**on**                       |
| Allow username autocompletion                             | Allow username autocompletion… / address book          | **on**                            |
| Restrict users to only share with members of their groups | Restrict users to only share with users in their groups | **off** unless CS wants isolation |
| Allow public uploads                                      | Allow public uploads                                    | **off** until U3                  |
| Allow users to share via link                             | Allow users to share via link and email                 | **off** until U3 if CS unsure     |
| Exclude groups from creating links                        | Exclude groups from creating link shares                | skip if links off                       |

3. Save if shown.

If **Sharing** is not in the left list: you are on **Personal** settings. Back → avatar → **Administration settings**. If still missing: Apps → **Share** / `files_sharing` must be enabled (it already is if you can share folders).

---

## 3. Create one user first (K1)

**Users is not** Administration → Security / Sharing.

1. Top of the page: **app menu** (grid / nine dots, left of Files).
2. Open **Users** or **Accounts** (people icon). Direct URL: `https://files.t-saraswathi.in/settings/users`
3. If that app is missing: Apps → search **User maintenance** / **Users** → enable. Do not enable LDAP.
4. On the Users page: **New user** (top, or empty Login + Password row + **Create**).
5. Username: e.g. `partner1` (lowercase, no spaces).
6. Display name: as CS wants.
7. Password: password manager only. **Do not screenshot. Do not paste here.**
8. Email: skip until U4 (no SMTP yet).
9. Groups: **Firm-Partners** only. Do **not** tick `admin`.
10. Quota: **5 GB** until they are told not to sync 132 GB locally (S3 Backup_data does not fill this the same way).
11. **Create**.

**Verify:**

1. **Log out** admin (or use a private window).
2. Login `partner1` + password.
3. Files home is empty or default. They must **not** see other people’s private home.
4. They should **not** see Administration settings.
5. Log out. Login admin again.

If login fails: Administration → Users → user → reset password. Still no password in chat.

---

## 4. Create the rest

Repeat step 3 for each remaining account. One private-window login **spot-check** is enough for a second user (e.g. `trainee1`).

**CSV bulk (K2):** Administration → Users → **Download CSV** / **Upload** if the button exists. Only if CS gives a sheet. Do not invent emails.

**Disable test (K5):** on a **trainee** test account only: Users → **⋯** → **Disable**. Private window login must fail. **Enable** again if that account is real.

---

## 5. Groups check (K3)

Administration → Users → **Groups** (or filter).

| Group         | Expected         |
| ------------- | ---------------- |
| Firm-Admins   | saraswathi.admin |
| Firm-Partners | partner accounts |
| Firm-Seniors  | senior accounts  |
| Firm-Juniors  | junior accounts  |
| Firm-Trainees | trainee accounts |
| Firm-Departed | empty            |

Do not add staff to built-in `admin` except the real admin.

---

## Paste / record

```
U1 min password length: pass
U1 brute-force left on: yes
U1 public links default: on
U1 first extra user login: yes
U1 users created count: pass
U1 groups filled as planned: yes
U1 disable test: yes 
```

Do not list passwords.
Next: [10_U2_GROUP_SHARES.md](10_U2_GROUP_SHARES.md)
