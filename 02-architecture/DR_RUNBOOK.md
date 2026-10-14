# DR runbook — Saraswathi Nextcloud (no secrets)

Account `055855670388`. Region **ap-south-1**. Operator `logesh.implementer` + MFA. Never root from home. Never paste passwords, `config.php`, keys, or emails.

## What is live

| Layer | Location | Recovery already proven |
|---|---|---|
| File bytes | EC2 `/opt/nextcloud/data` on `vol-0063c19bdcb7583bf` | Nextcloud trash + versions on `_restore-drill.txt` |
| Metadata | RDS `saraswathi-nextcloud-db` MySQL 8.4.9 | Automated backups **Enabled 7 days**; window 17:22–17:52 UTC; latest restore 2026-08-26 21:57 IST (do **not** restore over prod) |
| EBS image | AWS Backup vault `saraswathi-backup-vault` | On-demand `snap-0877c1316d9702f73` Completed; daily plan 12:30 IST retain 7d |
| S3 files bucket | `saraswathi-nextcloud-files-055855670388` versioning On | Empty; **not** objectstore — do not treat as live file store |
| Audit | CloudTrail `Saraswathi-management-trail`; NC Activity + admin_audit | Trail Logging; validation digest delivered |

## User restore (first choice)

1. Login as the file owner (`saraswathi.admin` today).
2. **Deleted files** → Restore. Proven 2026-08-26.
3. File **Details → Versions** → restore older. Proven 2026-08-26.
4. Do not empty Deleted files unless asked.

## Admin host path (second choice)

SSM only (no SSH 22). Instance `i-002509b77963fd5fc`. App `/var/www/nextcloud`. Data `/opt/nextcloud/data`. Do not copy production files off-box in chat.

## AWS restore (last resort — approval required)

- **Do not** Restore over the live instance or live RDS.
- **Do not** Fast Snapshot Restore.
- **Do not** DLM.
- If a volume restore is approved: restore snapshot to a **new** volume, attach to a **stopped test** path, never swap prod blindly.
- RDS: use a **new** instance from snapshot, not overwrite `saraswathi-nextcloud-db`.
- After any EC2 stop/start, public IPv4 may change — update Route 53 `files` A only. Do not change NS / delete / transfer domain.

## Monitoring

Five CloudWatch alarms **OK** → SNS `saraswathi-ops-alerts` (Confirmed). Do not create a sixth. Do not fire a test alarm.

## Hard stops

No NAT, no EIP unless IP lost after stop/start, no port 22, no PHP 8.5, no S3 150 GB fill, no extra users until groups/sharing is scheduled, no SMTP until asked.
