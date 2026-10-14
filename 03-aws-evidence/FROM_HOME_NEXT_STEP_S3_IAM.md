# From Home — Next Step: S3 IAM access from the app host

Bucket `saraswathi-nextcloud-files-055855670388` already exists (private, versioning, SSE-S3, empty). Instance role is `saraswathi-ec2-ssm` (SSM only so far).

This step only proves the host can use **IAM** to talk to that bucket. Do **not** put objectstore into Nextcloud yet (instance is already installed on local `/opt/nextcloud/data`; primary S3 after install is not a live toggle).

Sign in as `logesh.implementer`. Region **Mumbai** for EC2/IAM. S3 bucket is in **ap-south-1**.

Do **not** create access keys.
Do **not** make the bucket public.
Do **not** upload 150 GB.
Do **not** create NAT or EIP.
Do **not** paste `config.php`.
Do **not** open port 22.

## Values

| Item | Value |
|---|---|
| Bucket | `saraswathi-nextcloud-files-055855670388` |
| Region | ap-south-1 |
| IAM role | `saraswathi-ec2-ssm` |
| Instance | i-002509b77963fd5fc |
| Policy name | `saraswathi-nextcloud-s3` |

## 1. Confirm the bucket (console)

1. Search `S3` → **Buckets**.
2. Open **saraswathi-nextcloud-files-055855670388** only.
3. Confirm: region **ap-south-1**, Block all public access **On**, Versioning **Enabled**, encryption SSE-S3 (or bucket default). Empty is OK.
4. Do not upload files here.

Reply: `S3_BUCKET_OK` or what differs.

## 2. Attach a least-privilege policy to the existing role (console)

1. Search `IAM` → **Roles** → **saraswathi-ec2-ssm**.
2. Confirm it is still attached to the Nextcloud instance. Do not create a second role.
3. **Add permissions** → **Create inline policy**.
4. JSON tab. Replace the sample with **exactly**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBucket",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation",
        "s3:ListBucketMultipartUploads",
        "s3:ListBucketVersions"
      ],
      "Resource": "arn:aws:s3:::saraswathi-nextcloud-files-055855670388"
    },
    {
      "Sid": "Objects",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:AbortMultipartUpload",
        "s3:ListMultipartUploadParts",
        "s3:GetObjectVersion",
        "s3:DeleteObjectVersion"
      ],
      "Resource": "arn:aws:s3:::saraswathi-nextcloud-files-055855670388/*"
    }
  ]
}
```

5. Next. Policy name: `saraswathi-nextcloud-s3`
6. **Create policy**.
7. Do **not** create an access key for `logesh.implementer` or for Nextcloud.

Reply: `S3_IAM_OK`

Result (2026-08-25): `S3_BUCKET_OK`. `S3_IAM_OK`.

## 3. Install AWS CLI v2 (SSM)

Ubuntu 24.04 has no `awscli` apt package (`E: Package 'awscli' has no installation candidate`). Install the official v2 bundle. Do not create access keys.

```sh
sudo DEBIAN_FRONTEND=noninteractive apt install -y unzip && curl -fsSL https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o /tmp/awscliv2.zip && unzip -qo /tmp/awscliv2.zip -d /tmp && sudo /tmp/aws/install && aws --version && rm -f /tmp/awscliv2.zip
```

Expected: `aws-cli/2.x` (or similar). If `aws` is still not found, stop.

Result (2026-08-25): apt `awscli` failed as expected. Use the v2 command above.

## 4. Prove instance-role S3 access (SSM)

Uses the instance profile. No keys.

```sh
aws sts get-caller-identity --region ap-south-1 && aws s3api get-bucket-location --bucket saraswathi-nextcloud-files-055855670388 --region ap-south-1 && aws s3 ls s3://saraswathi-nextcloud-files-055855670388 --region ap-south-1 && printf 'probe\n' | aws s3 cp - s3://saraswathi-nextcloud-files-055855670388/.saraswathi-iam-probe.txt --region ap-south-1 && aws s3 ls s3://saraswathi-nextcloud-files-055855670388 --region ap-south-1 && aws s3 rm s3://saraswathi-nextcloud-files-055855670388/.saraswathi-iam-probe.txt --region ap-south-1 && echo S3_PROBE_OK
```

Expected: Account `055855670388`; ARN containing `saraswathi-ec2-ssm`; bucket location `ap-south-1` (or empty LocationConstraint for some APIs — still OK if ls works); probe uploaded then deleted; `S3_PROBE_OK`.

If `AccessDenied` or `Unable to locate credentials`, stop. Do not create access keys.

## 5. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| Bucket | saraswathi-nextcloud-files-055855670388, ap-south-1, private |
| IAM | inline policy `saraswathi-nextcloud-s3` on `saraswathi-ec2-ssm` |
| AWS CLI | 2.36.30 at `/usr/local/bin/aws` (not Ubuntu apt) |
| Caller | account 055855670388, assumed-role `saraswathi-ec2-ssm` / `i-002509b77963fd5fc` |
| Probe | put then delete `.saraswathi-iam-probe.txt`; `S3_PROBE_OK` |
| Access keys | none |
| Nextcloud objectstore | not configured; data still `/opt/nextcloud/data` |

## Stop

S3 IAM access from the app host is complete. Do not paste `config.php`. Do not create access keys. Do not upload 150 GB. Do not switch Nextcloud primary storage in this step.
