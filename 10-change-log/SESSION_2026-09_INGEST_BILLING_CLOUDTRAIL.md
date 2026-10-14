# Session log — HP ingest, billing, users, CloudTrail data events off

**Written:** 2026-09-12  
**Scope:** Everything done in the Copilot chat that ended with CloudTrail data events confirmed **not configured**.  
**Operator:** Logesh P S (`logesh.implementer` + MFA)  
**Nextcloud admin:** `saraswathi.admin`  
**Live URL:** https://files.t-saraswathi.in  
**AWS account:** 055855670388 (Saraswathi), region Mumbai `ap-south-1`  
**Copy PC:** HP laptop, source `F:\f`  
**Do not** put passwords, app passwords, keys, MFA, or `config.php` here.

This chat was **not** already in project files. Older notes still said CloudTrail S3 data events were on, rclone target was `DATA!`, and M3 was desktop-client / `F:\Final`. This file is the start-to-end reference for **this** chat.

---

## 0. Hard stops (unchanged)

- Do **not** grow EBS 30 GiB → 200 GiB.
- Do **not** enable primary `objectstore` in `config.php`.
- Do **not** Apply RDS OS update.
- Do **not** run a second rclone while ingest was running (ingest is now finished).
- Do **not** Recopy `E:\` or `F:\`.
- Do **not** Nextcloud desktop **full sync** of ~123 GB / Backup_data (two-way; can change/delete `F:\f`; fills a 30 GB disk).
- Do **not** `rclone sync` (can delete remote). Only `rclone copy` (one-way, read local, write `DATA1`).
- Do **not** dump the tree in S3 console.
- Do **not** Stop logging or Delete `Saraswathi-management-trail`.
- Do **not** stop the EC2 to save money.
- Do **not** paste secrets in chat or git.

---

## 1. Product / demo (answered in this chat)

| Topic | Fact |
|---|---|
| Nextcloud | Hub 26 Spring **34.0.3** at https://files.t-saraswathi.in |
| LibreSign | **14.1.0**. **Not** CCA Class 3 / MCA production DSC. Sample/UAT signing only. |
| Collabora / Office | Built-in CODE. **No** Adobe Acrobat “Attachments” pane. PDF attachments are Nextcloud Files, not Adobe UI. |
| Calendar | **6.5.4** |
| Tasks | **0.18.1** |
| Deck | **1.18.3**. Board **Firm_Work** exists. Lists were empty — add: To do / Waiting client / Doing / Partner review / Done; share Firm-Seniors and Firm-Juniors. |
| Talk | No high-performance backend (expected). |
| SMTP / SES | Send-test yes earlier. **Not** firm-wide calendar/share email reminders until SES production + mail policy. |

Ground truth for features remains [CLIENT_FEATURE_ENCYCLOPEDIA.md](../CLIENT_FEATURE_ENCYCLOPEDIA.md) (B13 LibreSign limit; E Calendar/Tasks; F Deck).

---

## 2. Staff accounts (instructed; not fully verified in files)

Create at `https://files.t-saraswathi.in/settings/users`. Quota **5 GB**. **Not** `admin`. Unique password each. Shared password used in chat = **burned** — do not reuse; do not record the secret here.

| Username (as given) | Group |
|---|---|
| Sneka | Firm-Seniors |
| Dhanapriya | Firm-Seniors |
| Aglin | Firm-Seniors |
| Vijalakshmi | Firm-Seniors |
| Selvameena | Firm-Seniors |
| Asarudeen | Firm-Seniors |
| Jayalakshmi | Firm-Juniors |
| Saranya | Firm-Juniors |

Desktop: **selective sync only**. Never full Backup_data / DATA1 on a staff PC.

---

## 3. Bulk copy `F:\f` → `Backup_data/DATA1` (complete)

**Method:** rclone WebDAV on HP, `C:\rclone\rclone.exe`, remote `nextcloud` → `.../remote.php/dav/files/saraswathi.admin/`.  
**Target:** `nextcloud:Backup_data/DATA1` only. Not `DATA`, not `DATA!`, not `Final_v2`, not S3 console.  
**Desktop Nextcloud:** Paused.  
**PowerShell:** single quotes around remote path.

### 3.1 Source / counts

| Item | Value |
|---|---|
| Local source | `F:\f` on HP |
| Explorer file count | **1,67,861** files |
| rclone size (with old excludes) | 162364 objects, 123.414 GiB — **excludes** made object count differ; not missing files |
| Proven earlier (2026-09-03) | 167860 files / 123.5 GiB (pre-final) |

### 3.2 Problems seen (do not treat as “copy failed”)

| Symptom | Meaning | What we did |
|---|---|---|
| WebDAV 404 / 409 | Parent folder race | Retry **same** `rclone copy` (skip existing) |
| DNS “no such host” | Wi-Fi | Fix network; retry same copy |
| CPU 86–88% | `--transfers 8` then 6/4 too heavy | Fall back **transfers 2**, **checkers 4** |
| PowerShell gone; LastBootUpTime **2026-09-09 03:40:48** | Windows Update reboot (WU 43/19 then boot). DCOM 10010 noise | Not “rclone finished”. Restart copy |
| Short run Transferred **0 B**, Listed ~82k–98k | Incomplete tree walk | Not full inventory. Later Listed **304282** then **400834** |
| “Make it as local / full sync desktop” | Two-way client can change/delete `F:\f`, CPU, ~30 GB disk | Forbidden. rclone **copy** only |

### 3.3 Finish

Leftover no-exclude copy of remaining **~2.377 GiB / 8766 files**, **19h 7m**, **0 Errors**.

### 3.4 Verify (`rclone check --one-way`)

**When:** 2026-09-12 **00:37:47** (check end time as recorded in chat)

| Check | Result |
|---|---|
| Differences | **0** |
| Matching files | **167861** |
| Checks | **167861 / 167861** |
| Listed | **409498** |
| Hashes could not be checked | **56** (WebDAV checksum limit — **not** 56 missing files) |
| Transferred | **0 B** |
| Duration | **9h 22m** |
| vs Explorer | **1,67,861** files — match |

**Copy is done.** HP laptop **may stay off**. Do not recopy. Do not start another rclone unless **new** files appear on `F:\f`.

---

## 4. AWS billing (this chat)

| Item | Value |
|---|---|
| Budget | `Saraswathi-Monthly-AWS-Budget` **$60** |
| Seller | AISPL |
| Past due | **₹900.39** — Health `AWS_BILLING_ACCOUNT_PAST_DUE` **9 Sep 2026**. Pay. Payment preferences auto-pay. August invoice in Bills period **August 2026**. |
| Sep 1–10 MTD | **~$85.10** (Bills ~$84.59 Mumbai; EC2 listed top in one view) |
| Cost split (ingest month) | S3 **~$47.25** + CloudTrail **~$14.41** = rclone APIs + **S3 data events**, **not** t3.medium hourly (~**$9.78** instances) |
| Amazon Q “NAT” | Wrong. There is **no** NAT Gateway. |
| Cost Explorer $0 | AISPL pending invoice / empty report — not “AWS is free” |
| Do not | stop EC2, delete trail, empty log bucket, grow EBS |

September CloudTrail/S3 data-event **charges already billed do not reverse**.

---

## 5. CloudTrail S3 data events — OFF (2026-09-12)

**Goal:** keep management trail **Logging**; turn **off** S3 data events (ingest cost driver).

**Trail ARN:** `arn:aws:cloudtrail:ap-south-1:055855670388:trail/Saraswathi-management-trail`

### 5.1 Console observed (user paste, 2026-09-12)

| Field | Observed |
|---|---|
| Console user | `logesh.implementer` |
| Region | Asia Pacific (Mumbai) |
| Account | Saraswathi (055855670388) |
| Trail name | `Saraswathi-management-trail` |
| Trail logging | **Logging** |
| Multi-region | Yes |
| Org trail | Not enabled |
| Log location | `aws-cloudtrail-logs-055855670388-1f1c3ed9/AWSLogs/055855670388` |
| Last log file delivered | **September 12, 2026, 09:32:45 (UTC+05:30)** |
| SSE-KMS on log files | Not enabled |
| Log file validation | **Enabled** |
| Last file validation | September 12, 2026, 09:22:37 (UTC+05:30) |
| SNS | Disabled |
| CloudWatch Logs | Not configured |
| Tags | Project=Nextcloud, Environment=Production |
| Aggregated events | None |
| Management events | **API activity = All**; Exclude KMS **No**; Exclude RDS Data API **No** |
| **Data events** | **Data event collection is not configured for this trail** |
| Insights | not configured |
| Network activity | basic selectors; not configured |

**Status: done.** S3 data events are off. Management events stay on.

### 5.2 Trap on Edit trail

User opened **Edit trail** with **Event type = Data events**. That page **re-enables** data events (additional charges).

**Correct action:** **Cancel**. Do **not** Save changes.

Do **not** Delete trail. Do **not** Stop logging. Do **not** data-event the log bucket. Do **not** “all S3 buckets”. Do **not** add Lambda/DynamoDB/Insights.

### 5.3 How it was inverted (for next operator)

Enable runbook was [FROM_HOME_NEXT_STEP_CLOUDTRAIL_DATA.md](../03-aws-evidence/FROM_HOME_NEXT_STEP_CLOUDTRAIL_DATA.md) (files bucket Read+Write). Disable: Trails → this trail → Data events **Edit** → **remove** S3 selector for `saraswathi-nextcloud-files-055855670388` → Save → confirm “not configured”. If Edit already shows empty Data events, **Cancel**.

---

## 6. Still open (not this chat’s finish line)

- Pay **₹900.39** past due (not confirmed paid).
- Deck: five lists on Firm_Work + share groups (if not done).
- Staff: unique passwords; selective desktop sync only.
- SES production / firm-wide email reminders.
- CloudTrail data events stay **off** unless a later written change says otherwise.

---

## 7. Related files updated with this session

| File | What changed |
|---|---|
| [change-log.md](change-log.md) | 2026-09 rows for DATA1 check + data events off |
| [RESULTS_SHEET.md](../04-from-now-runbooks/RESULTS_SHEET.md) | rclone DATA1 complete + check |
| [DO_THIS_NOW_SYNC.md](../05-migration/DO_THIS_NOW_SYNC.md) | complete banner; do not recopy |
| [FROM_HOME_CLOUDTRAIL_DATA_EVENTS_OFF.md](../03-aws-evidence/FROM_HOME_CLOUDTRAIL_DATA_EVENTS_OFF.md) | disable + observed |
| [TECHNICAL_SNAPSHOT_AND_FLOW.md](../02-architecture/TECHNICAL_SNAPSHOT_AND_FLOW.md) | CloudTrail data events off |
| [00_READ_ME_FIRST.md](../04-from-now-runbooks/00_READ_ME_FIRST.md) | extra hard stops |
| [15_DO_NOT_DO_YET.md](../04-from-now-runbooks/15_DO_NOT_DO_YET.md) | rclone sync / desktop full / recopy / data events stay off |
