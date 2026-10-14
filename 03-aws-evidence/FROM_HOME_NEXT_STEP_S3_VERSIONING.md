# From Home — Next Step: Confirm S3 versioning

`files_versions` 1.27.0 and `files_trashbin` 1.24.0 are enabled. Retention stays default `auto`.

Next: confirm the **files bucket** still has versioning and public access blocked. Do **not** upload 150 GB. Do **not** make the bucket public. Do **not** set Nextcloud objectstore. Do **not** Restore AWS.

Sign in as `logesh.implementer`. Region: **Asia Pacific (Mumbai) / ap-south-1**.

## Values

| Item | Value |
|---|---|
| Bucket | `saraswathi-nextcloud-files-055855670388` |
| Need | Block all public access **On**; Versioning **Enabled**; SSE on |

## 1. Open the bucket

1. **S3** → **Buckets** → `saraswathi-nextcloud-files-055855670388` only.
2. **Properties**.
3. Paste (text): **Bucket Versioning** Enabled/Suspended, **Default encryption**, **Block public access** On/Off.
4. Do not upload objects. Do not edit Block Public Access.

If versioning is Suspended: **Edit** → Enable → Save. Then paste Enabled.

### Observed (2026-08-26)

| Item | Value |
|---|---|
| Bucket | `saraswathi-nextcloud-files-055855670388` ap-south-1 |
| Bucket Versioning | **Enabled** |
| MFA delete | Disabled (leave) |
| Default encryption | **SSE-S3**; Bucket Key Enabled |
| Object Lock | Disabled (do not enable) |
| Static website | Disabled |
| Transfer acceleration | Disabled |
| EventBridge / server access logging | Off |

Do not enable Object Lock, MFA delete, or website hosting. Do not upload objects.

## Stop

Do not fill the bucket. Do not create a second bucket. Do not paste access keys. Nextcloud Activity confirm is the next guide.
