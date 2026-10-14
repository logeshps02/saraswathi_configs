# U5 — Desktop, mobile, WebDAV (G1–G12 subset)

**Who:** one **Partner** PC and optionally one phone. Not admin-only.  
**When:** After U1. After U2 if they should see Firm shares.  
**Do not:** sync the full 132 GB to a laptop with a small disk. Use **selective sync**. Do not paste app passwords.

Admin already used the desktop client in M2. This file is for **staff**.

---

## 1. Browser (G1)

1. Chrome or Edge: https://files.t-saraswathi.in
2. Login `partner1`.
3. Open a shared Templates file. Logout.

**Pass:** HTTPS padlock, login, Files load.

---

## 2. Windows client (G2) — Partner

1. Install Nextcloud Windows client (same as M2).
2. Server `https://files.t-saraswathi.in`. Login `partner1`. Grant access.
3. **Do not** sync entire account.
4. **Choose what to sync:** tick **Firm/Templates** only (and Trainee-Workspace if testing trainee).
5. Untick Archive / Clients if those are huge.
6. Wait Up to date for Templates.
7. In Explorer, open the Nextcloud folder → Templates → open `_partner-write.txt` or a small file.
8. Create `from-pc.txt` locally in that folder. Client syncs. Browser as partner: file visible.

**Virtual files (G9):** if the client offers “Use virtual files”, you may enable it on a small laptop. Confirm a file **downloads on open**.

**Selective sync (G10):** confirmed by unticking Archive.

**Bandwidth (G11):** client settings → Network → limit if present. Optional.

---

## 3. WebDAV (G12) — Partner

1. Partner: avatar → **Settings** → **Security** → **New app password**. Name `dav-pc`. Copy once to password manager.
2. WinSCP (not Map network drive first). New site:

| Field | Set |
|---|---|
| File protocol | **WebDAV** |
| Encryption | **TLS/SSL Implicit encryption** |
| Host name | **type** `files.t-saraswathi.in` (21 chars, no `https://`, no paste) |
| Port | **443** |
| User name | `partner1` |
| Password | **app password** (not the login password) |

3. **Edit** → **Advanced** → **Environment** → **Directories** → **Remote directory** (type, do not paste):

`/remote.php/dav/files/partner1/`

4. Save. Login. List folders. Disconnect.

**If error is** `Could not resolve hostname` **and the name looks like** `â€‹files.t-saraswathi.inâ€‹` **or extra dots:** that is **zero-width space** from paste, not DNS down. Clear Host. **Type** `files.t-saraswathi.in`. Do not change NS or the `files` A record.

**If 405 Method Not Allowed:** WinSCP probed `/` or used GET (login page is not DAV). Do **not** change nginx. Recheck:

- Remote directory is **not** empty and **not** `/`
- Path is `/remote.php/dav/files/partner1/` (username matches the login)
- Port **443**, Implicit TLS (not 80)
- Retry with Remote directory `/remote.php/webdav/` (legacy)

If still 405: **Cyberduck** (G12 allows it) — Protocol WebDAV (HTTPS), Server `files.t-saraswathi.in`, Port 443, Path `/remote.php/dav/files/partner1/`. Or record `U5 WebDAV: skip WinSCP 405` — Windows **desktop client already pass** is enough for staff files. Do not open port 22.

---

## 4. Android or iOS (G5/G6) — optional one device

1. Play Store / App Store: **Nextcloud**.
2. Server URL `https://files.t-saraswathi.in`. Login partner or trainee.
3. Browse Templates. Download one small file. Upload a photo to **Trainee-Workspace** only if testing trainee (G7 auto-upload: enable later, pick a folder, do not flood Clients).
4. **Offline** (G8): pin one file; enable airplane mode; file still opens; turn network back on.

**Push (D13/N3):** needs Google/Apple push + Talk. If no notification, record **no push** until U4/Talk configured. Not a blocker for files.

---

## 5. macOS / Linux (G3/G4)

Skip unless a user has those machines. Same server URL and selective sync.

---

## Paste / record

```
U5 partner browser: yes/no
U5 partner Windows selective Templates: yes/no
U5 from-pc.txt round-trip: yes/no
U5 virtual files: yes/skip
U5 WebDAV list: yes/no
U5 Android/iOS: yes/skip
U5 offline pin: yes/skip
```

Next: [14_U6_FEATURE_UAT_WITH_USERS.md](14_U6_FEATURE_UAT_WITH_USERS.md)
