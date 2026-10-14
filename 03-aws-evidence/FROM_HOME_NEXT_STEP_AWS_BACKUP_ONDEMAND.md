# From Home — Next Step: On-demand EBS backup into the vault

Vault `saraswathi-backup-vault` and plan `saraswathi-ebs-daily` exist. Assignment is EBS `vol-0063c19bdcb7583bf` only. Next scheduled run is **12:30 AM Asia/Calcutta**. Vault still has **0** recovery points.

This step: **one on-demand backup** of that volume into the same vault so Jobs can show Completed tonight.

Do **not** Restore. Do **not** enable Fast Snapshot Restore. Do **not** add RDS. Do **not** create DLM, NAT, or EIP.

Sign in as `logesh.implementer`. Region: **Asia Pacific (Mumbai) / ap-south-1**.

## Values

| Item | Value |
|---|---|
| Vault | `saraswathi-backup-vault` |
| Resource type | EBS |
| Volume | `vol-0063c19bdcb7583bf` |
| Retention | **7 days** |
| IAM role | Default `AWSBackupDefaultServiceRole` |

## 1. Create on-demand backup

1. AWS Backup → **Protected resources** or vault `saraswathi-backup-vault` → **Create on-demand backup**.
2. Resource type: **EBS**.
3. Volume ID: `vol-0063c19bdcb7583bf` (same app disk).
4. Backup vault: **`saraswathi-backup-vault`** (not Default).
5. Retention: **7 days**.
6. IAM role: **Default role**.
7. Do not enable continuous backup. Do not copy to another region.
8. **Create on-demand backup**.

## 2. Watch the job

1. AWS Backup → **Jobs** → **Backup jobs**.
2. Wait until **Completed** (can take several minutes).
3. Paste: job **status** + resource volume id only. No restore.

If **Failed**, paste the status and the short error text (no ARNs dump). Do not retry on a different volume.

### Observed job (wrong vault)

| Item | Value |
|---|---|
| Job | `d11d5ef7-7820-4fdf-853d-5596a7c1239f` |
| Status | **Completed** 01:55–01:56 IST |
| Resource | EBS `vol-0063c19bdcb7583bf` (correct) |
| Size | 30 GiB |
| Retention | 7 days |
| Target vault | **Default** — **wrong** |
| Snapshot | `snap-07664ef633cc92904` |

Do not Restore. Do not FSR. Do not delete Default. Do not delete this snapshot yet. Daily plan still targets `saraswathi-backup-vault`.

## 3. Redo on-demand into the firm vault (do this now)

1. Open vault **`saraswathi-backup-vault`** (not Default, not Vaults list Create).
2. **Create on-demand backup**.
3. EBS `vol-0063c19bdcb7583bf`.
4. Backup vault must read **`saraswathi-backup-vault`**. If the form shows Default, change it before Create.
5. Retention 7 days. Default role. Continuous off.
6. Create. Jobs → wait **Completed**.
7. Paste: **Status**, **Target vault** (must be `saraswathi-backup-vault`), volume id.

### Observed job (firm vault)

| Item | Value |
|---|---|
| Job | `6d24f30a-df45-4c0f-a288-ba0d38d3a218` |
| Status | **Completed** 02:01–02:02 IST |
| Resource | EBS `vol-0063c19bdcb7583bf` |
| Target vault | **`saraswathi-backup-vault`** |
| Snapshot | `snap-0877c1316d9702f73` |
| Size / retention | 30 GiB / 7 days |

On-demand into the firm vault is done. Leave the earlier Default-vault copy. Daily plan still runs 12:30 AM IST.

## Stop

Do not click Restore. Do not enable Fast Snapshot Restore. Do not backup RDS here. Do not create another on-demand job. Nextcloud versions/trash confirm is the next guide.
