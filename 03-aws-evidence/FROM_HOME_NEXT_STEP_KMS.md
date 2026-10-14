# From Home — Next Step Only: KMS keys

Do this after security groups are correct. Sign in as `logesh.implementer`.
Region must be **Asia Pacific (Mumbai) / ap-south-1**.

Do not create EC2, RDS, or Nextcloud in this step.
Do not download or paste key material. AWS holds the keys.

Create two customer-managed keys:

| Alias | Use later for |
|---|---|
| alias/saraswathi-ebs | EC2 / EBS volumes |
| alias/saraswathi-rds | RDS storage and snapshots |

S3 and CloudTrail can stay on AWS-managed keys for now.

## 1. Open KMS in Mumbai

1. Confirm top-right region is **Mumbai**.
2. Search `KMS` → open **Key Management Service**.
3. Left: **Customer managed keys**.
4. Click **Create key**.

## 2. Create alias/saraswathi-ebs

1. Key type: **Symmetric**.
2. Key usage: **Encrypt and decrypt**.
3. Key material origin: **KMS**.
4. Regionality: **Single-Region key**.
5. Click **Next**.
6. Alias: `saraswathi-ebs`
7. Description: `Saraswathi EBS encryption`
8. Tags: `Project=Nextcloud`, `Owner=Saraswathi`, `Environment=Production`
9. Click **Next**.
10. Key administrators: tick `logesh.implementer` and, if shown, the `Firm-Implementers` group.
    Do not tick anonymous or public.
11. Leave **Allow key administrators to delete this key** as AWS default unless you have a reason to change it.
12. Click **Next**.
13. Key users: tick `logesh.implementer`.
    We will add EC2 / Autoscale roles later if needed.
14. Click **Next**.
15. Review → **Finish**.
16. Open the key → copy the **Key ID**. Do not copy anything called plaintext key material. There will not be one.

## 3. Create alias/saraswathi-rds

Repeat Create key with:

- Alias: `saraswathi-rds`
- Description: `Saraswathi RDS encryption`
- Same tags, same admin and user (`logesh.implementer`)
- Single-Region, Symmetric, Encrypt and decrypt

## 4. Turn on rotation

For each new key:

1. Open the key.
2. Tab **Key rotation**.
3. Enable **Automatic key rotation** if it is off.
4. Period: **365 days** if asked.
5. Save.

## Stop

Reply **KMS done** with the two key IDs only (long hex IDs). No screenshots of secrets needed.
