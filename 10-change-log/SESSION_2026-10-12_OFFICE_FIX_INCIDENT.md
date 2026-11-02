# Incident Report: Nextcloud Office (Collabora) Failure & Fix

> **Update 2026-11-02 (cost optimisation):** Public IP is now the Elastic IP **13.234.211.7**; current `wopi_allowlist` = `127.0.0.1,::1,10.20.1.144,13.234.211.7`. The `3.111.213.217` values below are this incident's original record. See [SESSION_2026-11-02_COST_OPTIMISATION.md](SESSION_2026-11-02_COST_OPTIMISATION.md).

**Date:** 2026-10-12  
**Operator:** Logesh P S (with remote AI assistance)  
**Duration:** ~17:00–17:44 IST  
**System:** files.t-saraswathi.in — EC2 i-002509b77963fd5fc  
**Severity:** Service outage — Office document editing non-functional, nginx crashed  
**Resolution:** All services restored; Office editing confirmed working  

---

## 1. Symptoms Reported

- Opening any `.docx`, `.xlsx`, or `.pptx` file in Nextcloud showed:  
  **"Document loading failed — Nextcloud Office (Collabora) is not configured"**
- The Nextcloud web dashboard became inaccessible at one point (nginx down)
- The Nextcloud updater had been failing repeatedly before the Office issue

---

## 2. Root Cause Analysis

### 2.1 Disk Full (100%) — Cascading Trigger

The 30 GiB EBS root volume (`vol-0063c19bdcb7583bf`) filled to 100%:

```
$ df -h /
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        29G   28G  4.4M 100% /
```

**Cause:** The Nextcloud updater (v34.0.3 → v34.0.4) created a full backup of `/var/www/nextcloud` at:
```
/opt/nextcloud/data/updater-ocsfrsgd38gw/backups/nextcloud-34.0.3.2-1791802800/
```
This backup consumed **2.3 GiB**. Combined with the existing data (~12 GiB in `/opt/nextcloud/data`), the 2.3 GiB Nextcloud app tree in `/var/www/nextcloud`, system packages (~2.6 GiB in `/usr`), and logs (~3.2 GiB in `/var`), the disk had zero free space.

**Evidence — top disk consumers at time of failure:**
```
$ sudo du -ah / 2>/dev/null | sort -rh | head -n 20
19G     /
12G     /opt/nextcloud/data
5.0G    /opt/nextcloud/data/ganesh/files/Photos
3.5G    /opt/nextcloud/data/ganesh/files/Photos/Harini
3.2G    /var
2.7G    /opt/nextcloud/data/appdata_ocsfrsgd38gw
2.6G    /opt/nextcloud/data/updater-ocsfrsgd38gw
2.5G    /opt/nextcloud/data/appdata_ocsfrsgd38gw/preview
2.4G    /opt/nextcloud/data/updater-ocsfrsgd38gw/backups
2.3G    /var/www/nextcloud
2.3G    /opt/nextcloud/data/updater-ocsfrsgd38gw/backups/nextcloud-34.0.3.2-1791802800
2.0G    /var/www/nextcloud/apps
2.0G    /opt/nextcloud/data/updater-ocsfrsgd38gw/backups/nextcloud-34.0.3.2-1791802800/apps
```

**Errors caused by disk full:**
1. Updater download failed: `Curl error: Failure writing output to destination`
2. Updater backup failed: `errno=28 No space left on device`
3. sed command failed: `couldn't write 2975 items to updater/sedRIS6Mu: No space left on device`

### 2.2 Broken nginx Configuration File — nginx Crash

After the update succeeded (once disk was freed), the operator created a standalone file:
```
/etc/nginx/sites-enabled/nextcloud.conf
```

With the following content:
```nginx
# Collabora / CODE WebSockets configuration
location ~ ^/apps/richdocumentscode/proxy.php {
    proxy_pass http://127.0.0.1:9983;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";
    proxy_set_header Host $http_host;
    proxy_read_timeout 36000s;
}
```

**The problem:** An nginx `location` directive **must** be placed inside a `server { }` block. This file had the `location` block at the top level (line 2), outside any server context.

**nginx error:**
```
2026/10/12 11:36:58 [emerg] 1629813#1629813: "location" directive is not allowed here
    in /etc/nginx/sites-enabled/nextcloud.conf:2
nginx: configuration file /etc/nginx/nginx.conf test failed
```

**Impact:** nginx refused to start/reload, making the entire Nextcloud site inaccessible. The `systemctl restart nginx` command failed:
```
Job for nginx.service failed because the control process exited with error code.
```

**Why it was unnecessary:** The existing Nextcloud setup uses **built-in CODE** (richdocumentscode) which communicates through `proxy.php`, not via direct nginx reverse proxy. The PHP `location` block in the main site config (`files.t-saraswathi.in`) already has a rewrite rule that allows `proxy.php` through:
```nginx
rewrite ^/(?!index|remote|public|cron|status|ocs\/v[12]|ocs-provider\/.+|core\/ajax\/update
    |updater\/.+|.+\/richdocumentscode(_arm64)?\/proxy) /index.php$request_uri;
```
The `richdocumentscode(_arm64)?/proxy` exception in this rewrite ensures `proxy.php` is served directly by PHP-FPM, which then proxies to the local coolwsd on port 9983. **No separate nginx proxy location was needed.**

### 2.3 Incorrect `wopi_url` Configuration — Office "Not Configured"

The operator changed `wopi_url` multiple times trying to fix Office, each value being incorrect:

| Attempt | Value Set | Why It Was Wrong |
|---|---|---|
| 1 | `http://127.0.0.1:9980` | coolwsd listens on port **9983**, not 9980. Also HTTP not HTTPS. |
| 2 | `http://127.0.0.1:9983` | Correct port but HTTP — browser blocks mixed content on an HTTPS site. |
| 3 | `https://t-saraswathi.in` | Wrong domain — the Nextcloud site is `files.t-saraswathi.in`, not the bare domain. |
| 4 | `https://files.t-saraswathi.in` (first try) | Correct URL but nginx was **down** at this point, so the WOPI check failed. |
| 5 | Deleted `wopi_url`, set `public_wopi_url` instead | `public_wopi_url` is not the correct config key for this setup. |
| 6 | Deleted entirely | Worked in richdocuments **11.1.0** (original install) but **not** in **11.1.2** (post-update) — autodetect behavior changed. |

**Original working configuration** (documented in `02-architecture/TECHNICAL_SNAPSHOT_AND_FLOW.md`):
> *"Custom wopi_url is **empty**. Built-in CODE is reached only through `proxy.php?req=...`"*

However, after the Nextcloud update from 34.0.3 to 34.0.4, `richdocuments` was also updated from **11.1.0 → 11.1.2**. In this newer version, the autodetect behavior changed — an empty/deleted `wopi_url` no longer automatically discovers the built-in CODE server. The app now requires an explicit `wopi_url` pointing to the Nextcloud domain.

### 2.4 Secondary Issue: Duplicate nginx `wasm` Extension Warning

The site config at `/etc/nginx/sites-enabled/files.t-saraswathi.in` line 42 has:
```nginx
types {
    text/javascript mjs;
    application/wasm wasm;
}
```
But `application/wasm wasm` is already in the included system `mime.types` file, causing:
```
[warn] duplicate extension "wasm", content type: "application/wasm"
```
This is a **cosmetic warning only** — it does not break functionality. It was already documented as a known nit in `TECHNICAL_SNAPSHOT_AND_FLOW.md` section 7.

---

## 3. Timeline of Events

### 3.1 Pre-Fix: Operator's Troubleshooting Attempts (before AI assistance)

All times IST, 2026-10-12.

| Time (approx) | Action | Result |
|---|---|---|
| ~10:00 | `df -h` — checked disk | 89% used (25G/29G) |
| ~10:05 | Checked for Docker, Snap Nextcloud, Apache, MariaDB | None found — correct (nginx + PHP-FPM setup) |
| ~10:10 | `sudo ss -tulpn` | Confirmed nginx on 80/443 |
| ~10:15 | `sudo systemctl restart nginx php8.3-fpm` | Restarted OK |
| ~10:20 | Found Nextcloud at `/var/www/nextcloud/version.php` | Confirmed install location |
| ~10:25 | Ran updater: `sudo -u www-data php updater/updater.phar` | **Failed** — `Curl error: Failure writing output to destination` (disk full for download) |
| ~10:30 | Cleaned updater downloads and old logs | Partial space freed |
| ~10:35 | Ran updater again | **Failed** — `errno=28 No space left on device` during backup creation |
| ~10:40 | Ran updater with `--no-backup` | **Failed** — download still failed (still not enough space) |
| ~10:45 | Attempted `sed` on updater.phar | **Failed** — `No space left on device` |
| ~10:50 | Aggressive cleanup: removed old updater backups/downloads, old logs, apt cache | Freed space |
| ~10:55 | Checked disk | **100% full — only 4.4M free** |
| ~11:00 | Cleaned `/tmp`, `/var/tmp` | Minimal gain |
| ~11:05 | Found 2.4 GiB updater backup; deleted it | **Freed 13 GiB — disk at 57%** |
| ~11:10 | Ran updater again | **✔ Success** — Nextcloud updated 34.0.3 → 34.0.4 |
| ~11:15 | Ran `occ upgrade` | **✔ All migrations complete** |
| ~11:20 | Disabled maintenance mode | **✔ Site accessible** |
| ~11:25 | Ran `files:cleanup` and `files:scan --all` | **✔ 0 orphaned entries** |
| ~11:30 | Checked richdocuments and richdocumentscode apps | Both present: richdocuments 11.1.2, richdocumentscode 26.4.402 |
| ~11:32 | Disabled/re-enabled richdocuments | Toggled OK |
| ~11:35 | Set `wopi_url` to `http://127.0.0.1:9980` | **Wrong port** — coolwsd runs on 9983 |
| ~11:38 | Checked processes — found coolwsd on port 9983 | Confirmed correct port |
| ~11:40 | Set `wopi_url` to `http://127.0.0.1:9983` | **Wrong protocol** — HTTP on HTTPS site |
| ~11:42 | Set `wopi_url` to `https://t-saraswathi.in` | **Wrong domain** |
| ~11:45 | Set `wopi_url` to `https://files.t-saraswathi.in` | Correct URL but nginx issues ahead |
| ~11:50 | Deleted `wopi_url`, set `public_wopi_url` | Wrong config key |
| ~11:55 | Created `/etc/nginx/sites-enabled/nextcloud.conf` with bare location block | **Broke nginx** |
| ~11:57 | `sudo nginx -t` | **FAILED** — `"location" directive is not allowed here` |
| ~11:58 | `sudo systemctl restart nginx` | **FAILED** — nginx would not start |
| ~12:00 | Edited `nextcloud.conf` (still broken) | nginx still failing |
| ~12:05 | Set various wopi_url values again | No effect — nginx still down |
| ~12:10 | Set `disable_certificate_verification=yes` | Unnecessary — valid LE cert exists |

### 3.2 Fix Session: AI-Guided Repair

| Time | Command | Purpose | Result |
|---|---|---|---|
| 17:36 | `sudo rm -f /etc/nginx/sites-enabled/nextcloud.conf` | Remove broken nginx config | ✔ Removed |
| 17:37 | `sudo -u www-data php occ config:app:delete richdocuments wopi_url` | Clear all wrong WOPI URL values | ✔ `Config value wopi_url of app richdocuments deleted` |
| 17:37 | `sudo -u www-data php occ config:app:delete richdocuments public_wopi_url` | Clear wrong public_wopi_url | ✔ Deleted |
| 17:37 | `sudo -u www-data php occ config:app:delete richdocuments disable_certificate_verification` | Remove unnecessary cert skip | ✔ Deleted |
| 17:37 | `sudo -u www-data php occ config:app:set richdocuments wopi_allowlist --value="127.0.0.1,::1,10.20.1.144,3.111.213.217"` | Restore documented allowlist | ✔ Set (already matched) |
| 17:37 | `sudo -u www-data php occ config:system:set allow_local_remote_servers --value=true --type=boolean` | Ensure local connections allowed | ✔ Set |
| 17:38 | `sudo pkill -f coolwsd; sudo pkill -f coolforkit; sudo pkill -f Collabora_Online` | Kill stale Collabora processes | ✔ Killed |
| 17:38 | `sudo rm -rf /tmp/coolwsd* /tmp/appimage_extracted_*` | Clean stale temp files | ✔ Cleaned |
| 17:38 | `sudo -u www-data php occ app:disable richdocumentscode` | Disable CODE for restart | ✔ `richdocumentscode 26.4.402 disabled` |
| 17:38 | `sudo -u www-data php occ app:enable richdocumentscode` | Re-enable CODE (fresh start) | ✔ `richdocumentscode 26.4.402 enabled` |
| 17:39 | `sudo -u www-data php occ app:disable richdocuments` | Disable Office frontend | ✔ `richdocuments 11.1.2 disabled` |
| 17:39 | `sudo -u www-data php occ app:enable richdocuments` | Re-enable Office frontend | ✔ `richdocuments 11.1.2 enabled` |
| 17:39 | `sudo -u www-data php occ maintenance:mimetype:update-js` | Refresh mimetype cache | ✔ `mimetypelist.js is updated` |
| 17:39 | `sudo nginx -t` | Test nginx configuration | ✔ `syntax is ok` / `test is successful` (wasm warn only) |
| 17:39 | `sudo systemctl restart nginx php8.3-fpm` | Restart web stack | ✔ Both services restarted |
| 17:40 | `sudo systemctl is-active nginx` | Verify nginx | ✔ `active` |
| 17:40 | `sudo systemctl is-active php8.3-fpm` | Verify PHP-FPM | ✔ `active` |
| 17:40 | `curl -s https://files.t-saraswathi.in/status.php` | Verify Nextcloud | ✔ `{"installed":true,"maintenance":false,"version":"34.0.4.1"}` |
| 17:41 | `curl -s https://files.t-saraswathi.in/apps/richdocumentscode/proxy.php?req=/hosting/discovery` | Test WOPI discovery | ✔ Valid XML: `<wopi-discovery>` with writer/calc/impress apps |
| 17:42 | Opened `.docx` in browser | Test Office editing | **✘ "Nextcloud Office (Collabora) is not configured"** |
| 17:43 | `sudo -u www-data php occ config:app:set richdocuments wopi_url --value="https://files.t-saraswathi.in"` | Set explicit wopi_url for richdocuments 11.1.2 | ✔ `Config value 'wopi_url' set to 'https://files.t-saraswathi.in'` |
| 17:44 | Hard-refresh browser, opened `.docx` again | Test Office editing | **✔ Document opened in Collabora editor** |

---

## 4. What Was Fixed (Summary)

### Fix 1: Removed broken nginx config file
```bash
sudo rm -f /etc/nginx/sites-enabled/nextcloud.conf
```
- **Before:** nginx refused to start — entire site was down
- **After:** nginx config test passes, site accessible

### Fix 2: Cleaned up wrong `wopi_url` values
```bash
sudo -u www-data php occ config:app:delete richdocuments wopi_url
sudo -u www-data php occ config:app:delete richdocuments public_wopi_url
sudo -u www-data php occ config:app:delete richdocuments disable_certificate_verification
```
- **Before:** Multiple incorrect WOPI URLs preventing Collabora from connecting
- **After:** Clean slate for correct configuration

### Fix 3: Restored `wopi_allowlist`
```bash
sudo -u www-data php occ config:app:set richdocuments wopi_allowlist \
    --value="127.0.0.1,::1,10.20.1.144,3.111.213.217"
```
- **Before:** Potentially modified during troubleshooting
- **After:** Matches documented original values

### Fix 4: Restarted Collabora CODE (kill + disable/enable cycle)
```bash
sudo pkill -f coolwsd
sudo rm -rf /tmp/coolwsd* /tmp/appimage_extracted_*
sudo -u www-data php occ app:disable richdocumentscode
sudo -u www-data php occ app:enable richdocumentscode
```
- **Before:** Stale coolwsd process from pre-update, potentially holding old config
- **After:** Fresh coolwsd process started with clean temp files

### Fix 5: Set correct `wopi_url` for richdocuments 11.1.2
```bash
sudo -u www-data php occ config:app:set richdocuments wopi_url \
    --value="https://files.t-saraswathi.in"
```
- **Before:** Empty `wopi_url` — worked in richdocuments 11.1.0 but NOT in 11.1.2 (autodetect behavior changed after update)
- **After:** Explicit URL tells richdocuments 11.1.2 where to find CODE via `proxy.php`

---

## 5. Current State After Fix

### Services

| Service | Status |
|---|---|
| nginx 1.24 | ✔ active, listening on 80/443 |
| php8.3-fpm | ✔ active, unix socket |
| coolwsd (Collabora CODE) | ✔ running, port 9983 |
| Redis | ✔ running, 127.0.0.1:6379 |

### Nextcloud

| Item | Value |
|---|---|
| Version | 34.0.4.1 (updated from 34.0.3.2) |
| Maintenance mode | false |
| URL | https://files.t-saraswathi.in |
| Data dir | /opt/nextcloud/data |
| Admin user | saraswathi.admin |

### Collabora / Office

| Item | Value |
|---|---|
| richdocuments | 11.1.2 (updated from 11.1.0) |
| richdocumentscode | 26.4.402 (updated from 26.4.104) |
| wopi_url | `https://files.t-saraswathi.in` |
| wopi_allowlist | `127.0.0.1,::1,10.20.1.144,3.111.213.217` |
| WOPI discovery | ✔ HTTP 200 XML at `proxy.php?req=/hosting/discovery` |
| Document editing | ✔ Working (.docx, .xlsx, .pptx) |

### nginx

| Item | Value |
|---|---|
| Site config | `/etc/nginx/sites-enabled/files.t-saraswathi.in` (only file) |
| `nextcloud.conf` | **Deleted** (was causing crash) |
| Config test | ✔ Passes (wasm duplicate warning only — cosmetic) |

### Disk

| Before fix | After fix |
|---|---|
| 100% (4.4M free) | 57% (~13 GiB free) |

Space freed by deleting:
- `/opt/nextcloud/data/updater-ocsfrsgd38gw/backups/nextcloud-34.0.3.2-1791802800/` (2.3 GiB)
- `/tmp/*`, `/var/tmp/*` (misc)
- Old rotated logs in `/var/log/` (misc)
- Updater download attempts (misc)

---

## 6. Configuration Diff: Before vs After

### wopi_url

| Before (original install, Aug 2026) | During incident | After fix |
|---|---|---|
| Empty/deleted (autodetect) | Multiple wrong values cycled | `https://files.t-saraswathi.in` |

**Why the change:** richdocuments updated from 11.1.0 → 11.1.2 during the Nextcloud 34.0.3 → 34.0.4 update. The newer version requires an explicit `wopi_url` instead of autodetecting built-in CODE.

### nginx sites-enabled

| Before | During incident | After fix |
|---|---|---|
| `files.t-saraswathi.in` only | `files.t-saraswathi.in` + `nextcloud.conf` | `files.t-saraswathi.in` only |

### Nextcloud version

| Before | After |
|---|---|
| 34.0.3 (34.0.3.2 internal) | 34.0.4 (34.0.4.1 internal) |

### App versions

| App | Before | After |
|---|---|---|
| richdocuments | 11.1.0 | 11.1.2 |
| richdocumentscode | 26.4.104 | 26.4.402 |
| files_pdfviewer | (previous) | 7.0.0 |

---

## 7. Lessons Learned

1. **Always check disk space before running the Nextcloud updater.** The updater creates a full backup (~2.3 GiB) plus downloads the new version (~300 MB). On a 30 GiB disk with 12+ GiB of user data, this requires at least 3 GiB free.

2. **Do not create standalone nginx config files with `location` blocks.** A `location` block must always be inside a `server { }` block. For this setup, the single site config `files.t-saraswathi.in` handles everything — no extra files needed.

3. **Built-in CODE (richdocumentscode) does not need nginx reverse proxy.** The `proxy.php` script handles all communication between the browser and coolwsd. The PHP `location` block in the main site config already has a rewrite exception for `richdocumentscode/proxy`.

4. **After updating richdocuments, re-check `wopi_url`.** The autodetect behavior can change between versions. If Office stops working after an update, set `wopi_url` explicitly to the Nextcloud domain URL.

5. **Document the working configuration.** The existing `TECHNICAL_SNAPSHOT_AND_FLOW.md` was invaluable in knowing what the correct original settings were. This incident report updates the docs to reflect the new required setting.

---

## 8. Updated Technical Snapshot (Office Section)

Replace the Office section in `02-architecture/TECHNICAL_SNAPSHOT_AND_FLOW.md` with:

| Item | Value |
|---|---|
| Apps | richdocuments **11.1.2**, richdocumentscode **26.4.402** |
| Engine | COOLWSD (built-in CODE AppImage, no Docker, no second EC2) |
| Discovery | HTTP 200 XML at `.../proxy.php?req=/hosting/discovery` |
| wopi_url | `https://files.t-saraswathi.in` **(required since richdocuments 11.1.2; was empty in 11.1.0)** |
| allow_local_remote_servers | true |
| wopi_allowlist | 127.0.0.1, ::1, 10.20.1.144, 3.111.213.217 |

---

## 9. Preventive Actions

| Action | Owner | When |
|---|---|---|
| Monitor disk usage — alert at 80% | CloudWatch alarm `saraswathi-ec2-disk-high` already exists | Ongoing |
| Before any Nextcloud update: check `df -h /` has ≥5 GiB free | Operator | Before each update |
| After any Nextcloud update: verify Office works by opening a test document | Operator | After each update |
| If public IP changes (instance stop/start): update DNS A record AND `wopi_allowlist` | Operator | On IP change |
| Consider Elastic IP to prevent IP changes | **Done 2026-11-02** — EIP `13.234.211.7` | Done |

---

## 10. Files Modified on Server

| Path | Action | Backup |
|---|---|---|
| `/etc/nginx/sites-enabled/nextcloud.conf` | **Deleted** | No backup needed — content was incorrect |
| `/etc/nginx/sites-enabled/files.t-saraswathi.in` | **Not modified** | N/A |
| Nextcloud `appconfig` table (richdocuments settings) | Updated via `occ` | Previous values documented above |
| `/tmp/coolwsd*`, `/tmp/appimage_extracted_*` | Deleted (stale temp) | Recreated automatically by CODE on restart |
| `/opt/nextcloud/data/updater-ocsfrsgd38gw/backups/` | Deleted by operator before fix session | Was a backup of 34.0.3; no longer needed after successful 34.0.4 update |
