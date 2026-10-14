# From Home — Next Step Only: S3 files bucket

Do this after KMS keys exist. Sign in as `logesh.implementer`.
S3 is global, but the bucket must be created in **Asia Pacific (Mumbai) ap-south-1**.

Do not upload the 150 GB yet. Do not make the bucket public. Do not create EC2.

Bucket name (lowercase, globally unique):

`saraswathi-nextcloud-files-055855670388`

If that name is taken, use:

`saraswathi-nextcloud-files-055855670388-aps1`

## 1. Create the bucket

1. Search `S3` → **Buckets** → **Create bucket**.
2. AWS Region: **Asia Pacific (Mumbai) ap-south-1**.
3. Bucket type: **General purpose**.
4. Bucket name: `saraswathi-nextcloud-files-055855670388`
5. Object Ownership: **ACLs disabled** (recommended).
6. Block Public Access: leave **Block all public access** ON.
7. Confirm the warning checkbox.
8. Bucket Versioning: **Enable**.
9. Default encryption:
   - Encryption type: **SSE-S3** (Amazon S3 managed keys) is OK for this first files bucket.
   - Bucket Key: Enable if shown.
   - Do not pick the EBS or RDS KMS keys for this bucket.
10. Object Lock: **Off** for now. We add immutability later after a restore test.
11. Tags: `Project=Nextcloud`, `Owner=Saraswathi`, `Environment=Production`
12. **Create bucket**.

## 2. Confirm settings

1. Open the new bucket.
2. **Permissions**: Block all public access = On.
3. **Properties**:
   - Region = ap-south-1
   - Versioning = Enabled
   - Default encryption = SSE-S3
4. Do not upload client files tonight.

## Stop

Reply **S3 created** with the exact bucket name.
