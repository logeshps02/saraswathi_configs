# M1S3-B — Mount S3 as folder Backup_data (no access keys)

**Who:** `saraswathi.admin` Administration → External storage  
**When:** After 18 (app enabled).  
**Do not:** type AWS access key / secret. Do not grow disk. Do not objectstore. Do not console-upload 132 GB.

Authentication: **None / builtin** so the EC2 role `saraswathi-ec2-ssm` is used (already proven `S3_PROBE:0`).

Folder name in Files: **Backup_data** (matches M0 `Firm/Backup_data` as the S3 mount name at Files root). Do **not** also create an empty local `Firm/Backup_data` — that would be on the 30 GB disk.

## 1. Open the form

1. Administration settings → **External storage**.
2. Bottom of the table: empty row **Add storage** / **Folder name**.

## 2. Fill exactly

If a red row already exists: **pencil** to edit it, or **trash** it and add a new row. Do **not** create a new AWS bucket. Do **not** change the bucket name. The name is valid in AWS; Nextcloud only uses that DNS message when it **failed to see** the existing bucket and then tried to create one.

| Field | Value |
|---|---|
| Folder name | `Backup_data` (underscore, **no space**, do not type a leading `/`) |
| External storage | **S3-Compatible Object Storage** (this is the Amazon S3 backend) |
| Authentication | **None** — **not** Access key |
| Bucket | `saraswathi-nextcloud-files-055855670388` (no space at the end) |
| Hostname | `s3.ap-south-1.amazonaws.com` (**required** — do not leave empty) |
| Port | empty |
| Region | `ap-south-1` (**required** — empty defaults to eu-west-1 and the bucket “does not exist”) |
| Storage Class | empty or STANDARD |
| Use HTTPS | **on** |
| **Use Path Style** (`https://example.com/bucket`) | **on** |
| Legacy (v2) auth | **off** |
| Access key / Secret | **leave empty** |

**Why path style on:** Nextcloud talks to `https://s3.ap-south-1.amazonaws.com/saraswathi-nextcloud-files-055855670388`. That matches how the instance already proved `HEAD_BUCKET:0`. If HeadBucket fails, Nextcloud tries to **create** the bucket and then shows the misleading “not dns compatible” error.

If Authentication has **only** Access key and no None:

1. **Do not invent keys.**
2. Record `M1S3-B auth: access-key only` and **ask**. Stop.

## 3. Who can see it

1. **Available for:** add group **Firm-Admins** first (you). Later U2 can add Partners.
2. Do **not** tick “Allow users to create this type” unless you want staff adding buckets.
3. **Enable sharing** (checkbox on that row, often off by default): **on** only if staff must **Share** files that live on S3 (`Backup_data`). Until this is on, Files **⋯ → Share** on Backup_data has no permission toggles. This does **not** change the AWS bucket. Leave **off** if the archive must stay admin-only.

## 4. Save

1. Click the **tick** / **Save** on that row (not the browser back button).
2. Wait. A **green** icon = OK. **Red** = fail.

**Red:** copy the short error (no keys). If it is still **“not dns compatible”** after hostname + region + path style: **stop the UI**. Do not rename the bucket. Go to [21_M1S3_OCC_MOUNT.md](21_M1S3_OCC_MOUNT.md).

**Green:** continue.

## 5. See it in Files

1. Open **Files** (app).
2. Left or home: folder **Backup_data**.
3. Open it. Empty is OK.
4. **⋯** on Backup_data → **Details**: should not be a tiny local folder you created under Firm.

If you **already** created local `Firm/Backup_data`: leave it empty; the mount is **Backup_data** at Files root. M3 uses the **mount**, not `Firm/Backup_data` on disk.

## Paste / record

```
M1S3-B folder name: Backup_data
M1S3-B auth: None/builtin / ACCESS KEY ONLY STOP
M1S3-B row icon: green / red (error text)
M1S3-B Files shows Backup_data: yes/no
```

Next: [20_M1S3_PROOF_FILE.md](20_M1S3_PROOF_FILE.md)
