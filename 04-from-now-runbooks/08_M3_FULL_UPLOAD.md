# M3 — Full 132 GB upload

**Who:** `saraswathi.admin` + Windows Nextcloud client on office broadband  
**When:** After M2 all yes. M0 source `F:\Final` (~132 GB). Remote = **`/Backup_data`** (S3 mount). Disk stays 30 GiB.  
**Do not:** browser zip/drag the tree. Do not S3 console upload. Do not stop/start EC2 mid-sync (public IP may change; not EIP). Do not Apply RDS OS. Do not create 10 users mid-copy. Do not grow EBS. Do not sync onto `/` home or `Firm/`.

This will **not** finish in minutes. M0 is **~179k files / ~41k folders / ~132 GB**. The desktop client sends **one object at a time** through Nextcloud to S3 (same path as the 30 MB pilot). Expect **1–4+ days** on typical office broadband, longer if most files are tiny. Leave the PC on **power + network**. Pause only if CloudWatch disk ALARM or the pair is on `/` home.

**Do not** try to “make it as fast as a USB copy”:
- Do not grow EBS to 200 GiB
- Do not S3 console / `aws s3 sync` the tree (Files will not show those as Nextcloud folders)
- Do not browser-drag 132 GB
- Do not enable `objectstore` in `config.php`

Speed-ups that **are** allowed later if M2 passes: keep **one** pair on `/Backup_data/Final`; exclude `~$*` / `Thumbs.db` / `*.tmp`; run overnight; if the client crawls on tens of thousands of tiny files, **split** `F:\Final` into a few large subfolder pairs (still all under `/Backup_data/Final/...`), never onto the 30 GB disk.

---

## 1. Freeze source

1. Tell the firm: no edits on the source disk until you say delta is done.
2. Re-check Properties: size / files / folders vs M0. If it grew a lot, update RESULTS_SHEET.
3. Note start date/time IST.

---

## 2. Remote parent (already the S3 mount)

1. Login `saraswathi.admin`.
2. Open **Backup_data**. This **is** the M0 landing (`Firm/Backup_data` meant this S3 folder, not a second tree on the 30 GB disk).
3. Optional: **+** → **New folder** `Final` if you want `F:\Final` contents under `Backup_data/Final`. Default: sync **into Backup_data** so files sit next to `_pilot` — or create `Final` and sync there so `_pilot` stays separate. **Prefer** remote `/Backup_data/Final` (empty).
4. Do **not** create `Firm/Backup_data` on local disk.

Do not upload into `Templates/_pilot` or home.

---

## 3. Add sync pair (client)

1. Nextcloud client (already logged in from M2).
2. **Add fo`F:\Final` (M0 source; ~132 GB).
4. Remote = `/Backup_data/Final` (or `/Backup_data` if you skipped the Final subfolder). Browse; confirm you are **not** on `/` or `/Firm`
4. Remote = the empty folder from step 2 (browse; confirm path).
5. **Virtual files / on-demand:** prefer **full sync of this pair only** for the server copy. You do **not** need a second copy on another PC.
6. Exclude if the client has ignore:
   - `~$*`
   - `Thumbs.db`
   - `desktop.ini`
   - `*.tmp`
7. Start.

---

## 4. Watch (do not babysit every file)

Every few hours:

1. Client: not paused; errors list.
2. Browser: remote folder **size growing** (Details on the folder if shown).
3. CloudWatch **disk** alarm should stay OK (30 GiB OS). If ALARM, **pause client** and ask — something is writing to EBS by mistake.
4. S3 size grows in S3 console (Metrics / total size). Do not open every object. Do not dump from the console.
5. Budget $60: storage cost rises during M3; that is expected. Do not create a third budget.

**If the client shows a red banner** `SAVEPOINT DOCTRINE_2 does not exist` **or** `Something went wrong on the server` **while upload still runs:** that is a **short MySQL/RDS glitch** during many S3 file writes, not a bad URL and not “the 132 GB is gone.” Do **not** Remove the pair. Do **not** delete local or **Backup_data**. Do **not** Apply RDS OS. Do **not** grow EBS. Do **not** enable objectstore.

1. Leave the window. If a progress bar is still uploading, let it continue.
2. Tray → **Pause** → wait 2 minutes → **Resume**.
3. Failed rows: ⋯ → **Retry**. Green folders already on the server stay.
4. Browser: open **Backup_data** (or `Data`) — files that finished are already on S3.
5. If the same SQL SAVEPOINT repeats for 30+ minutes: **Pause** the client (do not Remove pair). RDS `db.t4g.micro` is small; thousands of file creates in parallel can throw `SAVEPOINT DOCTRINE_2`. Ask Copilot. SSM (`sh`, one line). Do not paste file lists. Do not Apply RDS OS. Do not grow EBS.

```sh
sudo -u www-data php /var/www/nextcloud/occ status ; echo OCC:$?
```

```sh
df -h / /opt/nextcloud/data ; echo DF:$?
```

```sh
systemctl is-active nginx php8.3-fpm redis-server ; echo SVC:$?
```

```sh
sudo grep -oE 'SAVEPOINT[^"]{0,80}|SQLSTATE[^"]{0,80}|Connection refused|Too many connections' /opt/nextcloud/data/nextcloud.log | tail -n 8 ; echo SQLLOG:$?
```

**Pass (live 2026-09-02):** `installed: true` 34.0.3, disk **31%** (8.7G / 29G — was 7.7G; watch, do not grow), nginx/php/redis **active**. SQLLOG is SAVEPOINT only (not Too many connections). RDS `db.t4g.micro` cannot take the whole `Data` tree at once.

Keep **Pause** until you change client limits. Then:

1. Client **Settings** (not Activities) → **Network** → limit **upload** (start **200–500 KB/s**).
2. If the client has parallel / multi-connection upload: **off** or **1**.
3. Prefer **one** company folder under `Data` (not the entire tree). Green folders already on S3 — do not re-upload those.
4. **Resume**. If SAVEPOINT returns, Pause again and drop to **one folder** only.
5. Do not Remove pair. Do not Apply RDS OS. Do not grow EBS. Do not upgrade RDS class without asking (cost).

If the client says **disconnected**:

1. Browser: can you still open https://files.t-saraswathi.in ?
2. If instance was rebooted: check EC2 **public IPv4**. If it changed, Route 53 **A** record `files` only — **never** NS / delete zone. Then wait DNS. Ask if unsure.
3. Resume client. Chunked upload should continue (A3/A4).

---

## 5. When client is Up to date

### 5.1 Counts

On PC, Properties of source again.

In Nextcloud: folder **⋯** → **Details** if item counts exist. Do **not** `find` 132 GB on the 30 GB disk.

Record:

- Source files / folders / bytes
- Failed list from client (export if the client allows)
- Retry those files once (right-click retry)

### 5.2 Spot-check 10 files

Pick 10 from **different subfolders** (not only the first folder):

For each: browser locate → **Download** or **Open**. Pass = opens or downloads.

Include at least: 2 PDF, 2 DOCX, 1 XLSX, 1 image if present, 1 deep nested path.

### 5.3 Filename search

Search one unique deep filename. Result found.

### 5.4 One trash drill on a **copy**

Do **not** delete a unique original.

1. Copy one small TXT inside the tree to `_m3-trash-probe.txt` in the same folder.
2. Delete probe → Deleted files → Restore.
3. Confirm back.

### 5.5 Office on one real DOCX

Open one **non-critical** DOCX. Close. Save-as PDF near filename if you want. Skip Export PDF.

---

## 6. Delta (if source changed)

1. If anyone edited the disk during the run: **resume** client once more until Up to date.
2. Record delta date.

---

## 7. After M3

- Leave the sync pair running if the PC is the office archive PC.
- If this PC must not keep a second copy: after verification, you may **remove the folder sync** on the PC (files **stay on the server**). Removing the pair should **not** delete remote if you choose “delete local only”. Read the dialog twice. If it says delete server files — **Cancel**.

**Wrong way:** delete `F:\Final` (or `C:\NC-PILOT`) **while the pair is still connected**. Two-way sync will delete the same files in Nextcloud/S3. Always **remove the sync connection first**, confirm remote still listed in the **browser**, then delete local.

---

## 8. FAQ — local delete, browser drag, extra folders

### Why not browser-drag 132 GB

Browser upload is one POST (max **512M** here), no good resume, tab/timeouts, and it would hammer PHP on t3.medium. The **desktop client** chunks and can resume. Staff **may** drag **small** files in the browser later (invoices, one PDF). That is not the 132 GB job.

### Delete local after sync — yes

1. Client **Up to date**.
2. Browser: files still in **Backup_data** (or `Final`).
3. Client: **Remove folder sync connection**.
4. Dialog: keep files on **server**. If it offers to delete server copies — **Cancel**.
5. Then delete or keep the local folder.

**If the client or Explorer says `Delete folder: failed`:** the pair is still active, or Windows has files locked. Do **not** delete **Backup_data** in the browser (that is the S3 mount). Do **not** delete the 132 GB on the server to “free the PC.”

1. Tray Nextcloud → the folder row → **⋯** → **Remove folder sync connection** (wording may be Pause / Remove). Choose **keep files on the server**. Never “delete server files.”
2. Quit the Nextcloud client (tray → **Quit Nextcloud**, not only close the window).
3. Explorer: delete the **local** folder only (the PC copy). If still locked: reboot PC, quit client, delete again.
4. Browser: **Backup_data** must still list files.

If they meant delete **in Files** (cloud): stop. Removing the mount folder or `Final` on S3 is not a local-disk cleanup. Ask before any cloud delete of M3 data.

Users later: they do **not** need a full local copy. Browser, mobile, or client with **virtual files / choose what to sync**.

### Users drag-and-drop later

| They drop into | Where bytes go | OK? |
|---|---|---|
| **Backup_data** (or subfolder) | S3 | Yes — preferred for bulk |
| **Firm/** or Files home | 30 GiB disk | Only small files; will fill the disk |
| Desktop client pair still linked | Both sides | Deleting local deletes cloud |

Issues: 413 if one file > 512M in **browser** (use client); slow many tiny files; if sync still on, local delete = cloud delete; extra users must **not** sync all of Backup_data onto a small laptop.

### Only one S3 folder in Files — extra folders

**Backup_data** is the **only** S3 mount. Everything else (Firm, home) is the 30 GB disk.

- New folder **inside Backup_data** (or `_pilot` / `Final`) = still S3. **No problem.** This is the right way. Files → Backup_data → **+** → **New folder**.
- New folder at Files **root** (next to Backup_data, via **+** in home) = **30 GB disk**, not S3. Small Firm files only. Do not put 132 GB there. That is the only “problem.”
- A **second** External storage row (another top-level S3 name) is possible later. Prefer a **subfolder inside Backup_data** instead. Do **not** add a second row during M3.

### How to add another External storage row (optional, after M3)

This is **not** Files **+ → New folder**. It is a second mount (like `Backup_data`).

**Does it break the current mount?** No, if you **leave row 1** (`/Backup_data`) untouched. Disk stays 30 GiB. AWS bucket name stays the same. Existing files in Backup_data stay.

**What it does change**

| Choice | Effect |
|---|---|
| Same bucket as now | Files shows **two** top-level folders with the **same S3 objects**. Delete/rename in one = same change in the other. Client can double-sync and fight. |
| New empty AWS bucket | Extra S3 cost, extra IAM, extra HeadBucket/config. **Not in the quote.** Do not invent keys. |
| UI paste of bucket/region | Can inject U+200B again → red “not dns compatible”. Use occ if the tick stays red. |

**Clicks (only if CS really wants a second top-level S3 name)**

1. Finish or **pause** M3. Do not add a row mid-copy.
2. Administration settings → **External storage**.
3. **Do not** trash or edit the green `Backup_data` row.
4. Bottom empty **Add storage** row:
   - Folder name: a **new** name (not `Backup_data`). No leading `/`.
   - Storage: **S3-Compatible Object Storage**
   - Authentication: **None**
   - Bucket / hostname / region / path style: same as mount 1 **only if** you accept a duplicate view — otherwise **stop** and ask (new bucket needs IAM first).
   - Type bucket and region **by hand** (no browser paste).
5. Available for: **Firm-Admins** first.
6. **Tick / Save**. Green = OK. Red = do not retry blindly; same occ path as 21, **new ID**, do not `create` another `/Backup_data`.
7. Files: both names at home. Desktop client: **one pair per folder**. Do not map two mounts to the same local path.

**Usually skip this.** New S3 folders = **Backup_data → + → New folder**. That does not need a second row.

### Rename Backup_data (Nextcloud name only)

Do **not** rename the AWS bucket `saraswathi-nextcloud-files-055855670388`.

**A. Rename a subfolder** (e.g. `_pilot` → something else): Files → open **Backup_data** → **⋯** on that subfolder → **Rename**. Fine anytime.

**B. Rename the S3 mount itself** (the top-level name `Backup_data`):

1. Pause / do not start the 132 GB pair first.
2. Administration settings → **External storage**.
3. Row mount **1**: change **Folder name** (e.g. `Archive` or `Final-files`). No space if you can avoid it. No leading `/`.
4. **Tick / Save**. Wait green.
5. Files: old name gone, new name at home. Contents (S3) stay.
6. Desktop client: **remove** the old folder pair, **add** a new pair to `/NewName/...`. Old path `/Backup_data` will 404.

Do **not** use Files **⋯ → Rename** on the mount root if it is greyed out — that is normal for External storage.

Do **not** rename mid-M3. If you want a nicer name, do it **before** adding `F:\Final`. Plan remote stays `/Backup_data/Final` unless you rename first.

Office/PDF: **Save as PDF** missing and **Export PDF** fail are known; do not block M3. Download + print-to-PDF on the PC if a PDF is needed.

---

## Paste / record

```
M3 start IST: 
M3 source files/folders/bytes: 
M3 remote path: /Backup_data/Final (or /Backup_data) 
M3 client Up to date: yes/no
M3 failures (count): 
M3 10 spot-checks: yes/no (list short names)
M3 filename search deep: yes/no
M3 trash probe: yes/no
M3 disk/S3 alarm during copy: OK / ALARM
```

**Exit M3:** Up to date, failures listed, 10 spot-checks yes.  
Users: [09_U1_PASSWORD_POLICY_AND_USERS.md](09_U1_PASSWORD_POLICY_AND_USERS.md) (allowed after M1; safer after M2). Do not wait for M3 if you only need to **create** users — but do not let them sync 132 GB onto 30 GB.
