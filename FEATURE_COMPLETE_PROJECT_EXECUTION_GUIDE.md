# Secure Cloud Document Management System
## Feature-Complete Project Execution Guide

This guide explains how to execute the project end to end so that the promised AWS + Nextcloud solution is not just deployed, but delivered with the specified features working, tested, and documented.

It assumes the target remains:

- AWS Mumbai region: `ap-south-1`
- Nextcloud as the application platform
- 10 initial users
- 150 GB starting data volume
- Firm-owned AWS account and domain
- Delivery goal within 20 working days

This document is intentionally practical. It is organized in the order the project should actually be done, with dependencies, build steps, configuration goals, feature-enablement steps, and validation steps.

---

## 1. What "Feature-Complete" Means

A platform is only feature-complete when all four conditions are true:

1. The infrastructure exists and is secure.
2. The feature is enabled in the correct component.
3. The feature works for the intended user roles.
4. The feature has evidence: screenshot, export, test result, log, or sign-off.

For this project, that means you cannot stop at:

- server provisioned,
- Nextcloud installed,
- apps enabled,
- or data uploaded.

You must also prove:

- permissions work,
- search works,
- document editing works,
- sharing controls work,
- audit logs capture the required actions,
- backups restore correctly,
- admin operations are usable,
- and the client has been trained and handed over the operating procedure.

---

## 2. Delivery Strategy

Use this exact strategy:

1. Build the platform foundation first.
2. Secure it before bulk data arrives.
3. Enable only the approved apps.
4. Configure users, groups, and permissions before migration.
5. Migrate a small pilot batch before the full 150 GB.
6. Configure backup and audit before go-live.
7. Test each feature group with sample data before business data is fully handed over.
8. Run UAT using the exact feature codes and workflows promised in the feature document.

Do not invert this order.

---

## 3. Implementation Phases

| Phase | Objective | Main output |
|---|---|---|
| Phase 0 | Finalize scope and inputs | Approved scope, feature baseline, user matrix |
| Phase 1 | Build AWS foundation | Firm-owned secure AWS environment |
| Phase 2 | Deploy Nextcloud platform | Working base system with HTTPS |
| Phase 3 | Enable apps and core services | Office, Talk, Groupware, Deck, signing |
| Phase 4 | Configure identity and permissions | Roles, groups, quotas, access matrix |
| Phase 5 | Migrate validated data | 150 GB uploaded and reconciled |
| Phase 6 | Configure resilience and observability | Backup, restore, logs, alarms |
| Phase 7 | Validate every promised feature | UAT and admin acceptance evidence |
| Phase 8 | Train and hand over | Live service with documentation |

---

## 4. Phase 0: Scope Freeze and Design Lock

### Step 4.1: Freeze the committed feature baseline

Use the feature document and classify every feature as one of:

- `GO-LIVE REQUIRED`
- `GO-LIVE IF SUPPORTED BY CHOSEN VERSION`
- `POST-GO-LIVE OPTIONAL`
- `EXCLUDED`

Do not leave any feature unclassified.

### Step 4.2: Resolve the feature-count inconsistency

The document says `130+` features, but the coded list is `166`. Before client sign-off:

1. Correct the feature document to say `166 coded features`, or
2. publish a reduced committed baseline and clearly show what is excluded.

### Step 4.3: Pin the technology versions

Do not deploy from vague labels like `latest` or `LTS` alone. Record exact versions for:

- Ubuntu
- Nginx
- PHP
- Nextcloud
- Redis
- RDS MySQL
- Collabora / Nextcloud Office integration
- Talk
- Calendar
- Contacts
- Tasks
- Deck
- LibreSign
- ClamAV

### Step 4.4: Define acceptance standards

For each feature family, define what “working” means. Example:

- `A8 Full-text search`: searchable results from uploaded PDF and DOCX samples.
- `B5 Real-time co-authoring`: two users edit the same DOCX and see each other’s changes.
- `J10 CSV export`: administrator can export filtered audit events into CSV.
- `I8 Daily RDS snapshots`: snapshot job exists and restore to a test instance succeeds.

---

## 5. Phase 1: AWS Foundation

## 5.1 Create the AWS account correctly

1. Open the AWS account in the firm’s name.
2. Enable MFA on root immediately.
3. Remove root access keys.
4. Set billing alerts and budgets.
5. Restrict operational access to delegated IAM roles only.

### 5.2 Create the network layout

Use a clear layout:

- Public subnet for the web-facing entry if required.
- Private subnet for the app server where practical.
- Private database subnets across two AZs.
- No public RDS.
- Security groups with least privilege.

### 5.3 Create the core AWS services

Provision:

- EC2 for the Nextcloud app host.
- RDS MySQL for metadata.
- S3 for object/file storage.
- Route 53 for DNS.
- CloudTrail for AWS-side audit.
- CloudWatch for metrics and alarms.
- AWS Backup or equivalent snapshot policy.
- Glacier or lifecycle-managed archive path.

### 5.4 Encrypt everything appropriate

Enable encryption for:

- EBS volumes.
- RDS storage and snapshots.
- S3 bucket.
- Backup vault.
- Trail/log storage where required.

### 5.5 Set budgets and operational alerts

At minimum alert on:

- cost threshold,
- CPU,
- memory,
- disk,
- RDS storage,
- backup failures,
- certificate expiry,
- abnormal transfer,
- repeated failed logins.

### Exit criteria for Phase 1

- Firm owns the account.
- Region is Mumbai.
- Database is private.
- Encryption is enabled.
- Budgets and alarms work.
- CloudTrail is recording events.

---

## 6. Phase 2: Base Platform Deployment

### 6.1 Provision the app host

Deploy Ubuntu 24.04 LTS or the final approved version. Configure:

- IMDSv2 only
- patched OS
- no broad public SSH
- SSM or restricted admin access
- CloudWatch agent
- automatic security updates
- UFW and fail2ban

### 6.2 Install the runtime stack

Install and verify:

- Nginx
- PHP-FPM with required modules
- Redis
- certbot or approved ACME tooling
- database client tools
- image/PDF helpers if needed for previews/search
- antivirus tools if `H11` is in scope

### 6.3 Deploy Nextcloud

1. Download the exact pinned release.
2. Verify checksum/signature.
3. Place the data directory outside the web root.
4. Use RDS for the database.
5. Configure Redis for caching and file locking.
6. Set trusted domains.
7. Set background jobs to cron.
8. Set upload limits and timeouts for large files.
9. Configure phone region, locale, and timezone.

### 6.4 Configure HTTPS

1. Create the DNS record for `files.<firm-domain>`.
2. Issue the certificate.
3. Enforce HTTPS.
4. Add the required security headers.
5. Test certificate renewal.

### Exit criteria for Phase 2

- Login page works over HTTPS.
- Nextcloud health warnings are resolved or documented.
- Cron jobs run.
- Redis is active.
- RDS is connected privately.
- Sample file upload works.

---

## 7. Phase 3: App Enablement

Enable only apps that are part of the promised scope.

### 7.1 Office editing

Enable Nextcloud Office / Collabora and then test:

- DOCX open/edit/save
- XLSX open/edit/save
- PPTX open/edit/save
- ODT/ODS/ODP support
- version restore after edits
- export to PDF
- two-user co-authoring

### 7.2 Talk

Enable Talk and test:

- 1:1 chat
- group room creation
- audio call
- video call
- file attachment in chat
- waiting room if required
- mute/kick permissions
- mobile notification path

### 7.3 Groupware

Enable and validate:

- Calendar
- Contacts
- Tasks
- CalDAV
- CardDAV
- shared calendars
- reminders
- event attachments
- shared address book

### 7.4 Work tracking

Enable and validate:

- Deck
- card assignments
- due dates
- labels
- checklists
- attachments to Nextcloud files

### 7.5 Signing and optional tools

Enable and validate:

- LibreSign for PDF signing if committed
- Time Manager if committed
- any email delivery integration needed by notifications and reminders

### Exit criteria for Phase 3

- All approved apps are installed.
- Versions are recorded.
- Sample workflows work.
- Unsupported claims are identified now, not at go-live.

---

## 8. Phase 4: Identity, Permissions, and Policy

### 8.1 Build the role model

Create at least:

- Firm-Admins
- Firm-Partners
- Firm-Seniors
- Firm-Juniors
- Firm-Trainees
- Firm-Departed

### 8.2 Create the user accounts

1. Create the 10 users.
2. Apply quota if required.
3. Enforce reset or invitation flow.
4. Apply only the needed groups.
5. Disable self-service features if policy requires it.

### 8.3 Build the folder model

Create the approved top-level structure and permission inheritance. Keep the model simple enough for the firm to maintain later.

### 8.4 Apply security policies

Implement:

- password policy
- brute-force protection
- session timeout
- rate limiting
- trusted domains
- admin-access restrictions
- antivirus upload scanning if in scope
- app-management restrictions

### 8.5 Configure audit and admin controls

1. Enable relevant Nextcloud logging.
2. Confirm CloudTrail and S3 object logging where applicable.
3. Validate impersonation and admin audit.
4. Validate CSV export and filters.

### Exit criteria for Phase 4

- Users and groups exist.
- Permissions pass positive and negative tests.
- Security policies are active.
- Admin can view logs and health.

---

## 9. Phase 5: Data Migration

### 9.1 Prepare source data

Use the `CHAT_EXPORT` toolkit to identify and structure source folders before the cloud move.

Recommended sequence:

1. Refresh `source_lists` if needed.
2. Use the final reconciliation workbook `(12).xlsx` as the master path map.
3. Resolve unresolved paths through `NOT FOUND - REVIEW.xlsx`.
4. Optionally copy matched content into a structured staging tree.

### 9.2 Pilot migration

Before all 150 GB:

1. Upload one template folder.
2. Upload one representative client folder.
3. Upload one mixed-format folder with PDFs, images, DOCX, XLSX, and PPTX.
4. Verify previews, editability, permissions, tags, versions, restore, and search.

### 9.3 Full migration

1. Freeze the source set for the batch.
2. Upload in approved windows.
3. Preserve folder structure.
4. Record counts and bytes.
5. Record failed files.
6. Re-run only failures.
7. Perform a final delta after source freeze.

### 9.4 Integrity verification

Use checksum-based or equivalent integrity validation for the agreed scope. Keep a signed migration report.

### Exit criteria for Phase 5

- All in-scope data is uploaded or listed as approved exceptions.
- Folder structure is preserved.
- A client validates representative content.
- Search, preview, and Office behavior work on real data.

---

## 10. Phase 6: Backup, Recovery, Monitoring, and Compliance

### 10.1 Enable the three safety nets

Implement:

1. Nextcloud trash and version history.
2. S3 versioning.
3. AWS snapshots and long-term archive.

### 10.2 Configure restore paths

Test:

- user restore from trash
- version restore from sidebar
- admin recovery path
- S3 version restore
- EBS snapshot restore
- RDS snapshot restore
- archive retrieval

### 10.3 Configure compliance evidence

Collect proof for:

- login events
- failed logins
- view/download/edit/share/delete/restore actions
- admin actions
- AWS API events
- object access events where claimed
- log retention
- CSV export

### Exit criteria for Phase 6

- Restore drills succeed.
- Monitoring notifications are received.
- Audit evidence exists and is searchable.
- DR runbook is written.

---

## 11. Phase 7: Feature-by-Feature Enablement Guide

This section tells you how to make each promised feature family work.

## A. File Storage & Management

### Required platform components

- Nextcloud Files app
- correctly sized PHP upload limits
- correct web-server timeout settings
- previews enabled
- search/indexing as supported
- tagging/comments/activity enabled
- file locking with Redis

### How to deliver Section A

1. Enable file previews for PDFs, images, and supported Office files.
2. Increase upload limits for large files and long-running uploads.
3. Ensure chunked upload behavior is enabled by default in the client and server settings.
4. Configure Redis locking to prevent edit collisions.
5. Enable activity, comments, tags, favourites, and metadata sidebar.
6. Validate sorting and grid/list options in the UI.
7. Configure or verify full-text search capability if it is being promised, including the indexing component required by the chosen Nextcloud version and app stack.
8. Verify external storage mounts only if the business actually needs them.

### Must-test outcomes for A1-A18

- A1 folder depth creation works.
- A2-A4 large upload and interrupted upload recovery work.
- A5 ZIP download works for a representative folder.
- A6-A7 preview and thumbnails work.
- A8 full-text search returns content hits from sample files.
- A9-A13 tagging, stars, comments, metadata, and per-file activity are visible.
- A14 external mount works only if explicitly enabled.
- A15 file locking prevents unsafe concurrent modification paths.
- A16-A18 copy/move, sort, and grid/list work for all users.

## B. Document Editing

### Required platform components

- Nextcloud Office / Collabora
- compatible sample files
- stable CPU/memory sizing
- version history active
- PDF/signature components where promised

### How to deliver Section B

1. Install and configure Office integration.
2. Test on real client-like documents, not only vendor demos.
3. Build a template library folder and permissions model.
4. Confirm version-history restore inside the editor.
5. Test two-user co-authoring on DOCX and XLSX.
6. Enable or configure PDF signing and PDF forms only if the selected app/version truly supports the promised behavior.

### Must-test outcomes for B1-B14

- B1-B4 open/edit/save for DOCX, XLSX, PPTX, ODT, ODS, ODP.
- B5 co-authoring between two users.
- B6 track changes on a Word-style sample.
- B7 in-document comments persist.
- B8 export to PDF works.
- B9 templates are centrally accessible.
- B10 print path works.
- B11 save-as another format works on sample files.
- B12 editor-side version history works.
- B13 PDF signing works with the agreed signing flow.
- B14 PDF form filling works on sample forms.

## C. Sharing & Collaboration

### Required platform components

- internal sharing enabled
- group sharing rules
- public link controls
- notification path
- download restriction policy

### How to deliver Section C

1. Set the default sharing policy first.
2. Decide whether public links are allowed by default or only for admins/partners.
3. Enforce expiry and password rules where required.
4. Test upload-only file request behavior.
5. Test link revocation and link access logging.

### Must-test outcomes for C1-C11

- C1-C2 internal and group share rights work.
- C3 public links open correctly.
- C4 expiry cuts off access.
- C5 password protection works.
- C6 download restriction works where supported.
- C7 editable public links are limited and tested carefully.
- C8 upload-only requests do not expose existing files.
- C9 share notifications are delivered.
- C10 revoke blocks access immediately.
- C11 share dashboard is usable by the intended users.

## D. Team Communication

### Required platform components

- Nextcloud Talk
- push and notification path
- browser microphone/camera permissions
- possibly TURN/STUN or signaling adjustments depending on environment

### How to deliver Section D

1. Enable Talk.
2. Test browser permissions in the client’s browsers.
3. Confirm practical participant limits.
4. Decide whether public-link rooms are allowed.
5. Test mobile push if claimed.

### Must-test outcomes for D1-D15

- D1-D2 persistent 1:1 and group chat.
- D3-D4 voice and video.
- D5 screen sharing.
- D6 file drops in chat.
- D7-D9 reactions, voice messages, replies/threads.
- D10 public room access only if allowed.
- D11 message search.
- D12 scheduling integration with calendar.
- D13 mobile push notifications.
- D14 waiting room moderation.
- D15 mute and kick controls.

## E. Calendar, Contacts, Tasks

### Required platform components

- calendar app
- contacts app
- tasks app
- CalDAV/CardDAV support
- notification/email path

### How to deliver Section E

1. Enable the apps.
2. Create firm-wide shared calendars and address books.
3. Test on Outlook, Apple, Thunderbird, or mobile only if those clients are actually in scope.
4. Validate reminders, recurring events, and attachments.

### Must-test outcomes for E1-E14

- E1-E3 personal, shared, and read-only calendars.
- E4 recurring events.
- E5 reminders.
- E6 CalDAV sync.
- E7 meeting scheduler.
- E8 event attachments.
- E9 auto-create Talk room.
- E10 shared address book.
- E11 CardDAV sync.
- E12 vCard import/export.
- E13-E14 tasks, priorities, due dates, categories.

## F. Task & Work Tracking

### Required platform components

- Deck app
- user/group sharing
- integration with file links

### How to deliver Section F

1. Create at least one sample board.
2. Define list structure like `To Do`, `In Progress`, `Done`.
3. Test assignments, due dates, comments, labels, attachments, and sub-tasks.
4. Confirm board sharing by group.

### Must-test outcomes for F1-F9

- Visual boards work.
- Cards can be assigned.
- Reminders and due dates work.
- Labels, comments, attachments, and checklists work.
- Boards can be shared correctly.

## G. Access from Any Device

### Required platform components

- browser access
- desktop clients
- mobile apps
- sync policy
- WebDAV endpoint

### How to deliver Section G

1. Validate browser support on actual user browsers.
2. Configure and test Windows desktop sync first because it is the most likely primary client.
3. Test Android and iOS access with a pilot user.
4. Validate selective sync and bandwidth limits.
5. Confirm WebDAV endpoint and instructions.

### Must-test outcomes for G1-G12

- G1 browser access.
- G2-G4 desktop clients.
- G5-G6 mobile app access.
- G7 auto-photo-upload if required.
- G8 offline mode.
- G9 on-demand or virtual-file behavior if supported by the chosen client version.
- G10 selective sync.
- G11 bandwidth throttling.
- G12 WebDAV connectivity.

## H. Security

### Required platform components

- HTTPS
- encryption at rest
- password policy
- brute-force/rate limiting
- trusted domains
- CSP/security headers
- antivirus if promised
- hardened OS and network

### How to deliver Section H

1. Enforce TLS.
2. Confirm storage encryption in AWS.
3. Implement password and session policy.
4. Configure brute-force protection and fail2ban as appropriate.
5. Restrict the database privately.
6. Add security headers and trusted domains.
7. Enable ClamAV only if you can operationally support it.
8. Document what end-to-end encrypted folders mean operationally before enabling them.

### Must-test outcomes for H1-H14

- H1 HTTPS works and is externally valid.
- H2 encryption at rest is enabled on storage layers.
- H3 end-to-end encrypted folders work only if intentionally enabled and tested.
- H4-H8 password, brute-force, timeout, IP rules, and rate limiting function.
- H9 trusted domains are correct.
- H10 CSP/security headers are present.
- H11 upload scanning works if included.
- H12-H14 AWS, network, and server hardening evidence exists.

## I. Backup, Recovery & Version Control

### Required platform components

- Nextcloud trash
- Nextcloud versions
- S3 versioning
- EBS snapshots
- RDS snapshots
- archive policy

### How to deliver Section I

1. Set trash/version behavior.
2. Enable S3 versioning.
3. Schedule EBS and RDS backups.
4. Implement archive retention.
5. Test every restore path.

### Must-test outcomes for I1-I11

- I1-I5 trash and admin restore paths work.
- I6 S3 versioning is active.
- I7 EBS snapshots exist and can restore.
- I8 RDS snapshots exist and can restore.
- I9 archive exists and retrieval is understood.
- I10 backup copies or resilient placement reflect the agreed design.
- I11 ransomware-resistant retention controls are documented and tested where promised.

## J. Audit Log & Compliance

### Required platform components

- Nextcloud activity/logging
- CloudTrail
- S3 data event logging if claimed
- CSV export capability
- retention policy

### How to deliver Section J

1. Turn on the right app and infrastructure logs.
2. Generate representative events deliberately.
3. Verify filtering by user, date, action, and file.
4. Export CSV.
5. Prove retention settings.

### Must-test outcomes for J1-J13

- J1-J5 event capture works.
- J6-J9 filters work.
- J10 CSV export works.
- J11 CloudTrail events exist.
- J12 data-event logging exists if promised.
- J13 retention is documented and observable.

## K. User & Access Management

### Required platform components

- user admin functions
- groups
- quotas
- sub-admin controls
- app management
- health dashboard
- log viewer

### How to deliver Section K

1. Validate user lifecycle tasks.
2. Create a bulk-create path if trainee batches need it.
3. Apply quotas if the firm wants them.
4. Test sub-admin roles carefully so they are limited.
5. Ensure the admin dashboard and logs are usable without server shell access.

### Must-test outcomes for K1-K12

- individual and CSV user creation.
- groups and quotas.
- instant disable/enable.
- admin reset.
- sub-admin delegation.
- audited impersonation.
- folder permission matrix.
- app management.
- health dashboard and log viewer.

## L. Data Residency & Ownership

### Required platform components

- Mumbai deployment
- firm-owned account
- export capability
- standard file formats

### How to deliver Section L

1. Confirm region on all storage and compute.
2. Ensure the firm controls root account and billing.
3. Document export path for files and data.
4. Avoid proprietary-only storage formats.

### Must-test outcomes for L1-L5

- Region evidence exists.
- Firm controls the AWS account.
- Firm controls the data.
- user/admin export works.
- stored documents retain standard formats.

## M. Customisation & Branding

### Required platform components

- Nextcloud theming/customization controls

### How to deliver Section M

1. Upload the client-approved logo.
2. Configure the brand colours.
3. Customize the login text and footer only after sign-off.
4. Validate theme behavior on desktop and mobile browsers.
5. Enable relevant languages.

### Must-test outcomes for M1-M6

- logo is visible.
- colours are applied.
- login page is branded.
- dark/light mode works if available.
- language switching works.
- dashboard widgets can be configured.

## N. Notifications & Communication

### Required platform components

- email delivery
- in-app notifications
- mobile push path
- browser notification permissions

### How to deliver Section N

1. Configure SMTP or the approved email service.
2. Validate notification generation on shares, mentions, comments, and reminders.
3. Test browser notifications and mobile push separately.
4. Confirm users can control preferences.

### Must-test outcomes for N1-N6

- in-app notices appear.
- email notices are delivered.
- mobile push works for committed workflows.
- web push works where supported.
- mentions generate direct notice.
- users can manage preferences.

## O. Automation & Rules

### Required platform components

- background jobs
- optional rule or workflow apps
- admin CLI
- retention controls

### How to deliver Section O

1. Confirm what automation features are actually supported by the chosen app stack.
2. Enable scheduled background jobs.
3. Implement upload or tagging rules only after confirming the app path and maintenance status.
4. Configure retention carefully to avoid accidental deletion.
5. Document any CLI-based batch processes used by the administrator.

### Must-test outcomes for O1-O6

- auto-tagging works if explicitly enabled.
- auto-moving works if explicitly enabled.
- retention policy works on test data before production use.
- upload-only file request folders work.
- CLI automation path is documented.
- cron/background jobs run successfully.

---

## 12. Phase 8: UAT Structure

Run UAT by feature family, not only by department.

### 12.1 UAT batches

1. Core files and migration.
2. Office editing.
3. Sharing and external collaboration.
4. Talk and communication.
5. Calendar, contacts, tasks, Deck.
6. Security and audit.
7. Recovery and administration.

### 12.2 UAT evidence pack

Collect:

- screenshots
- exported CSVs
- sample share links
- sample restore logs
- sample CloudTrail events
- user sign-off sheet
- known-issues register

---

## 13. What Usually Fails if Not Planned Early

1. Full-text search is promised but not actually indexed.
2. Office editing works on simple files but breaks on real client documents.
3. Public sharing is enabled without strict policy.
4. Mobile push is promised but SMTP/push dependencies were never completed.
5. Backup exists but no one tested restore.
6. Audit logs exist, but not for the exact actions the client expects.
7. End-to-end encrypted folders are enabled without understanding operational tradeoffs.
8. Talk scalability is overstated beyond the real backend capacity.
9. Antivirus scanning is enabled but not monitored.
10. Users receive too many notifications because defaults were not tuned.

---

## 14. Definition of Done for This Project

The project is done only when:

- the platform is live on the firm-owned AWS account,
- the domain and HTTPS work,
- all required users can log in,
- the agreed permission matrix passes tests,
- the 150 GB migration is reconciled,
- every `GO-LIVE REQUIRED` feature has a passing test result,
- backup and restore paths are proven,
- audit and compliance evidence is exportable,
- admin procedures are documented,
- training is completed,
- and temporary implementation access has been removed.

---

## 15. Recommended Reading Order in This Workspace

Use the documents in this order:

1. `CHAT_EXPORT_DETAILED_INDEX.md`
2. `END_TO_END_INDEX_AND_IMPLEMENTATION_PLAN.md`
3. `DETAILED_STEP_BY_STEP_IMPLEMENTATION_RUNBOOK.md`
4. `FEATURE_COMPLETE_PROJECT_EXECUTION_GUIDE.md`
5. `CHAT_EXPORT\README.txt`
6. `CHAT_EXPORT\CHAT SUMMARY.docx`
7. `CHAT_EXPORT\workbooks\BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx`
8. `CHAT_EXPORT\workbooks\NOT FOUND - REVIEW.xlsx`

This gives the operator:

- folder context,
- project scope,
- exact delivery sequence,
- feature-complete implementation instructions,
- and the real migration-preparation artifacts.
