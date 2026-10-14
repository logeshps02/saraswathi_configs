# Plan path (quotation) — S3 holds 150 GB, disk stays 30 GB

**Date:** 2026-08-31  
**Budget:** `Saraswathi-Monthly-AWS-Budget` **$60** ≈ quoted **₹5,000 RI / ₹6,200 on-demand**.  
**Do not grow EBS.** 200 GiB disk + 7-day snapshots is **not** in the quote. S3 150 GB **is** (~₹320/mo).

## What is already done (do not redo)

- T1, T2, M0 (`F:\Final`, ~132 GB, target `Firm/Backup_data`, option S)
- IAM role `saraswathi-ec2-ssm` + policy `saraswathi-nextcloud-s3`
- `HEAD_BUCKET:0` `S3_PROBE:0`
- Vault snapshots (latest 31 Aug Completed)
- **Objectstore in config.php:** do **not** enable (hides the whole existing Files tree, not only UAT)
- **M1B grow disk:** **cancelled**

## How 132 GB fits the quote

| Layer | Where | Cost |
|---|---|---|
| OS + Nextcloud + small Firm tree | 30 GiB EBS | quoted ~₹250 |
| **F:\Final (132 GB)** | S3 bucket `saraswathi-nextcloud-files-055855670388` shown in Files as **Backup_data** | quoted S3 ~₹320 |
| Names/folders | Nextcloud external S3 mount (real key names in the bucket) | — |

This is **not** dumping files in the S3 console. Nextcloud must own the upload so Files shows folders.

UAT `_uat-*` / `_restore-drill.txt` may be deleted. They are tests only. **Keep** `Firm/{Partners,Administration,Clients,Statutory,Templates,Trainee-Workspace,Archive}`.

## Order from here (one file at a time)

| # | File | Stop until RESULTS_SHEET has |
|---|---|---|
| 1 | [17_OPTIONAL_DELETE_UAT.md](17_OPTIONAL_DELETE_UAT.md) | optional |
| 2 | [18_M1S3_ENABLE_EXTERNAL.md](18_M1S3_ENABLE_EXTERNAL.md) | app enabled |
| 3 | [19_M1S3_MOUNT_BUCKET.md](19_M1S3_MOUNT_BUCKET.md) | green mount, no access keys |
| 3b | [21_M1S3_OCC_MOUNT.md](21_M1S3_OCC_MOUNT.md) | **Done** — mount 1 verify ok (ZWSP stripped) |
| 4 | [20_M1S3_PROOF_FILE.md](20_M1S3_PROOF_FILE.md) | **Done** — S3LS:0, df ~30G |
| 5 | [06_M1C_CONFIRM_UPLOAD_LIMITS.md](06_M1C_CONFIRM_UPLOAD_LIMITS.md) | **Done** — 512M, upload into Backup_data, df ~30G |
| 6 | [07_M2_PILOT.md](07_M2_PILOT.md) | **Done** — structure/search/trash pass; Save-as PDF missing |
| 7 | [08_M3_FULL_UPLOAD.md](08_M3_FULL_UPLOAD.md) | **Done** (operator Up to date + spot-checks) |
| 8 | U1–U3 | **Done** |
| 9 | [12_U4_SMTP.md](12_U4_SMTP.md) | Mail — **send-test yes** (2026-09-02). Optional share/calendar |
| 10 | U5–U6 | **Done** (WebDAV skip; U6-F sign pass). SES production wait-only |

Fill [RESULTS_SHEET.md](RESULTS_SHEET.md) after **each** file. Ask only if a step fails.

## Hard stops

- No Modify volume to 200 GiB
- No `objectstore` in `config.php`
- No access keys
- No S3 console upload of the 132 GB tree
- No NAT / EIP / Apply RDS OS / port 22 / passwords in chat
