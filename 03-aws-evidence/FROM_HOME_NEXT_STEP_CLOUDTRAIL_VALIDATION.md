# From Home — Next Step: CloudTrail log file validation

S3 data events: files bucket Read+Write **Enabled**. All-buckets row may remain **unchecked** (basic UI). Insights off. Trail **Logging**.

Next: turn on **log file validation** on the same trail. Do **not** Stop logging. Do **not** create a second trail. Do **not** enable Insights. Do **not** enable CloudWatch Logs on the trail this step.

Sign in as `logesh.implementer`. Region: **Asia Pacific (Mumbai) / ap-south-1**.

## 1. Edit trail general details

1. CloudTrail → Trails → **`Saraswathi-management-trail`**.
2. **General details** → **Edit**.
3. **Log file validation**: **Enabled**.
4. Do **not** change the S3 log bucket (`aws-cloudtrail-logs-055855670388-1f1c3ed9`).
5. Do **not** enable SNS. Do **not** enable CloudWatch Logs here.
6. SSE-KMS: leave as-is (Not enabled is OK this step).
7. Save.

## 2. Paste back

- Trail **Logging**
- Log file validation **Enabled**
- Insights still off
- Data events still files bucket only (all-buckets not Enabled)

### Confirmed (2026-08-26)

| Item | Value |
|---|---|
| Trail | `Saraswathi-management-trail` **Logging** |
| Log file validation | **Enabled** |
| Last file validation delivered | `-` (first digest can take up to ~1 hour) |
| Insights / SNS / CloudWatch Logs | off |
| Data events | files bucket Read+Write Enabled; all-buckets row blank |
| Last log file | 2026-08-26 19:54 IST |

## Stop

Do not Stop logging. Do not delete the trail. Do not paste bucket policies. Trail tags are the next guide.
