# M1A — STOP. Do not enable primary objectstore

**Status 2026-08-31:** IAM + `HEAD_BUCKET:0` + `S3_PROBE:0` + vault **done**.  
**Do not** write `objectstore` into `config.php`. On this existing install that **hides** the current Files tree (not only UAT).

**Quotation path instead:** keep 30 GiB disk; attach the same bucket as Files folder **Backup_data**.

**Go here:** [16_PLAN_S3_FOLDER_INDEX.md](16_PLAN_S3_FOLDER_INDEX.md) → [18_M1S3_ENABLE_EXTERNAL.md](18_M1S3_ENABLE_EXTERNAL.md)

Keep the rest of this file only as history of the skipped cutover. Do not execute step 3+.

---

# (archived) M1A — S3 as Nextcloud primary storage (Option S)

**Who:** `logesh.implementer` + SSM. **Ask Copilot before pasting objectstore config** if anything differs from this file.
**When:** After M0 chose **S**. Maintenance window. Users should not be in Office.
**Do not:** upload 132 GB. Do not paste `config.php`. Do not create access keys. Do not make the bucket public. Do not Apply RDS OS. Do not NAT/EIP.

This was the original objectstore design. **Not used.** Bytes for 132 GB now go to the same bucket via **External storage**. Local `/opt/nextcloud/data` stays the Nextcloud data dir on 30 GiB.

If Nextcloud was installed on local disk first, objectstore is a **cutover**, not a checkbox in the UI.

---

## 0. Pre-check (console)

### 0.1 Bucket

1. AWS Console → region **Mumbai**.
2. **S3** → **Buckets** → `saraswathi-nextcloud-files-055855670388`.
3. Confirm: **ap-south-1**, Block public access **On**, Versioning **Enabled**, encryption **SSE-S3** (or bucket default).
4. **Permissions** → Block public access all four **On**.
5. Do not enable website hosting or Object Lock.

### 0.2 IAM — click-by-click

**A. Instance has the role**

1. AWS Console top-right region: **Asia Pacific (Mumbai) ap-south-1**.
2. Search **EC2** → **Instances**.
3. Open **`i-002509b77963fd5fc`** (name `saraswathi-nextcloud-app`).
4. Tab **Security** (not Networking).
5. Find **IAM role**. It must be exactly **`saraswathi-ec2-ssm`**.
6. If it is blank or a different name: **stop**. Do not Continue. Ask.

**B. Role has the S3 policy**

1. On that same Security tab, click the role name **`saraswathi-ec2-ssm`** (opens IAM).
   Or: search **IAM** → **Roles** → **`saraswathi-ec2-ssm`**.
2. Tab **Permissions**.
3. Under **Permissions policies**, find **`saraswathi-nextcloud-s3`**.
   - If it is listed as **Inline policy**, that is correct.
   - If the name is missing: **stop** and ask. Do not attach `AmazonS3FullAccess`.
4. Click **`saraswathi-nextcloud-s3`**. Confirm JSON has:
   - `s3:ListBucket` (and GetBucketLocation) on `arn:aws:s3:::saraswathi-nextcloud-files-055855670388`
   - `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` on `arn:aws:s3:::saraswathi-nextcloud-files-055855670388/*`
5. Do **not** create access keys.

SSM `HEAD_BUCKET:0` and `S3_PROBE:0` already prove this works. Still do A+B once and tick RESULTS_SHEET.

### 0.3 Snapshot before change — click-by-click

Do this **before** objectstore. Do **not** Restore. Do **not** pick vault **Default**.

1. Region **Mumbai**.
2. Search **AWS Backup** → left **Backup vaults**.
3. Click vault **`saraswathi-backup-vault`** (not Default).
4. Button **Create on-demand backup**.
5. Resource type: **EBS**.
6. Volume ID: click browse / dropdown → **`vol-0063c19bdcb7583bf`** only.
7. Backup vault: must show **`saraswathi-backup-vault`**. If it shows **Default**, change it.
8. Retention: **7 days**.
9. IAM role: **Default role**.
10. Continuous backup: **off**. Copy to another region: **off**.
11. **Create on-demand backup**.
12. Left **Jobs** → **Backup jobs**.
13. Wait until **Status = Completed** (several minutes). Refresh.
14. Open the job: **Target vault** must be `saraswathi-backup-vault`. Resource must be `vol-0063c19bdcb7583bf`.

Record: Status Completed + vault name (no Restore). An older Completed job in this vault (`snap-0877c1316d9702f73`) is from 26 Aug — still take a **new** one today before objectstore.

---

## 1. Maintenance

1. Nextcloud: Administration → **Overview** — note warnings (do not fix).
2. Tell anyone using Files to log out.
3. Optional: Files still works during config; Office may error. Prefer off-hours.

---

## 2. SSM — confirm IAM can still talk to S3

EC2 → `i-002509b77963fd5fc` → **Connect** → **Session Manager**.

Paste **one line**:

```sh
aws s3api head-bucket --bucket saraswathi-nextcloud-files-055855670388 --region ap-south-1 ; echo HEAD_BUCKET:$?
```

**Pass:** `HEAD_BUCKET:0` (or empty error + 0).
**Fail:** AccessDenied / 255 → stop. Do not edit Nextcloud. Ask.

Optional tiny probe (not 132 GB):

```sh
echo uat-s3-probe | aws s3 cp - s3://saraswathi-nextcloud-files-055855670388/uat-s3-probe.txt --region ap-south-1 ; aws s3 rm s3://saraswathi-nextcloud-files-055855670388/uat-s3-probe.txt --region ap-south-1 ; echo S3_PROBE:$?
```

**Pass:** `S3_PROBE:0`. Delete must succeed so the bucket stays empty of junk.

---

## 3. Enable objectstore

**Stop here if you have never done this on this server.**
Putting the wrong array in `config.php` can make **all files vanish from the UI** (data still on disk until migrated).

**Safe method (preferred):** use `occ` if the version supports it, **or** ask Copilot with SSM output of:

```sh
sudo -u www-data php /var/www/nextcloud/occ config:list system --private 2>/dev/null | grep -E 'objectstore|datadirectory|instanceid' ; echo OCC_LIST:$?
```

Do **not** paste the rest of config into chat. Only say: `objectstore present yes/no` and `OCC_LIST:0/1`.

Then ask Copilot: “M1A step 3: objectstore present yes/no” before writing config.

### Intended end state (do not type secrets)

- `objectstore` class: `OC\Files\ObjectStore\S3`
- bucket: `saraswathi-nextcloud-files-055855670388`
- region: `ap-south-1`
- **use_path_style** as required
- **no** `key` / `secret` — use **instance profile** (`use_arn_region` / IAM role). If a sample uses keys, **reject it**.
- `sse_c_key` unset
- hostname `s3.ap-south-1.amazonaws.com` unless AWS docs for the SDK say otherwise

After config + `php8.3-fpm` reload:

```sh
sudo systemctl reload php8.3-fpm ; echo RELOAD:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ status
```

**Pass:** `installed: true` and version 34.x.
**Fail:** installed false / exception → revert from EBS recovery point (ask; do not Restore over prod yourself).

---

## 4. Move existing Nextcloud files into the bucket

Local UAT files (`_uat-*`, Firm tree) must be copied into objectstore or they disappear from Files.

Typical pattern (run only after Copilot confirms the exact occ for NC 34):

```sh
sudo -u www-data php /var/www/nextcloud/occ files:scan --all ; echo SCAN:$?
```

If a dedicated migrate command exists on this version, Copilot will give **one line**. Do not invent `files:transfer` names.

**Verify in browser**

1. Login `saraswathi.admin`.
2. Files → Firm/Templates: `_uat-office`, `_uat-sheet`, `_uat-slides` still listed.
3. Home: `_restore-drill.txt` still listed. Open it; text still there.

**Verify in S3 (not a dump)**

1. S3 → bucket → list objects.
2. You should see **hashed object keys** (not pretty filenames). That is normal.
3. Object count > 0 after UAT files exist.
4. Do not delete objects in the console.

---

## 5. Proof file (required exit)

1. Files → Firm/Templates → **+** → **New text file** `_uat-s3.txt` with body `s3-ok`.
2. Refresh. File still there. Download matches `s3-ok`.
3. S3 console: object count increased (do not need to find the exact key).

**Pass:** round-trip in Files + bucket not empty.
**Fail:** Files error 503/500 → disable objectstore only with Copilot; do not keep retrying.

---

## 6. Health after cutover

1. Administration → Overview. New S3-related errors: copy **wording only** (no config).
2. CloudWatch disk alarm should stay **OK** (local disk no longer holds 132 GB).
3. Budget: S3 storage will grow only after M3.

---

## Paste / record

```
M1A bucket public blocked: yes
M1A IAM policy present: yes/no
M1A on-demand backup Completed: yes (id optional)
M1A HEAD_BUCKET: 0 / fail
M1A S3_PROBE: 0 / skip / fail
M1A objectstore enabled: yes / WAITING COPILOT
M1A occ status installed: true/false
M1A old UAT files still visible: yes/no
M1A _uat-s3.txt round-trip: yes/no
M1A S3 objects > 0: yes/no
```

If `WAITING COPILOT` at objectstore write: **ask before continuing**.
Next: [06_M1C_CONFIRM_UPLOAD_LIMITS.md](06_M1C_CONFIRM_UPLOAD_LIMITS.md)
