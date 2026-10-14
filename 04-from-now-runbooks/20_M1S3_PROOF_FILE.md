# M1S3-C — Proof: one file in Files and in S3

**Who:** `saraswathi.admin` + `logesh.implementer` S3 console (look only)  
**When:** After 19 green mount.  
**Do not:** upload 132 GB. Do not delete the bucket. Do not make public.

## 1. Create a tiny file in Nextcloud

1. Files → open **Backup_data**.
2. **+** → **New text file** named `_s3-proof.txt`.
3. Body: `s3-ok` → save/close.
4. Refresh. File still listed.
5. **Download**. Open locally: text is `s3-ok`.

If create fails (timeout / forbidden): stop. Ask with the error. Disk is not the issue.

## 2. Confirm it is in the bucket (console)

1. AWS → Mumbai → **S3** → bucket `saraswathi-nextcloud-files-055855670388`.
2. You should see a key like `_s3-proof.txt` (external storage uses **real names**, unlike objectstore hashes).
3. Do not change permissions. Do not make public.

If the object is missing but Files shows the file: wait 30 s, refresh. If still missing: mount may be local — **stop**.

## 3. Optional SSM

```sh
aws s3 ls s3://saraswathi-nextcloud-files-055855670388/ --region ap-south-1 ; echo S3LS:$?
```

Expect `_s3-proof.txt` in the list. `S3LS:0`.

## 4. Disk still small

SSM:

```sh
df -h /opt/nextcloud/data ; echo DFDATA:$?
```

Size still ~30G. Avail must **not** need 132G. Proof file must not have filled the disk.

## 5. Delete the proof file in Nextcloud only

1. Files → Backup_data → **⋯** on `_s3-proof.txt` → **Delete**.
2. Optional empty trash.
3. S3: object gone or delete-marker (versioning on). Fine.

## Paste / record

```
M1S3-C create _s3-proof.txt in Backup_data: yes/no
M1S3-C download matches s3-ok: yes/no
M1S3-C object visible in S3 console or aws s3 ls: yes/no
M1S3-C df still ~30G: yes/no
```

**M1 (plan) exit:** all yes.  
Next: [06_M1C_CONFIRM_UPLOAD_LIMITS.md](06_M1C_CONFIRM_UPLOAD_LIMITS.md) — for M1C step 4, upload the small file **into Backup_data**, not Templates.

Then M2/M3: remote path **`/Backup_data`** (or `/Backup_data/_pilot`), local `F:\Final` for M3. Do not sync onto 30 GB home.
