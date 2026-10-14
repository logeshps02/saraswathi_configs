# From Home — Next Step: CloudTrail validation digest

Five CloudWatch alarms are **OK**. Count = 5. Do not create a sixth.

Next: confirm the first **log file validation** digest was delivered. Earlier it showed `-` (up to ~1 hour is normal). Do **not** Stop logging. Do **not** enable Insights, SNS, or CloudWatch Logs. Do **not** change the log bucket.

Sign in as `logesh.implementer`. Region: **Asia Pacific (Mumbai) / ap-south-1**.

## 1. Open the trail

1. CloudTrail → Trails → **`Saraswathi-management-trail`**.
2. Check **General details**:

| Field | Need |
|---|---|
| Trail logging | **Logging** |
| Log file validation | **Enabled** |
| Last file validation delivered | a timestamp (not `-`) |

If **Last file validation delivered** is still `-`, wait; do not recreate the trail. Do not Stop logging.

## 2. Paste back

- Trail **Logging**
- Validation **Enabled**
- **Last file validation delivered** value (timestamp or still `-`)
- Insights still off

### Confirmed (2026-08-26)

| Item | Value |
|---|---|
| Trail | `Saraswathi-management-trail` **Logging** |
| Multi-region | Yes |
| Last log file | 2026-08-26 21:19:42 IST |
| Log file validation | **Enabled** |
| Last file validation delivered | **2026-08-26 20:22:26 IST** |
| Insights / SNS / CloudWatch Logs | off |
| Data events | files bucket Read+Write Enabled; all-buckets blank |
| Tags | **2** — Project=Nextcloud, Environment=Production (**Owner missing**) |

## Stop

Do not Stop logging. Do not create a second trail. Do not enable Insights / SNS / CloudWatch Logs. Do not paste bucket policies. Add trail tag **Owner** next.
