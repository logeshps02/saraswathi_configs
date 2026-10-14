# Read me first — runbooks from now through Phase U

**Date:** 2026-08-31 (quotation path)  
**Live URL:** https://files.t-saraswathi.in  
**Admin user:** `saraswathi.admin`  
**AWS user:** `logesh.implementer` (MFA). Never root from home.  
**Region:** Mumbai `ap-south-1`  
**Account:** 055855670388  

These files are the full click-by-click path from **remaining testing** through **Phase U**. Do them **in order**. If a step fails, stop and ask. Do not invent a workaround.

**Quotation (locked):** 30 GiB OS disk stays. **150 GB lives on S3** (~₹320/mo). Budget **$60** / ~₹5,000 RI. Do **not** grow EBS. Do **not** enable primary objectstore in `config.php` (hides existing Files). **F:\Final** goes into Nextcloud folder **Backup_data** mounted on the existing S3 bucket.

Master picture: [16_PLAN_S3_FOLDER_INDEX.md](16_PLAN_S3_FOLDER_INDEX.md) and [../02-architecture/FROM_NOW_TO_END_PLAN.md](../02-architecture/FROM_NOW_TO_END_PLAN.md)

---

## Order (do not skip)

| # | File | What | Status / 132 GB? |
|---|---|---|---|
| 1 | [01_T1_ADMIN_UAT_BATCH5.md](01_T1_ADMIN_UAT_BATCH5.md) | Finish AA–AE | **Done** |
| 2 | [02_T2_ADMIN_UAT_OPTIONAL.md](02_T2_ADMIN_UAT_OPTIONAL.md) | Extra admin tests | **Done** (AH no track-changes) |
| 3 | [03_M0_FREEZE_SOURCE.md](03_M0_FREEZE_SOURCE.md) | Count `F:\Final`, pick S | **Done** |
| — | [04_M1A_S3_OBJECTSTORE.md](04_M1A_S3_OBJECTSTORE.md) | Primary objectstore | **Skip** (IAM/probe done; do not enable) |
| — | [05_M1B_GROW_EBS.md](05_M1B_GROW_EBS.md) | Grow 30→200 GiB | **Cancelled** (budget) |
| 4 | [17_OPTIONAL_DELETE_UAT.md](17_OPTIONAL_DELETE_UAT.md) | Delete `_uat-*` only | Optional |
| 5 | [18_M1S3_ENABLE_EXTERNAL.md](18_M1S3_ENABLE_EXTERNAL.md) | Enable External storage app | **Done** |
| 6 | [19_M1S3_MOUNT_BUCKET.md](19_M1S3_MOUNT_BUCKET.md) | Mount bucket as **Backup_data**, no keys | UI red → 21 |
| 6b | [21_M1S3_OCC_MOUNT.md](21_M1S3_OCC_MOUNT.md) | Same mount via `occ` if UI stays red | **Done** (verify ok, ID 1) |
| 7 | [20_M1S3_PROOF_FILE.md](20_M1S3_PROOF_FILE.md) | Tiny file in Files **and** S3 | **Done** |
| 8 | [06_M1C_CONFIRM_UPLOAD_LIMITS.md](06_M1C_CONFIRM_UPLOAD_LIMITS.md) | PHP/nginx 512M; small upload into **Backup_data** | **Done** |
| 9 | [07_M2_PILOT.md](07_M2_PILOT.md) | Pilot via desktop client → `/Backup_data/_pilot` | **Done** (Save-as PDF missing; Export PDF known fail) |
| 10 | [08_M3_FULL_UPLOAD.md](08_M3_FULL_UPLOAD.md) | `F:\Final` → `/Backup_data` then rclone `F:\f` → `Backup_data/DATA1` | **Done** desktop earlier; rclone **check pass 2026-09-12** 167861 files. Do not recopy. |
| 11 | [09_U1_PASSWORD_POLICY_AND_USERS.md](09_U1_PASSWORD_POLICY_AND_USERS.md) | Policy + create users | **Done** |
| 12 | [10_U2_GROUP_SHARES.md](10_U2_GROUP_SHARES.md) | Share Firm tree to groups | **Done** |
| 13 | [11_U3_PUBLIC_LINKS.md](11_U3_PUBLIC_LINKS.md) | Only if CS allows | **Done** (password+revoke; expiry/S3 share limits) |
| 14 | [12_U4_SMTP.md](12_U4_SMTP.md) | Mail | **Send-test yes** (2026-09-02). Optional: share mail / calendar. Then U5 |
| 15 | [13_U5_DESKTOP_MOBILE_WEBDAV.md](13_U5_DESKTOP_MOBILE_WEBDAV.md) | Staff devices | **Done** (selective sync pass; WebDAV skip) |
| 16 | [14_U6_FEATURE_UAT_WITH_USERS.md](14_U6_FEATURE_UAT_WITH_USERS.md) | Sharing / co-edit | **Done** U6-A–F (2026-09-02) |
| — | [15_DO_NOT_DO_YET.md](15_DO_NOT_DO_YET.md) | HPB, full-text, ClamAV, NAT, grow disk, objectstore | Never in this path |
| — | [RESULTS_SHEET.md](RESULTS_SHEET.md) | Paste after **each** file | — |

**Users (U1) may start after M1S3-C proof**, not after 132 GB finishes. Do **not** let extra users sync the full tree onto a 30 GB disk. They must use **Backup_data** (S3) or selective sync.

---

## Hard stops (every file)

- No passwords, app passwords, SMTP secrets, keys, or `config.php` in chat, git, or these notes.
- No root from home. No port 22. No PHP 8.5.
- No domain NS change / delete / transfer. Only `files` A record if IP changes after stop/start.
- No NAT, no EIP, no Apply RDS OS update, no FSR, no Object Lock, no all-S3 CloudTrail data events. **S3 data events stay off** (2026-09-12) unless a written change says otherwise. Do not Stop logging / Delete `Saraswathi-management-trail`.
- No `rclone sync`. No Nextcloud desktop full sync of Backup_data / ~123 GB. No recopy of `F:\f` / `E:\` (DATA1 check passed 2026-09-12). Do not stop EC2 to cut cost.
- No File → Export → PDF retry (known fail). Use **Save as PDF** near the filename.
- No dumping 132 GB into the S3 **console**. Nextcloud will not see those objects as Files folders unless they were uploaded **through** Nextcloud.
- No browser upload of the whole 132 GB tree. Use the desktop client after M1S3 proof.
- `_uat-*` and `_restore-drill.txt` are **tests only**. You may delete them ([17_OPTIONAL_DELETE_UAT.md](17_OPTIONAL_DELETE_UAT.md)). Keep the seven Firm folders.
- No Modify volume to 200 GiB. No `objectstore` in `config.php`. No access keys.

---

## Live facts you will reuse

| Item | Value |
|---|---|
| URL | https://files.t-saraswathi.in |
| EC2 | `i-002509b77963fd5fc` `saraswathi-nextcloud-app` t3.medium |
| Public IPv4 | Check EC2 if instance was stopped (was 3.111.213.217) |
| Volume | `vol-0063c19bdcb7583bf` 30 GiB gp3 |
| Data dir | `/opt/nextcloud/data` |
| App dir | `/var/www/nextcloud` |
| RDS | `saraswathi-nextcloud-db` private; do not Apply OS |
| S3 files bucket | `saraswathi-nextcloud-files-055855670388` |
| IAM role | `saraswathi-ec2-ssm` + inline `saraswathi-nextcloud-s3` |
| Groups | Firm-Admins, Firm-Partners, Firm-Seniors, Firm-Juniors, Firm-Trainees, Firm-Departed |
| Folders | Firm/{Partners,Administration,Clients,Statutory,Templates,Trainee-Workspace,Archive} |
| PHP upload | 512M (chunked desktop client is the 132 GB path) |
| Budget | `Saraswathi-Monthly-AWS-Budget` $60 |

**SSM (how to launch):** AWS console as `logesh.implementer` (MFA) → Region **Mumbai** `ap-south-1` → **EC2** → Instances → `saraswathi-nextcloud-app` (`i-002509b77963fd5fc`) → **Connect** → tab **Session Manager** → **Connect**. Shell is `sh`. Paste **one line** at a time. Do not use EC2 **Instance Connect** (SSH 22 is closed). Never root from home. If Connect is grey: instance running + IAM `saraswathi-ec2-ssm` + SSM agent (already used for occ).

**AWS console:** always region **Mumbai (ap-south-1)** unless the page is global (IAM, Billing).

---

## How to use RESULTS_SHEET

After each file, copy the **Paste / record** block into [RESULTS_SHEET.md](RESULTS_SHEET.md). If anything is **no** or an error, stop that phase and ask.
