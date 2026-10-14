# From Home — Next Step: CloudWatch default-metric alarms

One monthly cost budget remains: `Saraswathi-Monthly-AWS-Budget` **$60**. Duplicate `_2` is deleted.

Next: **default CloudWatch alarms** (no agent). These use metrics AWS already publishes. Do **not** install `amazon-cloudwatch-agent`. Do **not** create extra users. Do **not** create NAT, EIP, AWS Backup vault, or DLM.

Sign in as `logesh.implementer`. Region: **Asia Pacific (Mumbai) / ap-south-1**.

## Values

| Item | Value |
|---|---|
| EC2 | `i-002509b77963fd5fc` (`saraswathi-nextcloud-app`) |
| RDS | `saraswathi-nextcloud-db` |
| Alarm 1 | `saraswathi-ec2-status-check-failed` |
| Alarm 2 | `saraswathi-ec2-cpu-high` |
| Alarm 3 | `saraswathi-rds-free-storage-low` |
| Tags | Project=Nextcloud, Owner=Saraswathi, Environment=Production |

Do **not** paste the notification email in chat. Type it only in the console.

## 1. SNS topic (once)

Alarms need one email destination.

1. Search **SNS** → **Topics** → **Create topic**.
2. Type: **Standard**.
3. Name: `saraswathi-ops-alerts`
4. Create.
5. **Create subscription**: Protocol **Email**. Endpoint = firm billing / ops address already used for AWS. Do not paste that address in chat.
6. Confirm the subscription from the mailbox (click the AWS confirm link).
7. Paste back: topic name + subscription **Confirmed** (yes/no). No email address.

If `saraswathi-ops-alerts` already exists and is Confirmed, skip create.

### Observed (2026-08-26)

| Item | Value |
|---|---|
| Topic | `saraswathi-ops-alerts` |
| Type | Standard |
| Region / account | ap-south-1 / 055855670388 |
| ARN | `arn:aws:sns:ap-south-1:055855670388:saraswathi-ops-alerts` |
| Subscriptions | **1** EMAIL — **Confirmed** (id `a5d1eb63-…`; do not store endpoint) |

Do not create a second topic.

## 1b. Create the email subscription (do this now)

Alarms will not mail anyone until this is **Confirmed**.

1. Stay on the topic `saraswathi-ops-alerts` (Mumbai).
2. **Create subscription**.
3. Protocol: **Email** (not Email-JSON, not SMS).
4. Endpoint: type the firm billing/ops address already used for AWS. **Do not paste that address in chat.**
5. **Create subscription**. Status will be **Pending confirmation**.
6. Open that mailbox. Click **Confirm subscription** in the AWS SNS mail.
7. Refresh the SNS topic. Status must be **Confirmed**. Count = 1.

Paste back: `saraswathi-ops-alerts` + **Confirmed** yes/no + subscription count. **No email. No ARN dump required.**

Do not create alarms until Confirmed. Do not create a second topic. Do not create a second subscription.

### Observed subscription (2026-08-26)

| Item | Value |
|---|---|
| Topic | `saraswathi-ops-alerts` |
| Protocol | EMAIL |
| Status | **Confirmed** (operator 2026-08-26) |
| Subscription id | `a5d1eb63-bc48-4b3b-8b86-f73d41781fd6` |

Endpoint was shown in console paste — **do not paste the address again**. It is not stored in this file.

## 1c. Confirm the mailbox (do this now)

1. Open the mailbox used for the SNS subscription (same address already in AWS).
2. Find mail from AWS Notifications: **Subscription Confirmation**.
3. Click **Confirm subscription**.
4. SNS topic → refresh. Status must change from Pending confirmation to **Confirmed**.
5. If no mail: wait 2–3 minutes, check spam. On the subscription page use **Request confirmation** once. Do not create another subscription.

Paste: **Confirmed** yes/no. No email. No alarms until Confirmed.

## 2. EC2 status check

1. **CloudWatch** → **Alarms** → **Create alarm** → **Select metric**.
2. **EC2** → **Per-Instance Metrics** → instance `i-002509b77963fd5fc`.
3. Metric: **StatusCheckFailed** (or StatusCheckFailed_Instance). Statistic **Maximum**, period **1 minute**.
4. Threshold: **Greater/Equal ≥ 1** (or **Greater than 0**). **Not** Greater than 1 — the metric is only 0 or 1, so `> 1` never fires.
5. Datapoints: **2 out of 2**. Missing data: **Treat as missing**.
6. Alarm name: `saraswathi-ec2-status-check-failed`
7. Notification: **In alarm** → topic `saraswathi-ops-alerts`.
8. Tags as above. **Create**.

### Preview checked (do not create yet)

| Field | Preview | Need |
|---|---|---|
| Metric / instance | StatusCheckFailed `i-002509b77963fd5fc` Max 1 min | OK |
| Notify | In alarm → `saraswathi-ops-alerts` | OK |
| Name | `saraswathi-ec2-status-check-failed` | OK |
| Threshold | Greater **> 1**, 1 datapoint | **Wrong** — change to **≥ 1** (or **> 0**) and **2 of 2** |
| Tags | 0 | Add Project/Owner/Environment |

### Preview rechecked (create now)

| Field | Value |
|---|---|
| Condition | Greater/Equal **>= 1**, Maximum, 1 min, **2 of 2**, missing as missing |
| Notify | In alarm → `saraswathi-ops-alerts` |
| Name | `saraswathi-ec2-status-check-failed` |
| Tags | 0 (optional; do not block) |

### Created (2026-08-26)

| Item | Value |
|---|---|
| Name | `saraswathi-ec2-status-check-failed` |
| State | **Insufficient data** (OK for a few minutes) |
| Condition | StatusCheckFailed >= 1 for 2 datapoints within 2 minutes |
| Actions | enabled |
| Region | ap-south-1 |

Do not delete it. Do not create a duplicate of this name.

## 3. EC2 CPU

1. Same instance. Metric: **CPUUtilization**. Statistic **Average**, period **5 minutes**.
2. Threshold: **Greater than 85** for **3 consecutive periods**.
3. Name: `saraswathi-ec2-cpu-high`
4. Notify **In alarm** → `saraswathi-ops-alerts`. Create.

### Created (2026-08-26)

| Name | State | Condition |
|---|---|---|
| `saraswathi-ec2-cpu-high` | **Insufficient data** (OK for a few minutes) | CPUUtilization > 85 for 3 datapoints within 15 minutes |
| `saraswathi-ec2-status-check-failed` | **OK** | StatusCheckFailed >= 1 for 2 datapoints within 2 minutes |

Do not delete either. Do not create duplicates.

## 4. RDS free storage

1. **Select metric**. Do **not** type `per` in the search box (that matches nothing).
2. Clear the search. Tab **Browse** (not Graph search).
3. Click namespace **RDS** (not EC2, not CPUUtilization).
4. Click **Per-Database Metrics** (or **By Database** / **DBInstanceIdentifier**).
5. Find DB `saraswathi-nextcloud-db`. Metric **FreeStorageSpace**. Select that one row.
6. Statistic **Average**, period **5 minutes**.
7. Threshold: **Lower <** `2147483648` (2 GiB in bytes). Datapoints **2 out of 2**. Missing as missing.
8. Name: `saraswathi-rds-free-storage-low`. Notify **In alarm** → `saraswathi-ops-alerts`. Create.

Do not change RDS publicly accessible. Do not resize the instance.

### Created (2026-08-26)

| Name | State | Condition |
|---|---|---|
| `saraswathi-rds-free-storage-low` | **Insufficient data** (OK for a few minutes) | FreeStorageSpace < 2147483648 for 2 datapoints within 10 minutes |
| `saraswathi-ec2-cpu-high` | **OK** | CPUUtilization > 85 for 3 datapoints within 15 minutes |
| `saraswathi-ec2-status-check-failed` | **OK** | StatusCheckFailed >= 1 for 2 datapoints within 2 minutes |

Default-metric alarms are complete. RDS Insufficient data is expected until the next 5-minute sample.

## 5. Paste back (no email)

- Topic `saraswathi-ops-alerts` Confirmed yes/no
- Three alarm **names** and **state** (OK / Insufficient data / In alarm)
- Region ap-south-1

Insufficient data for a few minutes is OK. In alarm on CPU or storage right after create is **not** OK — stop and paste the metric value only (no screenshot required).

## Stop

Do not create a fourth alarm this step. Do not create NAT, EIP, or another budget. Do not buy Savings Plans. Do not paste emails. CloudWatch **agent** (memory/disk) is the next guide.
