# From Home — Next Step Only: Turn On CloudTrail

Do this on your own laptop after the client meeting. Sign in as `logesh.implementer`. Never sign in as root from home.

Do not create EC2, RDS, S3 for files, or Nextcloud in this step.

## 1. Sign in

1. Open Chrome or Edge on your laptop.
2. Open the IAM console sign-in URL you copied at the meeting.
   - It looks like: `https://12-digit-account-id.signin.aws.amazon.com/console`
3. Account ID: `055855670388` (Saraswathi).
4. Username: `logesh.implementer`
5. Password: your implementer password.
6. MFA code: from YOUR authenticator app.
7. After login, top-right region must be **Asia Pacific (Mumbai) / ap-south-1**.
   - If it is N. Virginia or anything else, change it now.

If login fails, stop. Call the partner. Do not try root unless they are on the call and approve it.

## 2. Create the CloudTrail trail

1. Top search bar: type `CloudTrail`.
2. Click **CloudTrail**.
3. If AWS shows a first-run page, click **Create a trail**.
4. If a trail already exists named `management-events` or similar, open it and confirm it is logging. Do not create a second trail unless the first is clearly unused.
5. Trail name: `saraswathi-management-trail`
6. Storage location: **Create new S3 bucket**.
7. Bucket name: `saraswathi-cloudtrail-logs-055855670388`
   - Bucket names must be lowercase, no spaces.
   - If taken, use `saraswathi-cloudtrail-logs-055855670388-aps1`
8. Leave **Log file SSE-KMS** enabled if AWS offers an AWS-managed key for the first trail. You can switch to a customer-managed key later.
9. Enable **Log file validation**.
10. Customer-managed AWS KMS key: skip for this first trail unless you already created a key.
11. Additional settings:
    - CloudWatch Logs: **Off** for now. We add alarms later.
    - Tags: add `Project=Nextcloud`, `Owner=Saraswathi`, `Environment=Production`
12. Click **Next**.

## 3. Choose what to log

1. Event type: **Management events**.
2. API activity: **Read and Write**.
3. Do **not** enable Data events yet. That costs more. We turn on S3 data events after the files bucket exists.
4. Do **not** enable Insights yet.
5. Click **Next**.
6. Review the page.
7. Click **Create trail**.

## 4. Prove it is working

1. Open the trail name `saraswathi-management-trail`.
2. Status should be **Logging**.
3. Note the S3 bucket name.
4. Wait 5–10 minutes.
5. Top search: `S3` → open the CloudTrail bucket.
6. You should see a folder path starting with `AWSLogs/` then the account ID.
7. Screenshot:
   - Trail status = Logging. Save as `YYYY-MM-DD_aws_cloudtrail-enabled_v1.png`
   - S3 bucket showing `AWSLogs`. Save as `YYYY-MM-DD_aws_cloudtrail-s3_v1.png`
8. Put both screenshots in this `03-aws-evidence` folder.
9. Fill the CloudTrail row in `AWS_ACCOUNT_EVIDENCE_TEMPLATE.md`.

## Stop

Do not create VPC, EC2, or any other service until CloudTrail screenshots are saved.
