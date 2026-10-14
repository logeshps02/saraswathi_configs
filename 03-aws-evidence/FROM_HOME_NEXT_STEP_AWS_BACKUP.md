# From Home — Next Step: AWS Backup vault (EBS daily)

CloudWatch agent is running. Five alarms exist (status/CPU/RDS/mem **OK**; disk Insufficient data is OK).

RDS already has **automated backups 7 days**. This step adds a **scheduled EBS** backup in AWS Backup. Do **not** enable Fast Snapshot Restore. Do **not** restore over production. Do **not** create DLM. Do **not** create NAT, EIP, or extra users.

Sign in as `logesh.implementer`. Region: **Asia Pacific (Mumbai) / ap-south-1**.

## Values

| Item | Value |
|---|---|
| Vault | `saraswathi-backup-vault` |
| Vault encryption | KMS `alias/saraswathi-ebs` (same as the volume) |
| Plan | `saraswathi-ebs-daily` |
| Resource | EBS `vol-0063c19bdcb7583bf` only |
| Rule | Daily, retain **7 days** |
| Window | Start within 1 hour; complete in 2 hours (default OK) |
| Tags | Project=Nextcloud, Owner=Saraswathi, Environment=Production |

Do not add the RDS instance to this plan (RDS already snapshots). Do not enable continuous backup for EBS (not applicable).

## 1. Create vault

1. Search **AWS Backup** → **Backup vaults** → **Create backup vault**.
2. Name: `saraswathi-backup-vault`
3. Encryption key: **alias/saraswathi-ebs** (customer managed). Do not use `aws/backup` if the EBS key is offered.
4. Tags as above.
5. **Create vault**.

Paste vault **name** only.

### Observed (2026-08-26)

| Item | Value |
|---|---|
| Vault | `saraswathi-backup-vault` created 01:42 IST |
| Type | Backup vault (not air-gapped) |
| KMS | `c7e84359-7794-41ea-bd5c-5f77ccf75875` = `alias/saraswathi-ebs` |
| Recovery points | 0 (expected) |
| Vault lock | none — do not add |
| Tags | 0 (optional later) |
| Other vault | AWS `Default` — do not use for this plan |

Do not create a second custom vault. Do not create a logically air-gapped vault. Do not Create vault lock.

## 2. Create backup plan (EBS only)

1. AWS Backup → **Backup plans** → **Create plan**.
2. **Build a new plan** (not a template if the template adds extra resources).
3. Plan name: `saraswathi-ebs-daily`
4. Rule name: `daily-ebs-7d`
5. Vault: `saraswathi-backup-vault`
6. Frequency: **Daily**.
7. Retention: **7 days**.
8. Copy to another region: **off**.
9. Continuous backups / PITR: **off**.
10. Tags on recovery points: same Project/Owner/Environment if offered.
11. Create plan.

## 3. Assign resource

1. On the plan → **Assign resources**.
2. Resource assignment name: `saraswathi-nc-ebs`
3. IAM role: **Default role** (AWSBackupDefaultServiceRole). If AWS offers to create it, allow **once**.
4. Resource selection: **Include specific resource types**.
5. Resource type: **EBS**. Volume ID: `vol-0063c19bdcb7583bf`.
6. Do **not** add RDS, EC2 instance, S3, or EFS.
7. Assign.

### Observed plan + assignment (2026-08-26)

| Item | Value |
|---|---|
| Plan | `saraswathi-ebs-daily` created |
| Rule | `daily-ebs-7d` |
| Frequency | Daily **12:30 AM Asia/Calcutta** |
| Start within / complete within | 8 hours / 7 days (wider than 1h/2h; OK — do not recreate) |
| Retention | **7 days** |
| Vault | `saraswathi-backup-vault` |
| Continuous / PITR | Disabled |
| EBS archive / malware / air-gapped | off |
| Assignment | `saraswathi-nc-ebs` |
| IAM role | `AWSBackupDefaultServiceRole` |
| Resource | **EBS only** `vol-0063c19bdcb7583bf` |

Do not assign RDS. Do not Include all resource types. Do not create a second plan.

## 4. Paste back

- Vault name
- Plan name
- Resource: EBS volume id only
- Next backup time if shown

Do not click **Restore**. Do not enable Fast Snapshot Restore. Do not create a second vault.

## Stop

Scheduled EBS plan is complete. Do not add RDS. Do not create DLM. Do not Restore. Do not enable Fast Snapshot Restore. Do not create NAT or EIP. Do not paste emails. On-demand backup (same volume, same vault) is the next guide so the vault is not empty until 12:30 AM.
