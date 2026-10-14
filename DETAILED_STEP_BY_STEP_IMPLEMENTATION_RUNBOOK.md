# Secure Cloud Document Management System
## Detailed Step-by-Step Implementation Runbook

This runbook converts the quotation and feature index into an executable delivery sequence for a firm-owned AWS and Nextcloud deployment.

**Target:** 10 users, 150 GB initial migration, AWS Mumbai (`ap-south-1`)  
**Delivery target:** 20 working days after signed approval, advance payment, and complete client inputs  
**Primary implementer:** Logesh P S  
**Important:** Replace every value in angle brackets before execution. Never place passwords, private keys, access keys, or recovery codes in this document.

---

## 0. Rules Before Starting

1. The firm owns the AWS root account, domain, S3 data, backups, and Nextcloud data.
2. Do not share the AWS root password, root access keys, MFA recovery codes, or client user passwords.
3. Create a separate named implementation IAM identity or role with MFA and an expiry date.
4. Use `ap-south-1` for every production resource unless a written exception is approved.
5. Record every production change in a change log with date, operator, reason, and rollback plan.
6. Do not migrate production data until the backup and restore path has been tested with sample data.
7. Do not promise a feature solely because an app name exists. Test the exact feature in the chosen Nextcloud/app versions.
8. Do not buy a Reserved Instance until at least 30 days of actual usage and stability data are available.
9. Keep all generated reports in a restricted project folder, not in public links or personal cloud storage.
10. Use a password manager for credentials and delete temporary credentials after handover.

---

## 1. Required Inputs and Decisions

Obtain these before Day 1. Mark each item complete in the project tracker.

### 1.1 Client information

- [ ] Legal firm name and billing address.
- [ ] Final domain name, for example `firmname.co.in`.
- [ ] Final service hostname, for example `files.firmname.co.in`.
- [ ] Firm administrator name, email, and phone.
- [ ] AWS billing contact and payment method owner.
- [ ] 10-user list: full name, username, email, role, group, and status.
- [ ] Folder-level permission matrix.
- [ ] Approved folder naming convention.
- [ ] Source hard drive or source PC access for the 150 GB data.
- [ ] Office upload speed and migration windows.
- [ ] 3-5 UAT participants and all training participants.
- [ ] SMTP provider and sender address for system email.
- [ ] Mobile notification requirements.
- [ ] Retention period for audit logs, versions, trash, backups, and legal holds.
- [ ] Recovery objectives: target RPO and RTO.
- [ ] Approved sample DOCX, XLSX, PPTX, PDF, ODT, ODS, and ODP files.
- [ ] Approved logo, colours, login text, and disclaimer.

### 1.2 Decisions that must be written down

| Decision | Minimum required answer |
|---|---|
| AWS account owner | Named firm representative |
| Production region | Mumbai / `ap-south-1` |
| Domain owner | Firm, with registrar account controlled by firm |
| Database exposure | Private only |
| Backup retention | Exact number of days/months/years |
| Audit retention | Exact period and deletion/legal-hold process |
| RPO | Maximum acceptable data loss |
| RTO | Maximum acceptable restoration time |
| Public sharing | Allowed, restricted, or disabled by default |
| External file requests | Allowed only for named groups or disabled |
| Talk calls | Maximum participants and recording policy |
| Office compatibility | Named file samples and pass criteria |
| Support | Contact channel, severity definitions, response targets |

---

## 2. Day 1-3: Mobilisation and Baseline

### Step 2.1: Create the project control folder

Create a restricted folder with this structure:

```text
00-contract-and-approvals/
01-requirements/
02-architecture/
03-aws-evidence/
04-nextcloud-evidence/
05-migration/
06-security/
07-backup-restore/
08-uat-and-training/
09-handover/
10-change-log/
```

Set the project file naming format:

```text
YYYY-MM-DD_<area>_<description>_<version>.<extension>
```

### Step 2.2: Freeze the agreed scope

1. Copy the quotation into `00-contract-and-approvals`.
2. Copy the feature index into `01-requirements`.
3. Confirm whether the committed baseline is all 166 features or a subset.
4. Mark every feature as one of:
   - `MUST`: required for go-live.
   - `SHOULD`: required if configuration and compatibility permit.
   - `OPTIONAL`: not a go-live blocker.
   - `OUT`: explicitly excluded.
5. Correct the proposal wording from `130+` to `166`, or attach a reduced and approved feature list.
6. Record all scope changes in the change log before implementation.

### Step 2.3: Build the user and permission matrix

Use a table with these columns:

```text
username | full_name | email | group | status | quota_gb | top_level_folders | rights | admin_flag
```

Use groups such as:

```text
Firm-Partners
Firm-Seniors
Firm-Juniors
Firm-Trainees
Firm-Departed
Firm-Admins
```

For each folder, define only the rights needed:

```text
read | create | update | delete | share | reshare | download
```

Obtain written approval from the designated partner before creating accounts.

### Step 2.4: Inventory the source data

On the source Windows computer, record:

- Source drive label and serial number.
- Root folders included in scope.
- Total file count.
- Total byte size.
- File extensions.
- Files larger than 10 GB.
- Unsupported or encrypted files.
- Paths longer than the intended destination limits.
- Duplicate names and duplicate content.
- Files currently open or locked.
- Data excluded from migration.

Export the inventory to CSV and store it in `05-migration`.

Example PowerShell inventory command:

```powershell
$source = 'D:\FirmData'
Get-ChildItem -LiteralPath $source -File -Recurse -Force |
  Select-Object FullName, Length, LastWriteTime, Extension |
  Export-Csv -NoTypeInformation -Encoding UTF8 '.\source-inventory.csv'
```

Calculate the total file count and size:

```powershell
$files = Get-ChildItem -LiteralPath 'D:\FirmData' -File -Recurse -Force
[pscustomobject]@{
  FileCount = $files.Count
  TotalBytes = ($files | Measure-Object -Property Length -Sum).Sum
  TotalGB = [math]::Round((($files | Measure-Object -Property Length -Sum).Sum / 1GB), 2)
} | Format-List
```

Do not use this inventory as proof of migration. It is only the source baseline.

### Step 2.5: Confirm bandwidth and schedule

1. Measure upload bandwidth at the office during working and overnight periods.
2. Choose 3-5 migration windows.
3. Ensure the source PC does not sleep during migration.
4. Ensure no user edits the source data during the final migration window.
5. Make a written freeze plan for the final delta.

### Exit gate for Day 3

Proceed only when:

- [ ] Contract and scope are signed.
- [ ] AWS account owner and billing owner are identified.
- [ ] User and permission matrix is approved.
- [ ] Source inventory is complete.
- [ ] Domain is selected.
- [ ] Migration windows are approved.
- [ ] UAT and training participants are scheduled.

---

## 3. Day 4-5: AWS Account and Foundation

## Step 3.1: Create or verify the firm-owned AWS account

1. The firm representative creates the AWS account using the firm's legal email and payment method.
2. Confirm the AWS account ID and billing identity.
3. Enable MFA on the root user.
4. Remove any root access keys. If an unavoidable root access key exists, rotate and remove it immediately after setup.
5. Enable billing alerts and AWS Budgets.
6. Select `ap-south-1` in the AWS console.
7. Document account ID, region, owner, and creation date in the evidence folder. Do not document passwords.

### Step 3.2: Create the implementation role

Create a named role such as:

```text
LogeshImplementationRole
```

Requirements:

- MFA required where supported.
- Session duration limited to the work period.
- No permanent access keys.
- Access restricted to the required services.
- CloudTrail logging enabled before use.
- Role removed or disabled after handover.

Use IAM Access Analyzer to identify unused or public access.

### Step 3.3: Set the region and CLI profile safely

On the implementer's workstation, install AWS CLI v2 from the official AWS installer. Configure a temporary profile using SSO or an assumed role. Do not paste credentials into shell history.

Verify identity:

```powershell
aws sts get-caller-identity --profile <profile-name>
aws configure get region --profile <profile-name>
```

The result must show the firm account and `ap-south-1`.

### Step 3.4: Create the VPC

Recommended initial layout:

```text
VPC: 10.20.0.0/16
Public subnet AZ-a: 10.20.1.0/24
Public subnet AZ-b: 10.20.2.0/24
Private app subnet AZ-a: 10.20.11.0/24
Private app subnet AZ-b: 10.20.12.0/24
Private database subnet AZ-a: 10.20.21.0/24
Private database subnet AZ-b: 10.20.22.0/24
```

Use two Availability Zones for the database subnet group even if the initial application server is single-instance.

Create and record:

- VPC.
- Internet Gateway.
- Public route table.
- Private route tables.
- NAT Gateway if private application egress is required.
- Public and private subnets.
- VPC flow logs.
- DNS hostnames and DNS resolution.

Do not put the database in a public subnet.

### Step 3.5: Create security groups

Create separate security groups:

```text
sg-nextcloud-alb-or-web
sg-nextcloud-app
sg-nextcloud-db
sg-nextcloud-admin
```

Minimum intended rules:

| Group | Inbound | Source |
|---|---|---|
| Web | TCP 443 | `0.0.0.0/0` only if public portal is required |
| Web | TCP 80 | Public only for HTTP-to-HTTPS redirect and ACME if required |
| App | Application port | Web/security group only |
| DB | TCP 3306 | App security group only |
| Admin | SSH 22 | Fixed admin IP, VPN, or SSM only |

Prefer AWS Systems Manager Session Manager instead of public SSH. If SSH is temporarily needed, restrict the source IP and remove the rule after setup.

### Step 3.6: Create encryption keys

Create or use customer-managed KMS keys for:

- EBS volumes.
- RDS storage and snapshots.
- S3 server-side encryption where required.
- Backup vault encryption.
- CloudTrail log encryption if configured.

Record key aliases and rotation settings. Do not place key material in project files.

### Step 3.7: Create billing controls

Create:

- Monthly AWS Budget at the approved ceiling.
- Actual-cost alert at 50%, 80%, and 100%.
- Forecast-cost alert.
- SNS/email notification to the firm billing contact.
- Cost allocation tags such as `Project=Nextcloud`, `Owner=Firm`, `Environment=Production`.

### Exit gate for Day 5

- [ ] Account is firm-owned and MFA protected.
- [ ] Implementer uses delegated access only.
- [ ] VPC and private database subnets exist.
- [ ] Security groups are least-privilege.
- [ ] Encryption and billing controls exist.
- [ ] CloudTrail is active before further production actions.

---

## 4. Day 6-7: Server and Nextcloud Platform

### Step 4.1: Provision the application server

Choose the final EC2 size only after confirming the actual Nextcloud, Collabora, Talk, and concurrency requirements. Start with the quotation baseline if performance testing supports it.

Configure:

- Ubuntu 24.04 LTS.
- Encrypted root/data EBS volumes.
- IMDSv2 required.
- Automatic recovery enabled where supported.
- SSM agent installed and reachable.
- Security group with no unrestricted SSH.
- CloudWatch agent or equivalent monitoring.
- Instance tags.

Record AMI ID, instance ID, instance type, volume IDs, and private IP.

### Step 4.2: Patch the operating system

Connect through Session Manager or the approved restricted method:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt install -y nginx mariadb-client redis-server unzip curl wget jq acl fail2ban ufw unattended-upgrades
sudo reboot
```

After reboot:

```bash
uname -a
lsb_release -a
systemctl --failed
```

The failed-unit list must be empty or explained.

### Step 4.3: Configure the firewall

Use the AWS security group as the primary network boundary and host firewall as a second layer:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

Only allow SSH if the approved administration path requires it. If so, restrict it to the admin IP range.

### Step 4.4: Install the approved PHP and web stack

The exact PHP version must match the selected Nextcloud LTS support matrix. Do not blindly use a version from an unrelated tutorial.

Install the approved packages for the selected version, then verify:

```bash
php -v
php -m
nginx -v
redis-server --version
```

Enable required PHP modules from the Nextcloud installation documentation for the pinned version.

### Step 4.5: Configure Redis

Set Redis to local-only access unless a separate secured Redis design is approved:

```bash
sudo ss -ltnp | grep 6379
```

The listener should not be publicly reachable. Configure the Nextcloud local memory cache and file locking to use Redis. Save the final configuration in the admin runbook without exposing secrets.

### Step 4.6: Provision RDS MySQL

1. Create a private RDS subnet group using the database subnets.
2. Create an RDS security group allowing TCP 3306 only from the app security group.
3. Enable encryption.
4. Enable automatic backups and the agreed retention period.
5. Enable deletion protection for production.
6. Disable public accessibility.
7. Create a database, application user, and strong password in a secrets manager.
8. Test connectivity from the application server only.

Example connectivity check from the app host:

```bash
mysql --host=<private-rds-endpoint> --port=3306 --user=<app-user> --password --database=<database-name> -e 'SELECT VERSION();'
```

Do not put the password in the command line or shell history.

### Step 4.7: Install Nextcloud

1. Download the exact approved Nextcloud LTS package from the official source.
2. Verify the published checksum or signature.
3. Extract to the approved web root.
4. Place the data directory outside the web root.
5. Set ownership to the web server account.
6. Configure Nginx and PHP-FPM using the official version-specific guidance.
7. Complete installation using the RDS endpoint, database name, database user, Redis endpoint, and selected admin account.
8. Set trusted domains to the final hostname only.
9. Set default phone region, time zone, upload limits, background job mode, and maintenance settings.

Verify with the Nextcloud admin health page and CLI:

```bash
sudo -u www-data php /var/www/nextcloud/occ status
sudo -u www-data php /var/www/nextcloud/occ config:list system
```

Review the output for incorrect hostnames, public database settings, debug mode, and missing security warnings.

### Step 4.8: Configure Nginx and TLS prerequisites

1. Create the final DNS record only after the public endpoint is known.
2. Configure HTTP to redirect to HTTPS.
3. Configure request size and timeout values based on the migration and Office requirements.
4. Add the Nextcloud recommended security headers.
5. Obtain a certificate through the approved ACME/Let's Encrypt method.
6. Enable automatic renewal.
7. Test renewal in a controlled manner.

Verification:

```bash
sudo nginx -t
sudo systemctl reload nginx
curl -I https://<service-hostname>
sudo certbot renew --dry-run
```

Use an external TLS scanner after DNS resolves. Resolve all high-severity findings before UAT.

### Step 4.9: Configure background jobs

Use system cron for production background jobs rather than AJAX-only execution:

```bash
sudo -u www-data crontab -e
```

Add the approved Nextcloud cron command at the documented interval. Confirm jobs execute and that the admin health page does not report delayed background jobs.

### Exit gate for Day 7

- [ ] Ubuntu is patched and hardened.
- [ ] Nginx, PHP-FPM, Redis, RDS, and Nextcloud are healthy.
- [ ] Database is private.
- [ ] Trusted domain and HTTPS work.
- [ ] Background jobs run.
- [ ] No critical health or security warnings remain.

---

## 5. Day 8: Install and Configure Collaboration Apps

Install only the apps approved in the signed scope. Record the exact app version and configuration.

### Step 5.1: Nextcloud Office / Collabora

1. Decide whether to use a supported built-in/community deployment or a separate Collabora service.
2. Confirm the expected concurrent editing load.
3. Configure the WOPI/Collabora integration using the official documentation for the exact versions.
4. Restrict allowed hosts and origins.
5. Test DOCX, XLSX, PPTX, ODT, ODS, and ODP files.
6. Test two-user co-authoring.
7. Test export to PDF and version restore.
8. Record unsupported features instead of describing them as fully compatible.

### Step 5.2: Talk

1. Enable Talk.
2. Confirm signaling/backend requirements for the intended call size.
3. Configure public rooms only if approved.
4. Test chat, room membership, file drop, audio, video, screen share, mute, kick, and waiting room.
5. Confirm whether recording is disabled or controlled.
6. Confirm mobile push behavior.

### Step 5.3: Groupware

1. Enable Calendar, Contacts, and Tasks.
2. Create the shared firm calendar, for example `Firm-Deadlines`.
3. Configure time zone and working hours.
4. Test CalDAV and CardDAV with approved clients.
5. Test recurring events, reminders, shared contacts, vCard import/export, and tasks.

### Step 5.4: Deck, Time Manager, and LibreSign

1. Enable each app only after checking maintenance status and compatibility.
2. Create a sample board and test assignment, labels, comments, attachments, checklist, and sharing.
3. Configure signing policy and test with a non-production PDF.
4. Decide where signatures and audit evidence are retained.
5. Record any feature that requires a paid service, certificate, or separate backend.

### Exit gate for Day 8

- [ ] Every enabled app has an owner and version record.
- [ ] Office compatibility tests are recorded.
- [ ] Talk call-size and notification tests pass.
- [ ] Calendar/contact/task sync tests pass where in scope.
- [ ] No unapproved public room, public link, or app is enabled.

---

## 6. Day 9-10: Users, Groups, Permissions, and Audit

### Step 6.1: Create groups

Create the approved groups first. Do not assign permissions directly to individual users unless a documented exception is needed.

```text
Firm-Partners
Firm-Seniors
Firm-Juniors
Firm-Trainees
Firm-Departed
Firm-Admins
```

### Step 6.2: Create users

1. Create users with temporary invitation or password-reset flows.
2. Require users to set their own passwords.
3. Enable quotas from the approved matrix.
4. Disable self-service sharing or external sharing where the policy requires it.
5. Add each user to the approved group only.
6. Record account creation date and approver.
7. Do not record plaintext passwords.

### Step 6.3: Build the folder tree

Create the agreed root structure. Example only:

```text
Firm/
  Partners/
  Administration/
  Clients/
  Statutory/
  Templates/
  Trainee-Workspace/
  Archive/
```

Do not use this example without client approval. Preserve source folder names where migration requires it.

### Step 6.4: Apply permissions

For every top-level and sensitive folder:

1. Assign group access.
2. Disable resharing unless approved.
3. Set create/edit/delete rights separately.
4. Test access using a real test account from each group.
5. Test negative access: deliberately attempt access to a prohibited folder.
6. Record results in the permission test matrix.

### Step 6.5: Configure security policy

Configure and test:

- Password length and complexity.
- Failed-login throttling.
- Session timeout.
- Trusted domains.
- Rate limiting.
- Security headers.
- Upload scanning with ClamAV if included.
- Admin access and impersonation audit.
- IP restrictions only after confirming they will not lock out mobile/remote users.

### Step 6.6: Configure audit logs

Enable and record:

- Nextcloud login events.
- Failed login events.
- File view/download/edit/rename/move/share/delete/restore events.
- Administrative actions.
- CloudTrail management events.
- S3 object-level data events for the production bucket.
- Access logging where required.
- Retention and lifecycle rules.

Generate a test event for each category and save evidence with timestamps.

### Exit gate for Day 10

- [ ] All users and groups match the approved matrix.
- [ ] Positive and negative permission tests pass.
- [ ] User disable/re-enable workflow works.
- [ ] Security policy is active.
- [ ] Application and AWS audit evidence is available.

---

## 7. Day 11-15: Data Migration

Migration is a controlled process, not a single copy command.

### Step 7.1: Prepare the destination

1. Create the destination folder tree.
2. Confirm quotas and available capacity.
3. Confirm the destination is backed up.
4. Create a migration service account with only required access, or use the approved administrator workflow.
5. Set the migration log location.
6. Confirm no production user is editing destination folders during the bulk load.

### Step 7.2: Create source checksums

For the agreed source set, generate SHA-256 records containing:

```text
relative_path | size_bytes | last_write_time | sha256
```

Example PowerShell checksum command:

```powershell
$root = 'D:\FirmData'
Get-ChildItem -LiteralPath $root -File -Recurse -Force | ForEach-Object {
  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash
  [pscustomobject]@{
    RelativePath = $_.FullName.Substring($root.Length).TrimStart('\\')
    SizeBytes = $_.Length
    LastWriteTimeUtc = $_.LastWriteTimeUtc.ToString('o')
    SHA256 = $hash
  }
} | Export-Csv -NoTypeInformation -Encoding UTF8 '.\source-checksums.csv'
```

Keep the source drive unchanged while checksums are being generated.

### Step 7.3: Copy in batches

Use an approved transfer method. For a Windows source, use the Nextcloud desktop client or a controlled sync/upload tool. Avoid uploading through a browser for 150 GB.

Recommended batch order:

1. Templates and small reference data.
2. One representative client folder.
3. One complete department folder.
4. Remaining folders in approved batches.
5. Final delta after the source freeze.

After each batch:

- Record start/end time.
- Record source count and bytes.
- Record destination count and bytes.
- Record failures and retries.
- Record the operator and batch name.

### Step 7.4: Handle migration exceptions

Create an exception register for:

- Unsupported names.
- Path length errors.
- Locked files.
- Permission-denied files.
- Corrupt files.
- Files exceeding configured limits.
- Encrypted files requiring a password.
- Duplicate content.
- Files excluded by client decision.

Do not silently rename or omit files. Obtain client approval for every unresolved exception.

### Step 7.5: Verify batches

For each batch, compare:

- File count.
- Total size.
- Relative paths.
- SHA-256 checksums where the transfer method preserves the exact bytes.
- Randomly opened files from every major extension.

The comparison result must have one of these statuses:

```text
MATCHED
MATCHED_WITH_APPROVED_EXCEPTIONS
FAILED_RETRY_REQUIRED
FAILED_CLIENT_DECISION_REQUIRED
```

### Step 7.6: Freeze the source and perform the final delta

1. Notify all users of the source freeze time.
2. Prevent edits to the source folders.
3. Generate a new source inventory and checksum list.
4. Upload only new or changed files.
5. Reconcile the final destination.
6. Have the client verify representative folders.
7. Preserve the source drive unchanged until migration sign-off.

### Exit gate for Day 15

- [ ] All in-scope files are copied or listed as approved exceptions.
- [ ] Counts and sizes reconcile.
- [ ] Checksum comparison report is signed.
- [ ] Final delta is complete.
- [ ] Source preservation and retention decision is recorded.

---

## 8. Day 16-17: Backup, Disaster Recovery, Monitoring, and Audit

### Step 8.1: Configure S3 protection

1. Enable server-side encryption.
2. Enable versioning.
3. Block public access.
4. Restrict bucket access to the application role and approved administrators.
5. Enable object-level logging if required.
6. Add lifecycle rules only after retention requirements are approved.
7. Enable object lock/immutability only after confirming the legal and operational implications.
8. Test that an ordinary user cannot access the bucket directly.

### Step 8.2: Configure EBS and RDS backups

1. Configure daily EBS snapshots using AWS Backup or the approved mechanism.
2. Configure daily RDS snapshots and the approved retention period.
3. Tag all backup resources.
4. Encrypt the backup vault.
5. Configure cross-AZ or cross-region behavior only according to the approved data-residency decision.
6. Document the cost impact of every retention rule.

### Step 8.3: Configure Glacier archive

1. Define exactly what is archived: files, database exports, configuration, or full backup set.
2. Define archive frequency.
3. Define retention in years.
4. Define restore request ownership and expected retrieval time.
5. Define deletion/legal-hold rules.
6. Run a sample archive and retrieval test.

### Step 8.4: Run restore tests

Test these independently:

1. Restore a deleted user file from trash.
2. Restore an earlier file version.
3. Restore after user trash is emptied using the admin path.
4. Restore a sample object/version from S3.
5. Restore an EBS snapshot to a test instance.
6. Restore an RDS snapshot to a test database.
7. Restore the archive sample.
8. Document elapsed time, operator, result, and data integrity.

Do not perform destructive production restores without a maintenance window and approval.

### Step 8.5: Configure monitoring

Create alarms for:

- EC2 CPU, memory, disk, and status checks.
- EBS disk space.
- RDS CPU, storage, connections, and backup status.
- Application health endpoint.
- TLS certificate expiry.
- Failed backup jobs.
- Delayed Nextcloud background jobs.
- Unusual data transfer or cost.
- Repeated failed logins.

Send notifications to the firm's approved operations contact.

### Step 8.6: Write the disaster recovery procedure

The procedure must contain:

- Incident declaration authority.
- RPO and RTO.
- Contact list.
- Decision tree: file restore, database restore, server rebuild, or full recovery.
- Exact backup locations.
- Credential access process.
- Restore commands or console path.
- Validation checklist after restore.
- DNS cutover procedure.
- Communication template.
- Post-incident review.

### Exit gate for Day 17

- [ ] Backup jobs run successfully.
- [ ] Restore drills are recorded.
- [ ] Monitoring alerts are tested.
- [ ] Audit evidence is searchable.
- [ ] Disaster recovery procedure is usable by a trained administrator.

---

## 9. Day 18: User Acceptance Testing

Use a fresh test sheet with columns:

```text
Test ID | Feature code | Tester | Preconditions | Steps | Expected result | Actual result | Pass/Fail | Evidence | Defect ID
```

### Mandatory UAT scenarios

#### UAT-01: Login and account lifecycle

1. Log in as partner, senior, junior, trainee, and administrator.
2. Verify the correct landing page and visible folders.
3. Disable the trainee account.
4. Confirm active sessions and new login attempts are blocked.
5. Re-enable only after approval.

#### UAT-02: Folder permissions

1. Sign in as each role.
2. Open allowed folders.
3. Attempt to open prohibited folders.
4. Attempt create, edit, delete, share, and reshare operations.
5. Record every mismatch.

#### UAT-03: File workflow

1. Upload a file by browser and desktop client.
2. Preview it.
3. Rename, move, tag, favourite, comment, and lock it.
4. Edit it in Office.
5. Restore an earlier version.
6. Delete and restore it from trash.

#### UAT-04: External sharing

1. Create a password-protected link with expiry.
2. Open it in an unauthenticated browser.
3. Confirm download restriction if enabled.
4. Revoke the link.
5. Confirm access fails after revocation.
6. Test an upload-only file request and confirm existing files are not visible.

#### UAT-05: Collaboration apps

1. Co-edit an Office file with two users.
2. Create a Talk room and test chat, file drop, call, screen sharing, waiting room, mute, and kick.
3. Create a calendar event and reminder.
4. Attach a file to the event.
5. Test contact and task synchronization where included.

#### UAT-06: Audit

1. Generate login, failed login, view, download, edit, share, delete, restore, and admin events.
2. Search each event by user, date, action, and file.
3. Export CSV.
4. Correlate at least one event with CloudTrail/S3 evidence.

#### UAT-07: Recovery

1. Delete a test file.
2. Restore it from trash.
3. Restore an earlier version.
4. Confirm the backup/restore owner can explain the server and database restore process.

### Defect handling

- `P0`: security issue, data loss, broken login, or inability to recover. Blocks go-live.
- `P1`: core workflow or permission failure. Blocks go-live unless formally accepted by the partner.
- `P2`: non-core defect with workaround. May be scheduled after go-live.
- `P3`: cosmetic or documentation issue. Does not block go-live.

Obtain written sign-off for all accepted known issues.

---

## 10. Day 19: Training

### Administrator session

Cover:

1. Login and MFA.
2. User creation, disable, reset, and group assignment.
3. Folder permissions and sharing review.
4. Audit search and CSV export.
5. Trash and version restore.
6. Backup status and restore escalation.
7. Monitoring and billing alerts.
8. App enable/disable policy.
9. Support process and change control.
10. Credential and ownership rules.

### End-user session

Cover:

1. Browser login and password reset.
2. Upload, download, preview, search, tags, favourites, and comments.
3. Office editing and version restore.
4. Internal and external sharing policy.
5. Desktop sync and selective sync.
6. Mobile app and offline files.
7. Calendar, contacts, tasks, and Talk.
8. How to report suspicious links, lost devices, or wrong permissions.

Collect attendance and a short task-based completion record. A user should demonstrate at least one upload, one share, one restore, and one search.

---

## 11. Day 20: Go-Live and Handover

### Step 11.1: Go-live readiness review

Do not proceed unless all are true:

- [ ] P0 and P1 defects are closed or formally accepted.
- [ ] Final migration delta is complete.
- [ ] DNS and TLS are valid.
- [ ] Backups have passed.
- [ ] Monitoring notifications reach the firm contact.
- [ ] Users and permissions are approved.
- [ ] Documentation is complete.
- [ ] AWS billing owner is confirmed.
- [ ] Support contact and escalation path are confirmed.

### Step 11.2: Credential rollover

1. Create or confirm the firm's permanent administrator accounts.
2. Require MFA.
3. Rotate temporary implementation secrets.
4. Remove temporary users, access keys, SSH keys, and roles that are no longer needed.
5. Restrict the implementer to the agreed support role.
6. Record the completion without recording secret values.

### Step 11.3: DNS and user launch

1. Confirm the final DNS record resolves to the production endpoint.
2. Confirm HTTPS and certificate renewal.
3. Send users the approved login URL through a trusted channel.
4. Do not send passwords in the same message as usernames.
5. Ask users to change temporary passwords immediately.
6. Monitor login, error, CPU, memory, disk, and backup metrics during the first working day.

### Step 11.4: Handover contents

Deliver:

- Architecture diagram.
- AWS ownership and IAM guide.
- Resource/version inventory.
- User/group/folder permission matrix.
- User quick-start guide.
- Admin runbook.
- Migration report and checksum evidence.
- UAT results and known issues.
- Backup, restore, and DR procedure.
- Monitoring and billing guide.
- Audit-log procedure.
- Domain/DNS/TLS renewal instructions.
- Data export instructions.
- Support and change-request process.
- Credential rollover/deletion confirmation.

Obtain a signed handover and go-live acceptance.

---

## 12. First 30 Days After Go-Live

### Daily for the first week

- Review application health.
- Review failed logins and suspicious shares.
- Review backup status.
- Review disk, database, and server capacity.
- Record incidents and user questions.

### Weekly

- Review user/group membership.
- Review public links and expiries.
- Verify a sample restore.
- Review AWS cost and forecast.
- Review Nextcloud background jobs and logs.
- Apply approved security updates during a maintenance window.

### At Day 30

1. Review actual AWS spend against the estimate.
2. Review CPU, memory, disk, RDS, storage, traffic, and concurrency data.
3. Review support volume and feature adoption.
4. Decide whether an RI is financially and operationally justified.
5. Review the permission matrix and departed users.
6. Perform a formal restore drill.
7. Update the capacity and cost forecast.
8. Close temporary project access if not needed for support.

---

## 13. Rollback and Incident Procedures

### Failed deployment before migration

1. Put Nextcloud in maintenance mode.
2. Preserve logs and configuration.
3. Restore the previous known-good AMI or database snapshot.
4. Re-run health checks.
5. Notify the project owner.
6. Record the cause and recovery time.

### Migration failure

1. Stop the transfer process.
2. Keep the source unchanged.
3. Preserve transfer logs and failed-file list.
4. Identify whether failure is bandwidth, permissions, file names, capacity, or application-related.
5. Retry only the failed batch after correcting the cause.
6. Do not delete the source until signed reconciliation.

### Suspected compromised account

1. Disable the affected user immediately.
2. Revoke sessions and shares.
3. Preserve application, CloudTrail, and network logs.
4. Rotate affected credentials.
5. Check recent downloads, shares, deletes, and administrative events.
6. Restore affected files from versions or backups if required.
7. Notify the firm's incident owner.
8. Record the incident and corrective action.

### Accidental deletion

1. Identify the file, user, path, and deletion time.
2. Try user trash restore.
3. Try version restore.
4. Use admin recovery if needed.
5. Use S3/EBS/RDS recovery only when application-level recovery is insufficient.
6. Record the result and update the support log.

---

## 14. Final Completion Checklist

- [ ] Commercial quotation, scope, feature count, and exclusions are internally consistent.
- [ ] Firm-owned AWS account is protected with MFA.
- [ ] Production resources are tagged and located in the approved region.
- [ ] Database is private and encrypted.
- [ ] Application is patched, hardened, monitored, and backed up.
- [ ] Domain and HTTPS are operational with renewal tested.
- [ ] Approved apps are installed and version-recorded.
- [ ] User and permission matrix is tested.
- [ ] 150 GB migration is reconciled with checksum evidence.
- [ ] Trash, version, snapshot, archive, and restore processes are tested.
- [ ] CloudTrail, S3 data events, application audit, and retention are evidenced.
- [ ] UAT is signed and known issues are accepted.
- [ ] Training is completed.
- [ ] Handover documents are delivered.
- [ ] Temporary credentials and access are removed.
- [ ] Go-live approval is signed.
- [ ] Day-30 review is scheduled.

**Project completion condition:** every checked item has an owner, date, evidence location, and reviewer.
