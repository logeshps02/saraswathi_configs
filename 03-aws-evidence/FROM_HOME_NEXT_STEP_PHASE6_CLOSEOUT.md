# From Home — Phase 6 close-out (read-only, one paste)

Activity **working**. Restore apps enabled. `admin_audit` logfile unset (default) — do **not** set it. Leave `_restore-drill.txt`. DR runbook is in `02-architecture/DR_RUNBOOK.md`.

Do **D + E + F**. One reply. Sign in as `logesh.implementer`. Mumbai.

## D. Budget

Billing → **Budgets** → `Saraswathi-Monthly-AWS-Budget`.

Paste: amount **$60**, status (Healthy/Exceeded), MTD amount or %. Do **not** paste emails. Do not create another budget.

## E. AWS Backup plan

AWS Backup → **Backup plans** → `saraswathi-ebs-daily`.

Paste: rule `daily-ebs-7d`, next backup time if shown, resource still EBS `vol-0063c19bdcb7583bf` only. Do **not** Restore. Do **not** add RDS.

## F. RDS backups

RDS → `saraswathi-nextcloud-db` → Maintenance & backups (or Backup).

Paste: automated backups **Enabled**, retention **7 days**. Do **not** take a manual snapshot. Do **not** restore.

### Confirmed (2026-08-26)

| Item | Value |
|---|---|
| D Budget | `Saraswathi-Monthly-AWS-Budget` **$60** Monthly; **Healthy**; **$9.44** / 15.73% MTD; alerts OK |
| E Rule | `daily-ebs-7d` Daily **12:30 AM Asia/Calcutta**; retain **7 days**; vault `saraswathi-backup-vault`; continuous/malware/archive **off** |
| F RDS | paste was **Aurora and RDS Dashboard** (1 instance, 2 snapshots) — not the DB backup panel |

## F again (instance only)

1. RDS → **Databases** (left) → **`saraswathi-nextcloud-db`**.
2. Tab **Maintenance & backups** (or **Backup**).
3. Paste: Automated backups **Enabled** + retention **7 days**.

Do not Create database. Do not Restore from S3. Do not take a snapshot.

### Confirmed F (2026-08-26)

| Item | Value |
|---|---|
| Instance | `saraswathi-nextcloud-db` **Available** db.t4g.micro MySQL Community ap-south-1b |
| Automated backups | **Enabled (7 Days)** |
| Copy tags to snapshots | Enabled |
| Backup window | 17:22–17:52 UTC |
| Latest restore time | 2026-08-26 21:57 IST |
| Snapshots | 2 automated Available (`…-2026-08-24-18-50`, `…-2026-08-25-17-32`) |
| Pending OS update | available — **do not Apply now** |

## Stop

Phase 6 close-out is **complete**. Do not Apply OS update. Do not Restore. Do not Take snapshot. Do not create users, SMTP, NAT, EIP, sixth alarm, second vault, or objectstore.
