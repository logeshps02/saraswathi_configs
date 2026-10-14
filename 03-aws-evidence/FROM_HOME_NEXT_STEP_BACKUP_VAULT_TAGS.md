# From Home — Next Step: AWS Backup vault tags

CloudTrail tags are **done**. Trail **Logging**. Validation **Enabled**.

Next: add the same three tags on the firm backup vault. It was created with **0 tags**. Do **not** restore. Do **not** enable Fast Snapshot Restore. Do **not** add vault lock. Do **not** create a second vault. Do **not** add RDS to the plan.

Sign in as `logesh.implementer`. Region: **Asia Pacific (Mumbai) / ap-south-1**.

## 1. Tag the vault

1. AWS Backup → **Backup vaults** → **`saraswathi-backup-vault`**.
2. **Tags** (or **Manage tags**).
3. Add:

| Key | Value |
|---|---|
| Project | Nextcloud |
| Owner | Saraswathi |
| Environment | Production |

4. Save.

Do **not** tag the AWS `Default` vault. Do **not** change KMS (`alias/saraswathi-ebs`). Do **not** Create vault lock.

## 2. Paste back

- Three tag keys on `saraswathi-backup-vault`
- Vault name still `saraswathi-backup-vault`
- Vault lock still none

### Observed (2026-08-26)

| Item | Value |
|---|---|
| Vault | `saraswathi-backup-vault` |
| Type | Backup vault |
| KMS | `c7e84359-7794-41ea-bd5c-5f77ccf75875` |
| Vault lock | none |
| Recovery points | 1 — `snap-0877c1316d9702f73` Completed, EBS `vol-0063c19bdcb7583bf`, retain 7 days |
| Tags | **2** — Project=Nextcloud, Environment=Production |
| Missing | **Owner=Saraswathi** — add this now |

Do not Create vault lock. Do not Delete vault. Do not Restore the snapshot.

## 3. Add the missing tag

1. Same vault → **Backup vault tags** → **Manage tags**.
2. Add **Owner** = **Saraswathi**.
3. Save.

Paste three keys (Project, Owner, Environment) + vault lock still none.

### Confirmed (2026-08-26 21:16 IST)

| Item | Value |
|---|---|
| Vault | `saraswathi-backup-vault` |
| Vault lock | none |
| Recovery points | 1 — `snap-0877c1316d9702f73` Completed |
| Tags | **3** — Project=Nextcloud, Owner=Saraswathi, Environment=Production |

## Stop

Do not Restore. Do not FSR. Do not delete recovery points. Do not add RDS to `saraswathi-ebs-daily`. Alarm-state confirm is the next guide.
