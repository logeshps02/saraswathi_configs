# M1S3-A — Enable External storage app

**Who:** `saraswathi.admin`  
**When:** After M0 + IAM + vault (already done). Disk stays 30 GiB.  
**Do not:** grow EBS. Do not objectstore. Do not create access keys. Do not upload 132 GB.

This app lets Nextcloud show the **existing S3 bucket** as a folder. Bytes go to S3 (quoted). The 30 GB disk stays for OS + small Firm tree.

## 1. Open Apps

1. Login https://files.t-saraswathi.in as `saraswathi.admin`.
2. Click the **grid** (top) or your **avatar**.
3. **Apps** (or Administration → Apps).
4. Left: **Your apps** / search box.

## 2. Find External storage

1. Search: `External storage` or `files_external`.
2. App name: **External storage support**.
3. If it says **Disable** / **Enabled**: already on. Record **already enabled**.
4. If **Enable** / **Download and enable**: click **Enable**.
5. Wait until it is enabled. No other apps.

## 3. Verify the settings page exists

1. Avatar → **Administration settings**.
2. Left list: **External storage** (under Administration, not Personal).
3. Page opens with a table (may be empty) and a row to add a mount.

If the left item is missing: you opened **Personal** settings. Use **Administration settings**.

## Paste / record

```
M1S3-A External storage app: already enabled / enabled now / missing
M1S3-A Administration External storage page opens: yes/no
```

Next: [19_M1S3_MOUNT_BUCKET.md](19_M1S3_MOUNT_BUCKET.md)
