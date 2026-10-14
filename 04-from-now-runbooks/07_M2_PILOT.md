# M2 — Pilot folder (mandatory before 132 GB)

**Who:** `saraswathi.admin` on Windows + Nextcloud **desktop client**  
**When:** After M1C (small upload into **Backup_data** worked).  
**Do not:** browser-drag the 132 GB tree. Do not sync the whole source onto the 30 GB disk. Do not create extra users yet (optional later). Do not File → Export PDF. Do not grow EBS.

Pilot size: **tens or hundreds of MB**, mixed PDF/DOCX/XLSX, one nested folder. Not tens of GB. Bytes must land in **S3** via `/Backup_data/_pilot`.

---

## 1. Choose the pilot set on the PC

1. Create a **copy** folder on the PC, e.g. `C:\NC-PILOT\` (not inside the 132 GB tree).
2. Copy into it:
   - 1 nested subfolder (2–3 levels)
   - 1 PDF
   - 1 DOCX
   - 1 XLSX
   - 1 image (jpg/png) if you have one
   - 1 TXT
3. Properties on `C:\NC-PILOT`: write **size, files, folders**.
4. Target in Nextcloud: **`Backup_data/_pilot`** (S3 mount). Do **not** use `Firm/Templates/_pilot` (that is the 30 GB disk).

---

## 2. Install Windows desktop client

1. Browser: https://nextcloud.com/install/#install-clients → **Windows**.
2. Install. Do not enable random extra folders yet.
3. Open **Nextcloud** client.
4. **Log in** → server `https://files.t-saraswathi.in` (https, no trailing path).
5. Browser window: login `saraswathi.admin` + password + MFA if asked.
6. **Grant access**.
7. Account: **skip** syncing the entire home. Choose **manual** / add folder later.

If the client asks to sync everything, **Cancel** that folder pair.

**App password:** if the client creates one, store it in your password manager only. Never paste it here or in git.

---

## 3. Create landing folder in Files (on S3)

1. Browser Files → **Backup_data** (root mount from 19).
2. **+** → **New folder** → `_pilot`.
3. Confirm empty `_pilot` exists inside Backup_data.

---

## 4. Sync only the pilot (client)

The **Activities** window (`No synchronisation configured`) is **not** the place to add a folder. Account name greyed out there is normal. Do **not** click Activity rows.

### 4.1 Open Settings (not Activities)

1. Close or ignore **Activities**.
2. Find the Nextcloud icon in the Windows **system tray** (bottom-right, near the clock). Click the **^** chevron if the icon is hidden.
3. **Right-click** the Nextcloud cloud icon → **Settings…** (or **Open main dialog**).
4. If nothing opens: Start menu → type `Nextcloud` → open **Nextcloud**. You should get a window with the account `saraswathi.admin` @ `files.t-saraswathi.in` and a button **Add Folder Sync Connection** (or **Add folder**).

### 4.2 Add one pair only

1. Click **Add Folder Sync Connection** / **Add folder**.
2. Local folder: `C:\NC-PILOT` (the small copy, **not** `F:\Final`).
3. Remote: browse to **`Backup_data` → `_pilot`**. Path must be `/Backup_data/_pilot`.
   - Do **not** pick `/` (home).
   - Do **not** pick `Firm` or `Firm/Templates`.
4. Confirm. Wait until the client shows **Up to date** / green.

If a file fails, note the name. Do not delete the remote `_pilot`. Do not add a second pair for 132 GB.

### 4.3 If 30 MB looks “too slow”

This path is **file-by-file** (client → Nextcloud → S3), not a single disk copy. Tens of MB with **many small files** can take **10–30+ minutes**. That is not a reason to grow EBS or dump into the S3 console.

**Still working (leave it):**

- Tray icon / Settings: a filename changes, or `x / y` files increases.
- Browser Files → Backup_data/`_pilot`: new files appear on refresh.
- No red error on the pair.

**Stuck (stop and ask):**

- Same filename for **15 minutes** with **0 bytes** moving.
- Client red / paused / “network error” / 507 / 413.
- You accidentally pointed at `F:\Final` or whole home.

**Do not:** cancel and add 132 GB. Do not browser-drag the tree. Do not grow disk.

**Smaller pilot (only if stuck or thousands of tiny files):**

1. Pause or **Remove folder sync connection** for that pair (files already in `_pilot` can stay).
2. Make `C:\NC-PILOT` **5–10 files**, **under ~10 MB total** (1 nested folder + PDF + DOCX + XLSX + TXT).
3. Re-add local `C:\NC-PILOT` → remote `/Backup_data/_pilot`.
4. Wait **Up to date**, then do section 5.

M2 pass is **structure + open/save/search/trash**, not speed. 132 GB will also be slow; the client must stay on `/Backup_data`, never the 30 GB home.

---

## 5. Verify in the browser (in depth)

Do these **in order**. Tick RESULTS_SHEET.

### 5.1 Structure

1. Files → Backup_data/`_pilot`.
2. Nested subfolder names match the PC (spelling, spaces).
3. File count: count rows vs Properties files (tolerance: excluded `~$` files).

### 5.2 Open / preview

1. Click the **PDF** → preview or download. Preview is a pass; download if preview missing.
2. Click the **image** if present → thumbnail or preview.
3. Click the **DOCX** → Collabora opens. Close (X). Do not Export PDF.
4. Click the **XLSX** → opens. Close.
5. Click the **TXT** → editor or download. Content matches.

### 5.3 Save-as PDF (known working path)

1. Open the pilot DOCX.
2. **Save as** near the **filename** → PDF.
3. Confirm a PDF appears in `_pilot` or Downloads.
4. Do **not** use File → Export → PDF.

### 5.4 Filename search (not full-text A8)

1. Files top **magnifying glass**.
2. Type a unique pilot filename (without extension if needed).
3. Result lists that file.

### 5.5 Trash + restore (one file only)

1. In `_pilot`, **⋯** on the TXT → **Delete**.
2. Files left **Deleted files**.
3. Select that TXT → **Restore**.
4. Back in `_pilot`, file is back.

### 5.6 Activity / details

1. Click the restored TXT row.
2. Sidebar **Details**: size/date.
3. **Activity**: delete/restore events (may take a minute).

### 5.7 Optional WebDAV smoke (G12)

Windows Explorer or WinSCP:

- URL: `https://files.t-saraswathi.in/remote.php/dav/files/saraswathi.admin/`
- User: `saraswathi.admin`
- Password: account password **or** app password (never paste).

If 401: use app password (Settings → Security → New app password). Do not log the password.

**Pass:** you can list `Firm`. Disconnect. Full tree is **not** this step.

---

## 6. Client after pilot

Leave the `_pilot` pair **Up to date**. Do **not** add the 132 GB folder yet.

---

## Paste / record

```
M2 pilot size / files / folders: 
M2 client logged in: yes/no
M2 remote path: /Backup_data/_pilot
M2 structure match: yes/no
M2 PDF preview or download: yes/no
M2 DOCX open: yes/no
M2 XLSX open: yes/no
M2 Save-as PDF: yes/no
M2 filename search: yes/no
M2 trash+restore: yes/no
M2 WebDAV list Firm: yes / skip
```

**Exit M2:** all yes (WebDAV skip allowed).  
Next: [08_M3_FULL_UPLOAD.md](08_M3_FULL_UPLOAD.md)
