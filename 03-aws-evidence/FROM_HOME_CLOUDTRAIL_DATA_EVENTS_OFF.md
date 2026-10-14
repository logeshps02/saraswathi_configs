# From Home — CloudTrail S3 data events OFF (keep management trail)

**Date observed:** 2026-09-12  
**Who:** `logesh.implementer` + MFA  
**Account:** 055855670388 Mumbai `ap-south-1`  
**Why:** rclone ingest of ~167k files generated S3 API + CloudTrail **data-event** cost (Sep MTD CloudTrail ~$14 + S3 ~$47). Management audit stays. Object-level S3 Get/Put/List logging on the files bucket is **off**.

Enable history (do not follow now): [FROM_HOME_NEXT_STEP_CLOUDTRAIL_DATA.md](FROM_HOME_NEXT_STEP_CLOUDTRAIL_DATA.md).

Do **not** put passwords in this file.

---

## Values

| Item | Value |
|---|---|
| Trail | `Saraswathi-management-trail` |
| ARN | `arn:aws:cloudtrail:ap-south-1:055855670388:trail/Saraswathi-management-trail` |
| Management events | **Keep On** (All / Read+Write) |
| Data events | **None** / not configured |
| Log bucket | `aws-cloudtrail-logs-055855670388-1f1c3ed9` — do not empty, do not data-event it |
| Files bucket | `saraswathi-nextcloud-files-055855670388` — no S3 data-event selector |
| Insights | Off |
| Trail logging | **Logging** — do not Stop logging, do not Delete |

---

## Observed 2026-09-12 (done)

Trail detail page:

- Trail logging **Logging**
- Multi-region **Yes**
- Last log file **September 12, 2026, 09:32:45 (UTC+05:30)**
- Log file validation **Enabled** (last digest 09:22:37 IST same day)
- Management events **API activity All**
- **Data event collection is not configured for this trail**
- Insights not configured
- Tags: Project=Nextcloud, Environment=Production

If you open **Edit trail** and the only Event type shown is **Data events**, that screen **turns data events back on**. Click **Cancel**. Do **not** Save changes.

---

## If data events come back (remove again)

1. CloudTrail → **Trails** → **`Saraswathi-management-trail`** only.
2. Confirm status **Logging**. Do not Stop logging. Do not Delete.
3. **Data events** → **Edit**.
4. Remove the S3 row / selector for `saraswathi-nextcloud-files-055855670388`.
5. Do not tick all current/future S3 buckets. Do not add Lambda, DynamoDB, or the log bucket.
6. Keep management events All.
7. Save.
8. Detail page must say data events **not configured**.

---

## Stop

Do not create a second trail. Do not disable CloudTrail in Account settings. Do not stop EC2. Already-billed September data-event charges do not reverse.
