# From Home — Next Step: CloudTrail tags

Log file validation is **Enabled**. Trail **Logging**. First validation digest may stay `-` for up to an hour. Do **not** Stop logging.

Next: add the same three tags used on other production resources. Do **not** change the log bucket. Do **not** enable Insights, SNS, or CloudWatch Logs.

Sign in as `logesh.implementer`. Region: **Asia Pacific (Mumbai) / ap-south-1**.

## 1. Manage tags

1. CloudTrail → Trails → **`Saraswathi-management-trail`**.
2. **Tags** → **Manage tags**.
3. Add:

| Key | Value |
|---|---|
| Project | Nextcloud |
| Owner | Saraswathi |
| Environment | Production |

4. Save.

## 2. Paste back

- Three tag keys (values as above)
- Trail still **Logging**
- Validation still **Enabled**

### Observed after digest paste (2026-08-26 21:19 IST)

| Key | Value |
|---|---|
| Project | Nextcloud |
| Environment | Production |

**Owner=Saraswathi is not on the trail.** Add it now.

## 3. Add the missing tag

1. Same trail → **Tags** → **Manage tags**.
2. Add **Owner** = **Saraswathi**.
3. Save.

Paste three keys + Logging + validation **Enabled**. Do not Stop logging.

## Stop

Do not Stop logging. Do not create a second trail. Do not enable Insights.
