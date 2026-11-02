# From Home — Next Step: RDS backup + one EBS snapshot

> **Update 2026-11-02 (cost optimisation):** Manual snapshot `snap-0a1d21b760e5e6bf6` was **deleted** on 2026-11-02 (cost cleanup). Daily AWS Backup (7 days) continues in `saraswathi-backup-vault`. See [SESSION_2026-11-02_COST_OPTIMISATION.md](../10-change-log/SESSION_2026-11-02_COST_OPTIMISATION.md).

Talk (`spreed` 24.0.4) is enabled. No HPB. Quotation apps at enable-level are closed.

Next: prove backups exist. Do **not** create extra users. Do **not** install CloudWatch agent, NAT, EIP, or AWS Backup vault in this step.

Sign in as `logesh.implementer`. Region: **Asia Pacific (Mumbai) / ap-south-1**.

## Values

| Item | Value |
|---|---|
| RDS | `saraswathi-nextcloud-db` |
| Expected backup retention | **7 days** (set at create) |
| EBS volume | `vol-0063c19bdcb7583bf` (30 GiB, instance `i-002509b77963fd5fc`) |
| Snapshot name | `saraswathi-nc-app-20260826` |
| Tags | Project=Nextcloud, Owner=Saraswathi, Environment=Production |

Do **not** stop the instance. Do **not** open port 22. Do **not** paste passwords.

## 1. Confirm RDS automated backups

1. AWS Console → **RDS** → **Databases**.
2. Open `saraswathi-nextcloud-db`.
3. Tab **Maintenance & backups** (or **Backups**).
4. Record (paste into chat as text, no screenshots required):
   - Automated backups: Enabled / Disabled
   - Backup retention period
   - Latest automated snapshot identifier (name only)
   - Publicly accessible: must stay **No**
5. Left: **Snapshots**. Filter `saraswathi-nextcloud-db`. Note if at least one automated snapshot exists.

Do not disable deletion protection. Do not make the DB public.

## 2. One manual EBS snapshot (app disk + Nextcloud data)

Data is still on local EBS (`/opt/nextcloud/data`), not S3 objectstore.

1. AWS Console → **EC2** → **Elastic Block Store** → **Volumes**.
2. Select `vol-0063c19bdcb7583bf` (`saraswathi-nextcloud-app`).
3. **Actions** → **Create snapshot**.
4. Description: `saraswathi-nc-app-20260826`
5. Tags: `Name=saraswathi-nc-app-20260826`, plus Project / Owner / Environment as above.
6. **Create snapshot**.
7. **Snapshots** → wait until **Completed**. Paste snapshot id (`snap-...`) and state only.

Do not delete the volume. Do not attach the snapshot to another instance.

## 3. Confirmed (2026-08-26)

| Item | Value |
|---|---|
| RDS automated backups | **Enabled (7 days)** |
| Copy tags to snapshots | Enabled |
| Backup window | 17:22–17:52 UTC |
| Latest restore time | 2026-08-26 00:32 IST |
| Automated RDS snapshots | `rds:saraswathi-nextcloud-db-2026-08-24-18-50`, `rds:saraswathi-nextcloud-db-2026-08-25-17-32` Available |
| EBS snapshot create | `snap-0a1d21b760e5e6bf6` from `vol-0063c19bdcb7583bf` |
| EBS snapshot status | **Completed** 100%; 12.3 GiB of 30 GiB; encrypted `saraswathi-ebs`; started 2026-08-26 00:36 IST |
| Volume | still In-use on `i-002509b77963fd5fc` `/dev/sda1`; encrypted `saraswathi-ebs` |
| DLM | no default policy (0/1 in last 24h is expected) |
| Fast Snapshot Restore | **do not** enable (cost) |

## 4. Snapshot status (one check)

EC2 → **Snapshots** → `snap-0a1d21b760e5e6bf6`. Paste **Status** only (`pending` / `completed` / `error`).

## Stop

Do not create an AWS Backup vault yet. Do not install CloudWatch agent. Do not restore over production. Do not enable Fast Snapshot Restore. Do not create a DLM default policy this step.
