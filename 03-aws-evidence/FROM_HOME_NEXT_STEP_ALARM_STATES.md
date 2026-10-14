# From Home — Next Step: Confirm five CloudWatch alarm states

Backup vault tags are **done** (Project / Owner / Environment). Vault lock none. Recovery point `snap-0877c1316d9702f73` Completed.

Next: read-only confirm of the five existing alarms. Disk was **Insufficient data** earlier; it should be **OK** now. Do **not** create a sixth alarm. Do **not** create a composite. Do **not** delete alarms. Do **not** enable CloudWatch Logs on the trail.

Sign in as `logesh.implementer`. Region: **Asia Pacific (Mumbai) / ap-south-1**.

## 1. Open Alarms

1. CloudWatch → **Alarms** → **All alarms**.
2. Confirm these five names and states:

| Name | Expected |
|---|---|
| `saraswathi-ec2-status-check-failed` | OK |
| `saraswathi-ec2-cpu-high` | OK |
| `saraswathi-rds-free-storage-low` | OK |
| `saraswathi-ec2-mem-high` | OK |
| `saraswathi-ec2-disk-high` | OK (was Insufficient data) |

Count must stay **5**. Do not create another.

If disk is still Insufficient data: wait; do not recreate. If any is **In alarm**, paste the name + state only — do not edit the threshold this step.

## 2. Paste back

- Five names + five states
- Alarm count = 5

### Confirmed (2026-08-26)

Alarms **(5)**. All **OK**. Actions enabled. No mute.

| Name | State | Condition |
|---|---|---|
| `saraswathi-ec2-disk-high` | **OK** | disk_used_percent > 80 for 2/10m |
| `saraswathi-ec2-mem-high` | **OK** | mem_used_percent > 85 for 3/15m |
| `saraswathi-rds-free-storage-low` | **OK** | FreeStorageSpace < 2147483648 for 2/10m |
| `saraswathi-ec2-cpu-high` | **OK** | CPUUtilization > 85 for 3/15m |
| `saraswathi-ec2-status-check-failed` | **OK** | StatusCheckFailed >= 1 for 2/2m |

## Stop

Do not create a sixth alarm. Do not create a composite. Do not delete. Do not paste SNS emails. CloudTrail digest confirm is the next guide.
