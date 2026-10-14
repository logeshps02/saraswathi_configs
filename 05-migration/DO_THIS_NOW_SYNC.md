# Do this now — fastest safe sync

**STATUS 2026-09-12: COMPLETE.** `F:\f` → `nextcloud:Backup_data/DATA1` checked: **0 differences, 167861 matching files**. HP may stay off. **Do not run the copy commands in this file again** unless CS adds **new** files. Details: [RCLONE_F_TO_DATA1_COMPLETE.md](RCLONE_F_TO_DATA1_COMPLETE.md) and [SESSION_2026-09_INGEST_BILLING_CLOUDTRAIL.md](../10-change-log/SESSION_2026-09_INGEST_BILLING_CLOUDTRAIL.md).

Do this on the **copy laptop** that has `F:\f`.
Do **not** recopy. Do **not** use S3 console. Do **not** grow EBS.
Do **not** paste passwords in chat.

**Remote:** user later created **`Backup_data/DATA1`** and wants new files there. Do **not** use `Backup_data/DATA` (no bang). `DATA!` is unused unless they say otherwise. Do **not** create `Final_v2`.

If your dest is `D:\f` not `F:\f`, use `D:\f` in every command below.

---

## 0. Stop the slow desktop sync

1. Bottom-right tray → Nextcloud cloud icon.
2. Right-click → **Pause** (every pair).
3. Do **not** click Remove.
4. Leave the PC on power + Wi‑Fi/LAN.

You can resume rclone later; already-uploaded files are skipped.

---

## 1. Confirm remote folder `DATA!` (already exists)

1. Browser: https://files.t-saraswathi.in
2. Login `saraswathi.admin`.
3. Open **Backup_data**.
4. Open **`DATA!`** (name **with** `!`). Do **not** open **`DATA`** (no bang).
5. Confirm you are **not** in `/` home and **not** in `Firm`.
6. New company folders from `F:\f` will be created **inside `DATA!`**. Existing files there stay. rclone copy does not delete them.

---

## 2. Create a Nextcloud app password (click by click)

Do this in the **browser on the copy laptop**. Stay logged in as `saraswathi.admin`.
Do **not** use the normal login password in rclone. Do **not** paste the app password in chat.

1. Open https://files.t-saraswathi.in and log in if needed.
2. Look at the **top-right corner**. Click your **avatar / initials / profile picture**.
3. Click **Personal settings** (sometimes **Settings**).
   - If you landed on Admin settings by mistake, that is the wrong page. Go back and open **Personal**.
4. Left sidebar: click **Security**.
5. Scroll down to **Devices & sessions** (or **App passwords** / **Devices**).
6. Find a small box labelled **App name**.
7. Click in that box and type exactly: `rclone-sync`
8. Click the button **Create new app password** (or **Create**).
9. Nextcloud may ask you to type your **normal login password** again. That is only to prove it is you. Type it and confirm.
10. A new row appears with:
    - Username: `saraswathi.admin` (leave it)
    - A long one-time password (letters/numbers, often with spaces)
11. Click **Copy** if there is a copy icon. If not, select the whole password and Ctrl+C.
12. Open **Notepad** on that PC → Ctrl+V → **File → Save** as `C:\rclone-app-password.txt` if you want, or leave Notepad open.
13. Click **Done** on the Nextcloud page. After Done, Nextcloud will **not** show that password again. If you lose it, create a new app password named `rclone-sync-2`.
14. Do not email it. Do not put it in this chat. Do not use it in the Nextcloud desktop client (desktop already has its own login).

If you cannot find Security:

- Avatar → **Personal settings**
- Left list: look for a shield / **Security** under Personal (not Administration)
- You must be `saraswathi.admin`. A staff user may not see Devices & sessions the same way.

---

## 3. Install rclone on Windows (click by click)

rclone has **no window**. It is one file: `rclone.exe`. You run it from Command Prompt.

### 3.1 Download

1. On the copy laptop, open Chrome/Edge.
2. Go to: https://downloads.rclone.org/rclone-current-windows-amd64.zip
   - That is **Intel/AMD 64-bit**, which almost every office laptop is.
   - If the PC is ARM (rare), use the ARM64 zip from https://rclone.org/downloads/ instead.
3. Wait for the zip to finish. It usually lands in `Downloads`.
4. Open File Explorer → **Downloads**.
5. Find `rclone-current-windows-amd64.zip`.

### 3.2 Extract to `C:\rclone`

1. In File Explorer address bar, click, type `C:\` and press Enter.
2. Right-click empty space → **New** → **Folder**.
3. Name it exactly: `rclone`
4. You now have `C:\rclone` (it is empty).
5. Go back to Downloads. **Right-click** the zip → **Extract All…**
6. Click **Browse**, go to `C:\rclone`, click **Select Folder**, then **Extract**.
7. Open `C:\rclone`. You may see an inner folder like `rclone-v1.xx.x-windows-amd64`. Open that folder.
8. Inside you must see **`rclone.exe`**.
9. Select `rclone.exe` → Ctrl+X. Go up to `C:\rclone` → Ctrl+V.
10. Confirm this path exists: `C:\rclone\rclone.exe`
    - You can ignore README and other files.
11. Do **not** install WinFsp. You are not mounting a drive.

If Windows SmartScreen says “Windows protected your PC”:

1. Click **More info**.
2. Click **Run anyway**.
3. This is expected for a newly downloaded `rclone.exe`.

### 3.3 Open Command Prompt (not PowerShell if you want the exact `C:\rclone\...` lines)

1. Press the **Windows key**.
2. Type: `cmd`
3. Click **Command Prompt** (black window). Do **not** need Run as administrator.
4. Type this line and press Enter:

```bat
C:\rclone\rclone.exe version
```

5. Success looks like:

```
rclone v1.xx.x
- os/version: Microsoft Windows ...
- os/kernel: ...
- os/type: windows
- os/arch: amd64
```

6. Failures:

| What you see | Fix |
|---|---|
| `The system cannot find the path specified` | `rclone.exe` is not at `C:\rclone\rclone.exe`. Search This PC for `rclone.exe` and move it there. |
| `'C:\rclone\rclone.exe' is not recognized` | Same: file missing or still inside the unzipped subfolder. |
| Window flashes and closes | You double-clicked `rclone.exe`. Always run it from Command Prompt as above. |

Keep this Command Prompt open for the next section.

---

## 4. Configure rclone once (every prompt)

You are still in Command Prompt. Desktop Nextcloud stays **Paused**.

### 4.1 Start the wizard

Type this and press Enter:

```bat
C:\rclone\rclone.exe config
```

A text menu appears. You only type the **short answer**, then Enter.
If you type a wrong letter, you can usually finish, then run `config` again and delete the bad remote.

### 4.2 Prompt by prompt

**Prompt 1** — something like:

```
No remotes found, make a new one?
n) New remote
s) Set configuration password
q) Quit config
n/s/q>
```

If remotes already exist, the first lines list them, then `n) New remote`. That is fine.

Type: `n`  
Press Enter.

Do **not** type `s` (that encrypts the whole config and adds another password).

---

**Prompt 2**

```
name>
```

Type: `nextcloud`  
Press Enter.

Use this exact name. The later commands expect `nextcloud`.

If it says that name already exists: type `q`, then in a new config run choose `d` to delete the old `nextcloud` remote, or use `e` to edit it.

---

**Prompt 3** — long list of storage types (`alias`, `amazon cloud drive`, `s3`, …).

```
Storage>
```

1. Scroll the list with the window (or look carefully).
2. Find the line **WebDAV** (it also shows `"webdav"`).
3. Note the **number** on that line (it changes between rclone versions). Example only: `42 / WebDAV`.
4. Type **that number** (or type `webdav`).
5. Press Enter.

Do **not** pick Amazon S3, Nextcloud as a special brand if you do not see WebDAV, or “local”. It must be **WebDAV**.

---

**Prompt 4**

```
URL of http host to connect to
url>
```

Type this **one line**, no extra space at the end, including `https` and the trailing `/`:

```
https://files.t-saraswathi.in/remote.php/dav/files/saraswathi.admin/
```

Press Enter.

Wrong URLs (do not use):

- `https://files.t-saraswathi.in` (missing `/remote.php/dav/files/saraswathi.admin/`)
- `http://...` (must be https)
- A URL that ends with `/Backup_data` (Backup_data is chosen later, not in this URL)

---

**Prompt 5** — vendor list, similar to:

```
 1 / Fastmail Files
 2 / Nextcloud
 3 / Owncloud
 ...
vendor>
```

Numbers can differ. Find **Nextcloud**. Type **that number** (docs often show `2`; if your list is different, use the number next to Nextcloud).

Press Enter.

---

**Prompt 6**

```
User name
user>
```

Type: `saraswathi.admin`  
Press Enter.

---

**Prompt 7**

```
Password.
y) Yes type in my own password
g) Generate random password
n) No leave this optional password blank
y/g/n>
```

Type: `y`  
Press Enter.

---

**Prompt 8** — password is hidden. You will see nothing as you paste. That is normal.

```
Enter the password:
password:
```

1. Open Notepad with the app password.
2. Select the whole password → Ctrl+C.
3. Click the Command Prompt window.
4. Right-click once (or Ctrl+V). The cursor may not move. That is OK.
5. Press Enter.

If the app password has **spaces**, include the spaces. Paste the whole thing.

---

**Prompt 9**

```
Confirm the password:
password:
```

Paste the **same** app password again → Enter.

If it says they do not match: you mistyped. Run config again.

---

**Prompt 10**

```
Bearer token instead of user/pass (e.g. a Macaroon)
bearer_token>
```

Press Enter only (**leave blank**). Do not paste the app password here.

---

**Prompt 11** (newer rclone may ask)

```
Edit advanced config?
y) Yes
n) No (default)
y/n>
```

Type: `n`  
Press Enter.

If it does not ask, skip.

---

**Prompt 12**

```
Keep this "nextcloud" remote?
y) Yes this is OK
e) Edit this remote
d) Delete this remote
y/e/d>
```

Check the summary:

- `type: webdav`
- `url: https://files.t-saraswathi.in/remote.php/dav/files/saraswathi.admin/`
- `vendor: nextcloud`
- `user: saraswathi.admin`
- `pass: *** ENCRYPTED ***`

If any of those is wrong: type `e` and fix.  
If it looks right: type `y` → Enter.

---

**Prompt 13**

```
e) Edit existing remote
n) New remote
d) Delete remote
s) Set configuration password
q) Quit config
e/n/d/s/q>
```

Type: `q`  
Press Enter.

You are back at the normal `C:\...>` prompt.

### 4.3 Test that login works

Same Command Prompt:

```bat
C:\rclone\rclone.exe lsd nextcloud:
```

Wait 10–30 seconds. Success is a list of folders, for example `Backup_data`, `Firm`, maybe others. Names can wrap; that is OK.

Then:

```bat
C:\rclone\rclone.exe lsd nextcloud:Backup_data
```

You must see a line with `DATA!` (and maybe `DATA`). Target is **`DATA!` only**.

| Error | Meaning | What to do |
|---|---|---|
| `401` / Unauthorized / username or password | Wrong user or not the **app** password | New app password. Edit remote: `rclone config` → `e` → `nextcloud` → change password only |
| `couldn't find root directory` / 404 | URL wrong | Must be exactly the `/remote.php/dav/files/saraswathi.admin/` URL |
| timeout / connection refused | No internet or site down | Open https://files.t-saraswathi.in in the browser first |
| `command not found` | You closed cmd or path wrong | Use `C:\rclone\rclone.exe ...` again |

**Do not start the upload until both `lsd` commands work.**

When they work, continue from **section 5** in this file (scripts + `run_parallel_rclone.py`).

### 4.4 Target is `DATA!` (user confirmed)

Config is OK. **Do not** mkdir `Final_v2`. **Do not** copy into `DATA` (no bang).

Optional check that `DATA!` lists:

```bat
C:\rclone\rclone.exe lsd "nextcloud:Backup_data/DATA!"
```

Then go to section 5 / 6. Desktop pair stays Paused.

---

## 5. Fastest path if Python scripts are missing

On the copy laptop, `C:\Users\HP\Downloads\05-migration` does not exist. **Do not wait for those .py files.** rclone is already configured.

Same Command Prompt (`C:\Users\HP\Downloads>`). Desktop Nextcloud stays **Paused**. Target is **`DATA!` only**.

**Proven 2026-09-03:** `F:\f` is **167860 files / 123.5 GiB**. Company folders have files. Empty Nextcloud company folders were from the failed `DATA!` CMD run. User created **`DATA1`**. Use PowerShell. First copy one small company, then the full tree.

**Use PowerShell.** Windows key → type `powershell` → Enter.

```powershell
C:\rclone\rclone.exe size F:\f
C:\rclone\rclone.exe ls F:\f --max-depth 3 | Select-Object -First 30
```

`size` must show thousands of files / tens of GB. If it is tiny, stop.

PowerShell: do **not** use `-P` / `-v` (they can be eaten; window returns immediately). Use `--progress --verbose` and **no** `--log-file` so the bar stays on screen. `--transfers 8` is parallel.

```powershell
C:\rclone\rclone.exe copy F:\f 'nextcloud:Backup_data/DATA!' --transfers 8 --checkers 16 --exclude '_COPY_*.csv' --exclude '_UNSORTED_REORG_LOG.csv' --exclude '_SYNC_*.log' --exclude '~$*' --exclude 'Thumbs.db' --exclude 'desktop.ini' --exclude '*.tmp' --log-file F:\f\_SYNC_RCLONE.log --log-level INFO -v -P --stats 15s
```

Leave it open. You must see `INFO : ... Copied` and Transferred counting **up** (not 1/1 in three minutes). Browser: **DATA!** (not **DATA**). Empty top-level folders from the first run stay; files fill them on this pass.

If SAVEPOINT / many 500 errors: Ctrl+C, wait 2 minutes, run the same command with `--transfers 4` instead of `8`.

Already-uploaded files are skipped on rerun. Do not recopy `F:\f`.

---

## 5b. Put the scripts on that laptop (optional later)

You need these two files next to each other (already in this project):

- `05-migration\run_parallel_rclone.py`
- `05-migration\split_sync_batches.py`

If this project folder is **not** on the copy laptop, copy that whole `05-migration` folder onto it (USB is fine).

Confirm dest exists:

```bat
dir F:\f
```

You should see many company folders. If `F:\f` is missing, try `dir D:\f` and use that path in step 6.

Confirm Python:

```bat
python --version
```

If that fails, try `py --version`. Use whichever works in the next commands.

Confirm rclone is on PATH **or** use the full `C:\rclone\rclone.exe` path. If `rclone` is not found when Python runs, add `C:\rclone` to PATH:

```bat
set PATH=C:\rclone;%PATH%
```

Keep that Command Prompt open. All later commands go in **this** window.

---

## 6. Start the fast upload (this is the parallel step)

Go to the folder that contains the two `.py` files:

```bat
cd /d C:\path\to\05-migration
set PATH=C:\rclone;%PATH%
```

Replace `C:\path\to\05-migration` with the real path.

**Start the real upload** (4 jobs at once, 4 files per job = 16 files in flight):

```bat
python run_parallel_rclone.py --dest F:\f --jobs 4 --transfers 4 --remote "Backup_data/DATA!"
```

If `python` fails:

```bat
py run_parallel_rclone.py --dest F:\f --jobs 4 --transfers 4 --remote "Backup_data/DATA!"
```

Leave this window open. Leave the PC on. This will take **hours to a couple of days**, not minutes. That is still much faster than the desktop client.

You should see lines like:

```
[job 1] OK SOME COMPANY NAME ...
[job 2] OK OTHER COMPANY ...
```

Logs appear as:

- `F:\f\_SYNC_JOB_01.log`
- `F:\f\_SYNC_JOB_02.log`
- `F:\f\_SYNC_JOB_03.log`
- `F:\f\_SYNC_JOB_04.log`

---

## 7. What to do while it runs

Every few hours:

1. Command window still printing `OK ...` lines.
2. Browser → Backup_data → **DATA!** → refresh. New company folders appear. Do not open **DATA** (no bang).
3. Nextcloud desktop stays **Paused**.
4. If the window shows many `FAIL` in a row, or the browser stops growing for 30+ minutes, go to step 8.

Do **not**:

- Close the lid (set power to **never sleep**).
- Start a second copy of the script.
- Turn parallel up past 4 jobs.
- Upload in S3 console.
- Grow the server disk.

---

## 8. If it errors (do this, in order)

### A. `rclone` not found

```bat
set PATH=C:\rclone;%PATH%
```

Run the python command again. Already-done companies are skipped.

### B. Red Nextcloud / `SAVEPOINT DOCTRINE_2` / “Something went wrong on the server”

1. In the Command Prompt: **Ctrl+C** once. Wait until it stops.
2. Wait 2 minutes.
3. Restart **slower**:

```bat
python run_parallel_rclone.py --dest F:\f --jobs 1 --transfers 2 --remote "Backup_data/DATA!"
```

Do **not** Remove the old desktop pair. Do **not** Apply RDS OS. Do **not** grow EBS.

### C. Disk alarm on AWS / server disk filling

Ctrl+C. Stop. Ask before anything else. Files already in `DATA!` stay.

### D. Network drop / PC reboot

Just run the **same** command again. rclone copy skips files already on the server.

---

## 9. When the command finishes

The last line should look like:

```
ok=NNNN fail=0 seconds=....
```

If `fail` is not 0, run the **same** command again once (retries only failures / leftovers).

Then in the browser open 5 company folders inside `DATA!` and confirm files open.

Keep the old Nextcloud pair **Paused** until staff accept the new files in `DATA!`.

---

## Speed you should expect

| Method | Typical |
|---|---|
| Nextcloud desktop (what you had) | 1–4+ days, often idle on tiny files |
| This script (4×4) | often **several times faster** |
| 20 parallel jobs / S3 console | **forbidden** — breaks Nextcloud or RDS |

Office broadband + tens of thousands of small files still take time. Overnight + no sleep is the remaining speed-up.
