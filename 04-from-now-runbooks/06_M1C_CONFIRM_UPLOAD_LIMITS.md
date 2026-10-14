# M1C — Confirm upload limits (after S3 folder proof)

**Who:** `logesh.implementer` SSM + `saraswathi.admin` browser  
**When:** After [20_M1S3_PROOF_FILE.md](20_M1S3_PROOF_FILE.md) all yes. Before the pilot.  
**Do not:** raise limits to 132 GB POST. Desktop client uses **chunks**. 512M is enough for a single chunk/browser file. Do not grow EBS. Do not objectstore.

Live (2026-08-25): PHP `upload_max_filesize` / `post_max_size` **512M**, `max_execution_time` 3600, nginx `client_max_body_size 512M`.

---

## 1. PHP (SSM, one line each)

```sh
php -i | grep -E '^memory_limit|^upload_max_filesize|^post_max_size|^max_execution_time|^date.timezone'
```

**Pass:**

- memory_limit = 512M (or higher)
- upload_max_filesize = 512M
- post_max_size = 512M
- max_execution_time = 3600
- date.timezone = Asia/Kolkata

If missing, do **not** invent new files. The drop-in was `/etc/php/8.3/mods-available/saraswathi-limits.ini`. Ask before rewriting.

```sh
systemctl is-active php8.3-fpm
```

**Pass:** `active`.

---

## 2. nginx body size (SSM)

```sh
sudo grep -n client_max_body_size /etc/nginx/sites-enabled/files.t-saraswathi.in
```

**Pass:** `client_max_body_size 512M;` (or larger).  
Do not paste the rest of the vhost. Do not dump certs.

```sh
sudo nginx -t && echo NGINX_T:$?
```

**Pass:** `syntax is ok` / `successful` and `NGINX_T:0`.

If you changed nothing, skip reload. If you changed a number:

```sh
sudo systemctl reload nginx
```

---

## 3. Nextcloud chunking (browser)

1. Login `saraswathi.admin`.
2. Avatar → **Administration settings** → **Basic settings** or **Additional settings**.
3. Look for max upload. If the UI shows 512 MB or “unlimited via chunking”, that is OK.
4. Do **not** set a 150 GB PHP limit.

---

## 4. Tiny browser upload into Backup_data (not 132 GB, not Templates)

1. Files → **Backup_data** (the S3 mount from 19). **Not** Firm/Templates on the 30 GB disk.
2. **+** → **Upload file**.
3. Pick a small local file (under 10 MB). Name `_m1c-up-small.txt` (UAT names optional).
4. Wait until 100%. Refresh. File listed. **Download** matches.
5. Optional: S3 console — object `_m1c-up-small.txt` exists. Then delete in Files.

**Pass:** small upload works on the **S3 folder**.  
**Fail:** 413 / timeout / 0-byte / file only on disk → stop. Ask with the **error text only**.

---

## 5. Disk / S3 sanity (quotation)

```sh
df -h /opt/nextcloud/data ; echo DFDATA:$?
```

**Pass:** size still **~30G**. Avail does **not** need to be > 132G. Bulk data is S3.

S3 console: bucket `saraswathi-nextcloud-files-055855670388` shows the small upload object (or leftover from proof). Do not dump 132 GB here.

---

## Paste / record

```
M1C php 512M / 3600 / Kolkata: yes/no
M1C php8.3-fpm active: yes/no
M1C nginx client_max_body_size: 512M / other
M1C nginx -t: 0 / fail
M1C small browser upload into Backup_data: yes/no
M1C df still ~30G (bulk is S3): yes/no
```

**Exit M1:** S3 folder proven + 512M + small upload into Backup_data.  
Next: [07_M2_PILOT.md](07_M2_PILOT.md)
