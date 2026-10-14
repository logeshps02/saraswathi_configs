# M1S3-B2 — Mount Backup_data with occ (UI still red)

**Who:** `logesh.implementer` SSM. Then `saraswathi.admin` Files.  
**When:** After the External storage **tick stays red** with “not dns compatible”.  
**Do not:** rename or recreate the AWS bucket. Do not grow EBS. Do not objectstore. Do not create access keys. Do not paste secrets.

The message is **not** “this name is illegal in AWS”. Nextcloud **failed HeadBucket**, then tried to **create** the bucket, then showed that text. The bucket already exists (`HEAD_BUCKET:0` as the instance role).

SSM shell is `sh`. **One line at a time.**

---

## 1. Browser — remove the red row

1. Administration settings → **External storage**.
2. Red row → **trash**. Confirm.
3. Leave the page. Do not click the tick again.

---

## 2. SSM — list mounts (must be empty of Backup_data)

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:list ; echo FELIST:$?
```

**Pass:** no `/Backup_data` row, or only old IDs you will delete.

If a row remains, note **ID** (number in first column). Delete it (replace `N`):

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:delete --yes N ; echo FEDEL:$?
```

---

## 3. SSM — confirm PHP can HeadBucket (same role as Nextcloud)

```sh
sudo -u www-data aws s3api head-bucket --bucket saraswathi-nextcloud-files-055855670388 --region ap-south-1 ; echo HEADWWW:$?
```

**Pass:** JSON with BucketArn / BucketRegion `ap-south-1` and `HEADWWW:0`.

**Fail:** paste the error only (no keys). Stop and ask. Do not create IAM users.

---

## 3b. If list already shows Mount ID 1 `/Backup_data` — do **not** create again

This is the current live case (2026-08-31). `HEADWWW:0`. Auth is already **None**. Do **not** run `files_external:create`. Do **not** type the letter `N` — use the number **1**.

Nextcloud 34 syntax is **`files_external:config 1 KEY VALUE`** — there is **no** word `set`. (`get` is also not a subcommand; omit it and only pass the key to read.)

Zero-width spaces (`\u200b`) from the browser form are in **bucket** and **region**. Rewrite both, then verify.

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:config 1 bucket saraswathi-nextcloud-files-055855670388 ; echo FEBUCKET:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:config 1 region ap-south-1 ; echo FEREGION:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:config 1 hostname s3.ap-south-1.amazonaws.com ; echo FEHOST:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:config 1 use_path_style true ; echo FEPATH:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:config 1 verify_bucket_exists false ; echo FEVERIFYOFF:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:config 1 bucket ; echo FEBUCKETGET:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:config 1 region ; echo FEREGIONGET:$?
```

**Pass:** bucket line is exactly `saraswathi-nextcloud-files-055855670388`. Region line is exactly `ap-south-1`. No `\u200b`.

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:verify 1 ; echo FEOK:$?
```

**Pass:** Result **success**. Then skip to step 7 list + step 8 browser.

If verify still fails: paste Result + Message only. Stop.

---

## 4. SSM — create the mount (no keys) — **only if list has no Backup_data**

One line:

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:create /Backup_data amazons3 builtin::builtin --config bucket=saraswathi-nextcloud-files-055855670388 --config hostname=s3.ap-south-1.amazonaws.com --config region=ap-south-1 --config use_ssl=true --config use_path_style=true ; echo FECREATE:$?
```

**Pass:** `Storage created with id N` (or similar) and `FECREATE:0`. Write the **ID**.

If it says unknown auth `builtin::builtin`, run this **instead** (same configs):

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:create /Backup_data amazons3 null::null --config bucket=saraswathi-nextcloud-files-055855670388 --config hostname=s3.ap-south-1.amazonaws.com --config region=ap-south-1 --config use_ssl=true --config use_path_style=true ; echo FECREATE:$?
```

If both fail: paste the **one** error line. Stop.

---

## 5. SSM — do not let Nextcloud create buckets

Replace `N` with the ID from step 4.

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:config N verify_bucket_exists false ; echo FEVERIFYOFF:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:config N use_path_style true ; echo FEPATH:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:config N region ap-south-1 ; echo FEREGION:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:config N hostname s3.ap-south-1.amazonaws.com ; echo FEHOST:$?
```

---

## 6. SSM — only Firm-Admins for now

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:applicable N --add-group Firm-Admins ; echo FEAPPL:$?
```

---

## 7. SSM — verify

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:verify N ; echo FEOK:$?
```

**Pass:** Result **success** (empty message OK) and `FEOK:0`.

**Fail:** paste Result + Message only. Stop.

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:list ; echo FELIST2:$?
```

**Pass:** Mount Point `/Backup_data`, Storage amazons3, Status ok.

---

## 8. Browser

1. Hard refresh Files (Ctrl+F5).
2. Folder **Backup_data** at home. Open it. Empty is OK.
3. Administration → External storage: row **green**.

---

## Paste / record

```
M1S3-B2 red row deleted: yes/no
M1S3-B2 HEADWWW: 0 / fail
M1S3-B2 create auth used: builtin::builtin / null::null
M1S3-B2 mount ID: 
M1S3-B2 files_external:verify: success / fail (message)
M1S3-B2 Files shows Backup_data: yes/no
```

Next: [20_M1S3_PROOF_FILE.md](20_M1S3_PROOF_FILE.md)
