# M1B — CANCELLED. Do not grow the 30 GiB volume

**Status 2026-08-31:** Operator refused grow (budget). Quotation is **30 GB disk + 150 GB S3**. Extra EBS + 7-day snapshots would blow `Saraswathi-Monthly-AWS-Budget` **$60**.

**Do not** Actions → Modify volume. Leave `vol-0063c19bdcb7583bf` at **30 GiB**.

**Go here:** [16_PLAN_S3_FOLDER_INDEX.md](16_PLAN_S3_FOLDER_INDEX.md) → [18_M1S3_ENABLE_EXTERNAL.md](18_M1S3_ENABLE_EXTERNAL.md)

The rest of this file is archived. Do not execute.

---

# (archived) M1B — Grow local EBS (Option E only)

**Who:** `logesh.implementer` + SSM  
**When:** Not used. Quotation path is S3 folder, not 200 GiB EBS.  
**Do not:** Restore a snapshot over prod. Do not Apply RDS OS. Do not grow this volume.

Archived target was data volume **≥ 200 GiB**. That is **out of quote**.

Live volume today: `vol-0063c19bdcb7583bf` **30 GiB** gp3 on `i-002509b77963fd5fc`, encrypted `saraswathi-ebs`.

---

## 1. Snapshot first

Already **Completed** in `saraswathi-backup-vault` (latest `snap-0f2a86657a62ff29d` 31 Aug 00:30 IST). **Skip** a new on-demand job. Do not Restore.

---

## 2. Increase volume (console)

1. EC2 → **Volumes** → `vol-0063c19bdcb7583bf`.
2. **Actions** → **Modify volume**.
3. Size: **200** (or larger if source > 132 GB). Type stay **gp3**.
4. Do not change IOPS unless Copilot says.
5. **Modify** → Yes.
6. Wait state **optimizing** / **in-use**. You may grow the filesystem while optimizing.

**Verify:** Volume size shows 200 GiB. Encryption still `saraswathi-ebs`.

---

## 3. Grow partition + filesystem (SSM)

Connect Session Manager. **One line at a time.**

See disks:

```sh
lsblk ; echo LSBLK:$?
```

Typical: `nvme0n1` with partition `nvme0n1p1` (names may differ — use **your** `lsblk` output).

Grow partition (example for `nvme0n1` partition 1 — **change names if lsblk differs**):

```sh
sudo growpart /dev/nvme0n1 1 ; echo GROWPART:$?
```

If `growpart` not found:

```sh
sudo apt-get update && sudo apt-get install -y cloud-guest-utils
```

Then growpart again.

Find filesystem type:

```sh
df -Th / ; df -Th /opt/nextcloud/data ; echo DF:$?
```

- If **ext4** on the data path:

```sh
sudo resize2fs /dev/nvme0n1p1 ; echo RESIZE:$?
```

- If **xfs**:

```sh
sudo xfs_growfs / ; echo RESIZE:$?
```

(Use the mount that actually holds `/opt/nextcloud/data`. If data is on `/`, grow `/`. If a separate mount, grow that mount.)

**Verify:**

```sh
df -h /opt/nextcloud/data ; echo DFDATA:$?
```

**Pass:** Size **≥ 200G** and **Avail** clearly **> 132G** (aim > 150G free).  
**Fail:** still 30G → partition did not grow; stop and ask with `lsblk` + `df -Th` pasted (no secrets).

---

## 4. App still up

1. Browser: https://files.t-saraswathi.in login.
2. Open `_restore-drill.txt`.
3. CloudWatch disk alarm: may need a few minutes; should return **OK**.

---

## 5. Cost note

Daily EBS snapshots will grow. Watch budget $60. Collabora already reports insufficient hardware — large disk does **not** fix CPU. Office may stay slow.

---

## Paste / record

```
M1B on-demand backup Completed: yes/no
M1B volume size GiB: 
M1B df Avail on data: 
M1B Avail > 132G: yes/no
M1B Files login still works: yes/no
```

Next: [06_M1C_CONFIRM_UPLOAD_LIMITS.md](06_M1C_CONFIRM_UPLOAD_LIMITS.md)
