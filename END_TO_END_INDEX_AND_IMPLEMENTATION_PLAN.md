# Secure Cloud Document Management System
## End-to-End Index and Implementation Plan

**Prepared from:**

- [LOGESH_Quotation for Secure Cloud Document Management System.pdf](LOGESH_Quotation%20for%20Secure%20Cloud%20Document%20Management%20System.pdf)
- [Secure Cloud Document Management & Collaboration Platform Feature Document.pdf](Secure%20Cloud%20Document%20Management%20%26%20Collaboration%20Platform%20Feature%20Document.pdf)

**Prepared for:** CS. T. Saraswathi, B.Com., FCS  
**Prepared by:** Logesh P S  
**Target region:** AWS Mumbai (`ap-south-1`)  
**Target users:** 10 initial accounts, including 5 rotating trainees  
**Initial migration:** 150 GB  
**Target delivery:** 20 working days from signed quotation, advance, and client inputs

---

## 1. Executive Index

| Area | Source | Indexed content | Delivery implication |
|---|---|---:|---|
| Commercial quotation | Quotation | Sections 1–15 | Scope, fees, payment, assumptions, support, exclusions |
| Solution architecture | Both | AWS + Nextcloud stack | Requires security, backup, monitoring, and ownership decisions |
| Product capabilities | Feature document | 15 categories, 166 coded features | Requires a capability baseline and phased acceptance testing |
| Migration | Both | 150 GB from existing hard drives | Requires source inventory, checksum method, staged transfer, reconciliation |
| Governance | Both | Permissions, audit, ownership, support | Requires signed access matrix, retention policy, and handover controls |
| Commercial baseline | Quotation | INR 40,000 services + approx. INR 1,000 domain + AWS | AWS pricing must be revalidated before commitment |

### Important document controls

1. The feature document contains **166 feature codes**, not 130+. The “130+” statement should be corrected or qualified before client issue.
2. “Latest LTS” is time-sensitive. Pin the exact Nextcloud, Ubuntu, PHP, Collabora, Redis, and app versions in the solution design.
3. “Indefinite” audit retention, “5–10 year” Glacier retention, cross-availability-zone backup, immutable backups, and end-to-end encryption are design choices that need explicit AWS and Nextcloud configuration evidence.
4. “Full audit trail of every user action” must be tested against the actual events captured by Nextcloud Activity, CloudTrail management events, S3 data events, and application logs.
5. AWS estimates are approximate and should be recalculated using the final instance sizes, storage classes, traffic, backup retention, taxes, and email/video requirements.
6. The quotation has no Section 7.5 in the supplied text. Renumber or add the missing subsection before final issue.
7. “AWS account setup” should be handled through a firm-owned root account. The implementer should receive delegated least-privilege access, never the firm's root credentials.
8. “Full Microsoft-Word-compatible editor” and similar compatibility claims should be replaced with acceptance-tested compatibility language.

---

## 2. Source Document Index

### 2.1 Quotation: commercial and delivery index

| Section | Topic | Key contents | Implementation gate |
|---|---|---|---|
| Cover | Parties and quotation identity | Quotation number, date, client, preparer, GST note | Confirm legal names, contact details, validity date |
| 1 | Executive summary | 10 users, 150 GB, web/desktop/mobile, audit, three-layer backup, India residency | Approve target outcome and success criteria |
| 2 | Glossary | Cloud, AWS, Nextcloud, EC2, S3, RDS, DNS, TLS, encryption, backup, RI, bandwidth | Confirm client understands cost and technology terms |
| 3 | Solution overview | Nextcloud, EC2, S3, RDS, Route 53, CloudTrail, AWS Backup | Approve architecture and ownership model |
| 4 | One-time deliverables | 14 deliverables from architecture through ongoing support | Convert each deliverable into an acceptance test |
| 5 | One-time costs | INR 40,000 professional services; approx. INR 1,000 domain | Confirm payment recipient and tax wording |
| 6 | Recurring AWS costs | On-demand approx. INR 6,200; RI estimate approx. INR 5,000 | Recalculate with AWS Pricing Calculator |
| 7 | Month-by-month cost | Setup month, steady state, RI, annual renewal, forecast | Approve billing owner and budget guardrails |
| 8 | Payment milestones | INR 8,000 advance, INR 16,000 migration, INR 16,000 go-live | Define objective milestone evidence |
| 9 | Timeline | 20 working days, nine phases | Confirm client availability and dependencies |
| 10 | Assumptions/prerequisites | Account, users, source data, bandwidth, domain, UAT/training | Obtain signed prerequisite checklist |
| 11 | Exclusions | Domain and AWS paid directly by client | Confirm no hidden pass-through or subscription items |
| 12 | Ongoing support | Included support for delivered scope; exclusions for new work | Define support intake, severity, and boundaries |
| 13 | Confidentiality | NDA option, no retained data, credential handover | Execute NDA and deletion/handover record |
| 14 | Terms | Validity, pass-through, change control, ownership | Obtain acceptance of commercial/legal terms |
| 15 | Grand-total card | One-time, monthly, first-month, support summary | Ensure all totals match detailed sections |

### 2.2 Feature document: category index

| Section | Category | Codes | Count | Primary acceptance theme |
|---|---|---|---:|---|
| A | File Storage & Management | A1–A18 | 18 | Files, folders, search, metadata, locking |
| B | Document Editing | B1–B14 | 14 | Office editing, collaboration, PDF/signature |
| C | Sharing & Collaboration | C1–C11 | 11 | Internal and external sharing controls |
| D | Team Communication | D1–D15 | 15 | Talk chat, calls, rooms, notifications |
| E | Calendar, Contacts, Tasks | E1–E14 | 14 | Groupware synchronization and scheduling |
| F | Task & Work Tracking | F1–F9 | 9 | Deck boards, assignments, due dates |
| G | Access from Any Device | G1–G12 | 12 | Browser, desktop, mobile, WebDAV, sync |
| H | Security | H1–H14 | 14 | TLS, encryption, hardening, anti-virus |
| I | Backup, Recovery & Versions | I1–I11 | 11 | Restore paths, snapshots, archive, immutability |
| J | Audit Log & Compliance | J1–J13 | 13 | Application and AWS audit evidence |
| K | User & Access Management | K1–K12 | 12 | Provisioning, groups, quotas, admin controls |
| L | Data Residency & Ownership | L1–L5 | 5 | India location, account and data ownership |
| M | Customisation & Branding | M1–M6 | 6 | Logo, colours, login, languages, dashboard |
| N | Notifications & Communication | N1–N6 | 6 | In-app, email, mobile, web notifications |
| O | Automation & Rules | O1–O6 | 6 | Rules, retention, requests, jobs, scripting |
|  | **Total** | **A1–O6** | **166** | **Baseline for scope validation** |

---

## 3. Complete Feature Code Index

The feature document is the authoritative detail for each description. This index provides the searchable code-to-capability map used by the delivery plan and test matrix.

### A. File Storage & Management

| Code | Capability |
|---|---|
| A1 | Unlimited folder structure |
| A2 | Drag-and-drop upload |
| A3 | Chunked uploads |
| A4 | Resume-on-failure |
| A5 | Bulk download as ZIP |
| A6 | In-browser file preview |
| A7 | Thumbnails |
| A8 | Full-text search |
| A9 | File tags |
| A10 | Favourites / starred items |
| A11 | Comments on files |
| A12 | File-level activity log |
| A13 | Metadata sidebar |
| A14 | External storage mounts |
| A15 | File locking |
| A16 | Move/copy across shared folders |
| A17 | Sort by name, size, date, or tag |
| A18 | Grid or list view |

### B. Document Editing

| Code | Capability |
|---|---|
| B1 | Edit DOCX in browser |
| B2 | Edit XLSX in browser |
| B3 | Edit PPTX in browser |
| B4 | Open Office formats |
| B5 | Real-time co-authoring |
| B6 | Track changes |
| B7 | Comments in documents |
| B8 | Export to PDF |
| B9 | Templates library |
| B10 | Print documents |
| B11 | Save as another format |
| B12 | Version history within editor |
| B13 | Digital signatures on PDF via LibreSign |
| B14 | PDF form filling |

### C. Sharing & Collaboration

| Code | Capability |
|---|---|
| C1 | Share with internal users |
| C2 | Share with groups |
| C3 | Public shareable link |
| C4 | Link expiry date |
| C5 | Link password protection |
| C6 | Disable download |
| C7 | Editable public link |
| C8 | File-request link |
| C9 | Share notifications |
| C10 | Instant revoke |
| C11 | Share summary dashboard |

### D. Team Communication

| Code | Capability |
|---|---|
| D1 | One-to-one text chat |
| D2 | Group chat rooms |
| D3 | Voice calls |
| D4 | Video calls |
| D5 | Screen sharing |
| D6 | File drops in chat |
| D7 | Emoji and message reactions |
| D8 | Voice messages |
| D9 | Message replies and threads |
| D10 | Public chat rooms via link |
| D11 | Chat search |
| D12 | Meeting scheduler |
| D13 | Mobile push notifications |
| D14 | Waiting rooms |
| D15 | Kick and mute controls |

### E. Calendar, Contacts, and Tasks

| Code | Capability |
|---|---|
| E1 | Personal calendar |
| E2 | Shared team calendars |
| E3 | Public read-only calendars |
| E4 | Recurring events |
| E5 | Event reminders |
| E6 | CalDAV synchronization |
| E7 | Meeting scheduler |
| E8 | Files attached to events |
| E9 | Auto-create Talk room from event |
| E10 | Shared address book |
| E11 | CardDAV synchronization |
| E12 | vCard import/export |
| E13 | Tasks and to-do lists |
| E14 | Task categories, due dates, and priorities |

### F. Task and Work Tracking

| Code | Capability |
|---|---|
| F1 | Kanban boards |
| F2 | Cards with title and description |
| F3 | Assign cards to team members |
| F4 | Due dates and reminders |
| F5 | Labels and tags on cards |
| F6 | Card comments |
| F7 | Card attachments linked to files |
| F8 | Subtasks and checklists |
| F9 | Board sharing |

### G. Access from Any Device

| Code | Capability |
|---|---|
| G1 | Web browser access |
| G2 | Windows desktop sync |
| G3 | macOS desktop sync |
| G4 | Linux desktop sync |
| G5 | Android mobile app |
| G6 | iOS mobile app |
| G7 | Automatic photo upload |
| G8 | Mobile offline mode |
| G9 | On-demand file streaming |
| G10 | Selective sync |
| G11 | Bandwidth throttling |
| G12 | WebDAV access |

### H. Security

| Code | Capability |
|---|---|
| H1 | HTTPS/TLS 1.3 in transit |
| H2 | AES-256 encryption at rest |
| H3 | Optional end-to-end encrypted folders |
| H4 | Password policy enforcement |
| H5 | Brute-force protection |
| H6 | IP whitelist/blacklist |
| H7 | Session timeout |
| H8 | Rate limiting |
| H9 | Trusted domains |
| H10 | Content Security Policy |
| H11 | ClamAV upload scanning |
| H12 | AWS data-centre security |
| H13 | AWS network hardening |
| H14 | Ubuntu server hardening |

### I. Backup, Recovery, and Version Control

| Code | Capability |
|---|---|
| I1 | Per-user trash bin |
| I2 | File version history |
| I3 | Self-service version restore |
| I4 | Bulk restore from trash |
| I5 | Admin override restore |
| I6 | S3 object versioning |
| I7 | Daily EBS snapshots |
| I8 | Daily RDS snapshots |
| I9 | Glacier Deep Archive |
| I10 | Cross-availability-zone backup |
| I11 | Ransomware protection / immutable backups |

### J. Audit Log and Compliance

| Code | Capability |
|---|---|
| J1 | Every login recorded |
| J2 | Failed logins recorded |
| J3 | File events recorded |
| J4 | Share events recorded |
| J5 | Administrative actions recorded |
| J6 | Filter by user |
| J7 | Filter by date range |
| J8 | Filter by action type |
| J9 | Filter by file/folder |
| J10 | CSV export |
| J11 | AWS CloudTrail infrastructure events |
| J12 | S3 data event logging |
| J13 | Log retention |

### K. User and Access Management

| Code | Capability |
|---|---|
| K1 | Individual user creation |
| K2 | Bulk CSV user creation |
| K3 | Group management |
| K4 | Per-user storage quota |
| K5 | Enable/disable user |
| K6 | Admin password reset |
| K7 | Sub-admin roles |
| K8 | Audited impersonation |
| K9 | Per-folder permission matrix |
| K10 | App management |
| K11 | System health dashboard |
| K12 | Admin log viewer |

### L. Data Residency and Ownership

| Code | Capability |
|---|---|
| L1 | Data physically stored in India |
| L2 | Firm owns AWS account |
| L3 | Firm owns cloud storage contents |
| L4 | Full data export |
| L5 | Standard file formats retained |

### M. Customisation and Branding

| Code | Capability |
|---|---|
| M1 | Custom firm logo |
| M2 | Custom brand colours |
| M3 | Custom login page |
| M4 | Dark and light mode |
| M5 | Multi-language interface |
| M6 | Configurable dashboard |

### N. Notifications and Communication

| Code | Capability |
|---|---|
| N1 | In-app notifications |
| N2 | Email notifications |
| N3 | Mobile push notifications |
| N4 | Web push notifications |
| N5 | @mentions in comments |
| N6 | Per-user notification preferences |

### O. Automation and Rules

| Code | Capability |
|---|---|
| O1 | Auto-tagging rules |
| O2 | Auto-moving files by rule |
| O3 | Retention policies |
| O4 | File-request folders |
| O5 | Command-line automation |
| O6 | Background job scheduler |

---

## 4. End-to-End Architecture Index

```text
Users: browser | Windows/macOS/Linux sync | Android/iOS | WebDAV
                 |
             DNS / TLS
                 |
          Nginx reverse proxy
                 |
       Nextcloud application server
        Ubuntu + PHP-FPM + Redis
          /          |            \
       RDS MySQL   S3 files       Talk/Office services
          |          |              |
   AWS Backup     Versioning      Collabora / Talk
          |
   Audit and operations:
   CloudTrail + S3 data events + CloudWatch + alarms
          |
   Recovery:
   EBS/RDS snapshots + versioned backup + Glacier archive
```

### Required architecture decisions

| Decision | Recommended baseline | Evidence required |
|---|---|---|
| AWS account | Firm-owned account with delegated administrator role | Account ownership and IAM review |
| Region | Mumbai `ap-south-1` for in-scope data | Region configuration screenshots/export |
| Network | VPC, private database, restricted security groups | Route and security-group review |
| Application | Ubuntu 24.04 LTS, Nginx, PHP-FPM, Nextcloud LTS | Version manifest |
| Performance | Redis caching; sizing validated under UAT load | Load and health results |
| File storage | S3 with encryption and versioning | Bucket policy and encryption evidence |
| Database | RDS MySQL, private access, automated backups | RDS configuration and restore test |
| TLS | Custom domain with auto-renewing certificate | External TLS scan and renewal test |
| Audit | Nextcloud Activity plus CloudTrail/S3 data events | Sample CSV and CloudTrail event |
| Recovery | Trash, versions, snapshots, archive, documented restore | Restore drill record |
| Operations | CloudWatch alarms, patching, log review, support process | Runbook and alarm test |

---

## 5. Delivery Plan: 20 Working Days

| Phase | Days | Work | Outputs | Exit criteria |
|---|---:|---|---|---|
| 0. Mobilise | 1–3 | Confirm scope, users, roles, folders, domain, AWS ownership, source inventory | Signed requirements, access matrix, migration manifest | Client inputs complete |
| 1. Foundation | 4–5 | Firm AWS account, IAM roles, VPC, subnets, security groups, KMS/encryption, billing alerts, DNS | Architecture diagram, account baseline | Security review passed |
| 2. Platform | 6–7 | EC2/Ubuntu, Nginx, PHP-FPM, Nextcloud LTS, Redis, firewall, patching, hardening | Running private platform | Health checks green |
| 3. Collaboration apps | 8 | Collabora, Talk, Groupware, Deck, Time Manager, LibreSign, required mail/push settings | App configuration record | Smoke tests passed |
| 4. Identity and permissions | 9–10 | Create groups/users, quotas, folder structure, role matrix, admin/sub-admin controls, audit settings | User and permissions register | Negative access tests passed |
| 5. Migration | 11–15 | Inventory, staged upload, checksum comparison, retry failed items, reconcile counts and sizes | Migration report and exception list | 150 GB verified or exceptions signed |
| 6. Resilience and operations | 16–17 | Snapshots, S3 versioning, Glacier policy, CloudTrail, CloudWatch, alarms, restore runbook | Backup configuration and DR procedure | Restore drill completed |
| 7. UAT | 18 | Partners/staff test priority workflows and record defects | UAT evidence and issue log | Critical defects closed |
| 8. Training | 19 | Admin and end-user sessions | Attendance, guide, recording or notes | Users complete key tasks |
| 9. Go-live and handover | 20 | Credential rollover, DNS confirmation, final migration delta, documentation handover | Handover pack and sign-off | Go-live approval obtained |

### Milestone payment evidence

| Milestone | Amount | Objective evidence |
|---|---:|---|
| Advance | INR 8,000 | Signed quotation and mobilisation confirmation |
| Migration complete | INR 16,000 | Source/destination counts, checksums, exceptions, client verification |
| Go-live and training | INR 16,000 | UAT sign-off, training completion, documentation, credential handover |

---

## 6. Feature Delivery Mapping

| Workstream | Feature codes | Priority | Validation method |
|---|---|---|---|
| Core files | A1–A18 | Must-have | Upload, search, preview, version, lock, move, restore |
| Office and signing | B1–B14 | Must-have / verify compatibility | DOCX/XLSX/PPTX edit, co-author, export, sign, restore |
| Sharing | C1–C11 | Must-have | Internal, group, public, expiry, password, revoke, upload-only |
| Talk | D1–D15 | Should-have | Chat, call, room, file drop, moderation, notifications |
| Groupware | E1–E14 | Should-have | Calendar/contact/task sync and reminders |
| Work tracking | F1–F9 | Should-have | Board, assignment, due date, comment, attachment, sharing |
| Device access | G1–G12 | Must-have | Browser, desktop/mobile sync, offline/selective sync, WebDAV |
| Security | H1–H14 | Must-have | TLS scan, policy tests, firewall, anti-virus, hardening review |
| Recovery | I1–I11 | Must-have | Delete/restore, snapshot restore, archive policy, immutability |
| Audit | J1–J13 | Must-have | Generate events, filter, export, CloudTrail correlation, retention |
| Administration | K1–K12 | Must-have | User lifecycle, quotas, groups, admin delegation, health/log view |
| Ownership | L1–L5 | Must-have | Region/account/export/format verification |
| Branding | M1–M6 | Should-have | Login and UI branding, themes, language, dashboard |
| Notifications | N1–N6 | Should-have | Email, in-app, push/web push, mentions, preferences |
| Automation | O1–O6 | Optional / verify app availability | Rule execution, retention safeguards, jobs, CLI |

### Acceptance priority

- **Must-have:** identity, permissions, core files, migration, TLS, encryption, backups, audit, ownership, recovery, handover.
- **Should-have:** Office, Talk, Groupware, Deck, device clients, notifications, branding.
- **Optional or compatibility-dependent:** end-to-end encrypted folders, external storage mounts, advanced Talk scale, automation rules, web push, full Office feature compatibility, third-party sync behavior.

---

## 7. UAT and Operational Acceptance Checklist

### Identity and permissions

- [ ] All 10 accounts exist and are assigned to the approved groups.
- [ ] Partner, Senior, Junior, and Trainee access matches the signed matrix.
- [ ] A trainee can be disabled immediately and loses access.
- [ ] Users cannot access folders outside their assigned scope.
- [ ] Admin and sub-admin privileges are least-privilege and audited.

### Files and migration

- [ ] Folder tree is preserved.
- [ ] Source and destination file counts match, or every exception is documented.
- [ ] Checksums are recorded for the agreed migration set.
- [ ] Large, interrupted, duplicate, renamed, and locked files are tested.
- [ ] Search, preview, tags, comments, versions, and ZIP download work.

### Editing and collaboration

- [ ] DOCX, XLSX, PPTX, PDF, ODT, ODS, and ODP test files behave acceptably.
- [ ] Two users can co-edit a test document.
- [ ] Version restore works after an edit.
- [ ] PDF signing and form filling are tested with client-approved samples.

### Sharing and communication

- [ ] Internal and group shares enforce the intended rights.
- [ ] Public links support password, expiry, download restriction, and revoke tests.
- [ ] File-request links cannot expose existing files.
- [ ] Talk chat, calls, moderation, and file sharing are tested.
- [ ] Calendar, contact, task, email, and mobile notifications are tested where configured.

### Security and operations

- [ ] HTTPS certificate is valid, auto-renewal is proven, and only intended domains are trusted.
- [ ] Database is not publicly reachable.
- [ ] Failed login throttling, password policy, session timeout, firewall, and anti-virus are tested.
- [ ] CloudTrail and S3 data events produce searchable evidence.
- [ ] CloudWatch alarms notify the agreed administrator.
- [ ] Patch, incident, access review, and log review procedures are documented.

### Recovery and handover

- [ ] User trash restore works.
- [ ] Version restore works.
- [ ] Admin recovery path works.
- [ ] EBS and RDS restore drills are recorded.
- [ ] S3 versioning and immutable/archive controls are verified.
- [ ] Firm receives architecture, admin runbook, quick-start guide, backup/restore procedure, credentials, and export instructions.
- [ ] Temporary implementation access is removed after handover.

---

## 8. Risk, Assumption, and Dependency Register

| ID | Risk/dependency | Impact | Mitigation / decision |
|---|---|---|---|
| R1 | Client delays user and permission matrix | Timeline slips | Freeze inputs by Day 3; use change control afterward |
| R2 | 20 Mbps upload is insufficient for 150 GB | Migration exceeds window | Measure actual throughput; use staged overnight migration and final delta |
| R3 | Office/Collabora compatibility varies by document | User dissatisfaction | Test representative client files before acceptance |
| R4 | Public links or Talk expose additional attack surface | Security incident | Default-deny sharing policy, expiry, passwords, logging, UAT abuse tests |
| R5 | AWS costs exceed estimate | Budget variance | Billing alerts, budgets, monthly review, pricing recalculation, no unapproved RI |
| R6 | “Indefinite” retention increases cost and compliance burden | Cost and legal ambiguity | Obtain written retention period, legal hold, deletion, and access policy |
| R7 | Single application server is a recovery bottleneck | Longer outage | Document RTO/RPO; test rebuild/restore and consider standby as a later option |
| R8 | External mail, push, and mobile services are not configured | Notifications fail | Confirm SMTP, mobile push, firewall, and DNS requirements before Phase 3 |
| R9 | Feature claims depend on app/version/configuration | Scope dispute | Mark each feature Must-have, Should-have, Optional, or Compatibility-dependent |
| R10 | Root credentials are shared with implementer | Account compromise | Firm retains root; delegated IAM role with MFA and expiry |
| R11 | Feature total mismatch: 130+ vs 166 | Proposal credibility | Correct count before client issue |
| R12 | GST and legal wording may require professional confirmation | Commercial dispute | Have the provider/client verify applicable tax and contract wording |

---

## 9. Required Handover Pack

1. Final architecture diagram and component/version manifest.
2. AWS account ownership record, IAM roles, MFA, billing alerts, and budget settings.
3. Nextcloud administrator runbook and user quick-start guide.
4. Approved user/group/folder permission matrix.
5. Migration manifest with counts, checksums, exceptions, and sign-off.
6. Backup, restore, retention, and disaster-recovery procedure.
7. UAT test results and unresolved known-issue list.
8. CloudTrail, S3 data-event, Nextcloud Activity, and log-retention configuration evidence.
9. Monitoring dashboard, alarms, patching schedule, and support contacts.
10. Domain/DNS/TLS renewal ownership and instructions.
11. Export procedure for files, database, configuration, and audit records.
12. Credential rollover record and removal of temporary implementation access.
13. Confidentiality/NDA and data-destruction confirmation, where applicable.

---

## 10. Recommended Next Actions

### Before approval

1. Correct “130+” to “166” or intentionally reduce the committed feature baseline.
2. Replace placeholders such as `yourfirm.co.in` and `files.yourfirm.co.in` with the chosen domain.
3. Confirm the exact AWS architecture, RTO/RPO, retention periods, notification providers, and expected Talk meeting size.
4. Recalculate AWS costs and state whether GST, taxes, data transfer, email, and optional services are included.
5. Convert the feature index and UAT checklist into an agreed scope annexure.

### Immediately after approval

1. Open or verify the firm-owned AWS account and enable MFA, budgets, and billing alerts.
2. Obtain the user/role/folder permission matrix and source-data inventory.
3. Capture representative Office/PDF files for compatibility testing.
4. Measure upload bandwidth and choose migration windows.
5. Confirm domain registrar, DNS ownership, SMTP, mobile push, and support contacts.

### Before go-live

1. Complete UAT with signed evidence.
2. Complete at least one restore drill from each recovery layer that is claimed as production-ready.
3. Review public-sharing defaults and administrator access.
4. Perform final migration delta and reconcile checksums.
5. Roll over credentials, remove temporary access, and obtain formal go-live sign-off.

---

## 11. Definition of Done

The project is complete when:

- The firm-owned AWS environment is operational in Mumbai with documented ownership.
- The approved user and permission matrix is enforced and tested.
- The agreed 150 GB migration is reconciled with checksum evidence and signed exceptions.
- Must-have features in the delivery mapping pass UAT.
- TLS, encryption, backups, audit logging, monitoring, and restore procedures are evidenced.
- The client receives the complete handover pack and training.
- Temporary access is removed and ongoing support boundaries are understood.
- Commercial totals, feature count, assumptions, exclusions, and retention claims are internally consistent.

**End of index and plan.**
