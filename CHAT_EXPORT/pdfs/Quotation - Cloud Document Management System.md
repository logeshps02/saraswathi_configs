# Quotation for Secure Cloud Document Management System

**Quotation No.:** LPS/2026/CDM/001
**Date:** August 2026
**Valid for:** 30 days from date of issue

---

**Prepared for:**
[Client / Firm Name]
[Firm Address, Line 1]
[Firm Address, Line 2]

**Prepared by:**
Logesh P S
[Contact: Email / Phone]

*Note: The undersigned is a freelance professional and is not registered under GST. Accordingly, no GST is charged on the professional services fee below.*

---

## 1. Executive Summary

This quotation covers the design, deployment, migration and go-live of a **Secure Cloud Document Management System** for your firm, hosted on Amazon Web Services (AWS) in the Mumbai region, running Nextcloud open-source enterprise document platform.

**Scope covers:**

- **10 user accounts** (5 permanent + 5 rotating trainees).
- **150 GB of firm data** migrated from existing hard drives to secure cloud storage.
- **Web + Desktop + Mobile access** for all users.
- **Full audit trail** of every user action for compliance.
- **3-layer backup** (Trash bin + Version history + AWS Glacier archive).
- **India-resident data storage** (AWS ap-south-1, Mumbai).

**Commercial structure:**

- **One-time professional services fee (paid to Logesh P S):** ₹40,000
- **One-time domain registration (paid to registrar):** approx. ₹1,000
- **Recurring monthly AWS infrastructure cost (paid directly to AWS India):** approx. **₹5,000/month** with 1-year Reserved Instance (recommended, no upfront payment). Approx. ₹6,200/month on-demand without commitment.

---

## 2. Glossary — Technology Terms Used in This Document

Since some technology terms are unavoidable in a cloud project, a short glossary is included so the commercial sections are easy to read.

| Term | Meaning in plain language |
|---|---|
| **Cloud** | Storing files and running software on secure remote servers over the internet, instead of on physical hard drives in your office. |
| **AWS (Amazon Web Services)** | The world's largest cloud infrastructure provider. Your data will physically sit in Amazon's Mumbai data centre. |
| **Nextcloud** | A well-established open-source software that turns cloud storage into a private "Google Drive" or "Dropbox" for your firm — with editing, sharing, chat, and audit built in. |
| **Server (EC2)** | A powerful computer running 24×7 that hosts your Nextcloud portal. Since this runs continuously, it is the largest monthly cost line (see Note 1 in Section 5). |
| **Storage (S3)** | Where your files physically reside. Very cheap per GB. |
| **Database (RDS / MySQL)** | A small structured record of who has access to what file and what happened when. Files themselves are stored separately. |
| **Domain / URL** | Your firm's web address (e.g. `files.yourfirm.co.in`). |
| **HTTPS / TLS** | The "lock symbol" in your browser — meaning all data traveling between users and server is encrypted. |
| **Encryption at rest** | Files are stored in scrambled form on the server. Even if someone stole the drive, they couldn't read the data. |
| **Backup** | Additional safely-stored copies of data used for recovery in case of accidental deletion. |
| **Sync** | Automatic mirroring of files between your laptop and the cloud. |
| **Reserved Instance (RI)** | An optional 1-year commitment to Amazon in exchange for a ~30 % discount on the server cost. |
| **Bandwidth / Data Transfer Out** | Amount of data that leaves the cloud (i.e. downloads by users). Uploads into the cloud are always free. |

---

## 3. Solution Overview

| Component | What it does |
|---|---|
| **Nextcloud** (open-source, free) | Provides the entire user interface, sharing, editing, audit log, backup, and admin capabilities. See the accompanying Feature Document for the detailed list of 150+ capabilities. |
| **AWS EC2** | Cloud server that runs Nextcloud 24×7. |
| **AWS S3** | Secure cloud storage that holds all 150 GB of firm data. |
| **AWS RDS (MySQL)** | Managed database for Nextcloud's internal records, automatically backed up. |
| **AWS Route 53** | Domain-name management for `https://files.yourfirm.co.in`. |
| **AWS CloudTrail + Backup** | Independent audit log + automated daily backups. |

**Deployment region:** AWS Mumbai (ap-south-1) — data stays inside India.

---

## 4. Scope of Work — One-Time Deliverables

| # | Deliverable | Description |
|---:|---|---|
| 1 | Cloud architecture design | End-to-end architecture diagram tailored to the firm's requirements, delivered as a documented PDF. |
| 2 | AWS environment provisioning | Setup of the AWS account, private network, encryption keys, server, storage, database, DNS and billing alerts in a new AWS account under the firm's ownership. |
| 3 | Nextcloud installation & hardening | Ubuntu 24.04 LTS server + Nginx + PHP-FPM + Nextcloud latest LTS + Redis caching + firewall + auto-updates. |
| 4 | HTTPS with custom domain | Configuration of `files.yourfirm.co.in` with TLS encryption via Let's Encrypt (auto-renewing). |
| 5 | Nextcloud Office (Collabora) | Browser-based Word / Excel / PowerPoint editing engine installed and integrated. |
| 6 | Additional apps enabled | Nextcloud Talk (chat + video), Groupware (Calendar + Contacts), Deck (Kanban board), Time Manager, LibreSign (PDF signing). |
| 7 | Data migration | Migration of **150 GB** of existing firm data from source hard drives to AWS with folder structure preserved and integrity verified via checksum comparison. |
| 8 | User & permission model | Creation of 10 user accounts with role-based access (Partners / Seniors / Juniors / Trainees) per client-supplied matrix. |
| 9 | Audit log configuration | Nextcloud Activity log + AWS CloudTrail + storage access logging configured for indefinite retention and CSV export. |
| 10 | Backup & disaster recovery | Daily server + database snapshots, storage versioning, Glacier long-term backup, and a written disaster-recovery procedure. |
| 11 | User acceptance testing (UAT) | Guided walk-through with partners and staff; issue log and fixes. |
| 12 | Training sessions | Two sessions of 90 minutes each — one for firm administrators, one for all end-users. |
| 13 | Documentation | Admin Runbook, User Quick-Start Guide, Backup & Restore Procedure, AWS Account Architecture Diagram. |
| 14 | Ongoing post-go-live support | **Endless support** for any issue arising from the delivered scope (see Section 12). |

---

## 5. One-Time Costs

### 5.1 Professional Services Fee (payable to Logesh P S)

| Line Item | Amount (INR) |
|---|---:|
| Cloud architecture design & documentation | 4,500 |
| AWS environment provisioning & hardening | 7,000 |
| Nextcloud installation, Office integration & app setup | 5,500 |
| Data migration of 150 GB with integrity verification | 7,500 |
| User accounts & role-based permission model | 2,500 |
| Audit log & three-tier backup configuration | 4,500 |
| User acceptance testing, training (2 sessions) & documentation | 5,500 |
| Ongoing post-go-live support & knowledge transfer | 3,000 |
| **Subtotal — Professional Services** | **40,000** |

*Freelance professional services. GST not applicable.*

### 5.2 Third-Party One-Time Costs (paid by client directly)

| Line Item | Vendor | Approx. Amount (INR) |
|---|---|---:|
| Domain name registration `yourfirm.co.in` (annual) | Registrar of choice (BigRock / GoDaddy / Namecheap) | ~1,000 |
| Nextcloud software licence | Open-source (Nextcloud GmbH) | 0 |
| Nextcloud Office (Collabora Community Edition) | Open-source | 0 |
| Migration tools (AWS CLI, etc.) | Open-source | 0 |
| **Subtotal — Third-Party One-Time** | | **~1,000** |

### 5.3 One-Time Grand Total

| | Amount (INR) |
|---|---:|
| Professional services fee (to Logesh P S) | 40,000 |
| Third-party — domain (to registrar) | 1,000 |
| **One-Time Grand Total** | **~41,000** |

---

## 6. Recurring Monthly Costs (Paid Directly to AWS India)

The recurring cost is entirely for AWS cloud infrastructure. AWS India Pvt. Ltd. issues a proper GST invoice directly to the firm each month. The client's credit card / net-banking is charged automatically by AWS. Logesh P S does not receive any part of this payment.

### 6.1 Detailed Line Items — On-Demand Pricing

| Item | Purpose | Approx. Monthly (INR) |
|---|---|---:|
| EC2 `t3.medium` server (running 24×7) | Nextcloud application server | 2,800 |
| Server disk (30 GB) | Operating system storage | 250 |
| Database (RDS MySQL) | Nextcloud's internal records | 1,050 |
| Database storage (20 GB) | Data + logs | 230 |
| Cloud storage (S3, 150 GB) | All firm files | 320 |
| Storage versioning (est. 20 GB) | Past versions of edited files | 45 |
| Storage request charges (typical usage) | Standard read/write operations | 60 |
| Bandwidth out (est. 50 GB/month — see Note 2) | User downloads & mobile sync | 450 |
| DNS (Route 53) | For `files.yourfirm.co.in` | 45 |
| Automated backups (server + database daily snapshots) | Disaster recovery | 200 |
| Audit log storage (CloudTrail) | Independent AWS audit trail | 100 |
| System monitoring (CloudWatch) | Server health & alarms | 100 |
| Glacier Deep Archive (long-term backup) | 5–10 year compliance archive | 45 |
| Buffer / contingency (~10 %) | For usage spikes | 500 |
| **Approximate monthly total — On-Demand** | | **≈ ₹6,200** |

### 6.2 Notes on the Above Cost Structure

**Note 1 — Why is the server (EC2) larger than the storage cost?**
Cloud pricing works differently from personal storage. The server (`EC2`) is a computer that runs 24×7 to host the Nextcloud portal — this is a **fixed cost** regardless of how many files are stored. Storage (`S3`) is charged **per gigabyte** and scales with the volume of data. Because you currently have 150 GB, the storage line is small. As data grows to 1 TB or 2 TB in future years, the storage line will grow proportionally while the server line stays roughly the same. This is standard cloud economics.

**Note 2 — Uploading files is free; only downloading is charged.**
- **Uploading files to AWS is completely free** — you can upload as many files as you want, at any speed, without incurring bandwidth charges. This is guaranteed by Amazon for every account.
- **Only "download" traffic (data leaving the cloud) is billed** — this happens when a user clicks "Download", when the desktop sync client copies files to a laptop, or when the mobile app fetches a file.
- **Editing in the browser (Nextcloud Office / Collabora) does not download the file** — the file stays on the server; only your edit clicks travel between your browser and the server, which is a few kilobytes. Even heavy editing sessions use very little bandwidth.
- The 50 GB/month estimate accounts for realistic daily downloads. Actual usage will vary. If it goes higher, the buffer (~₹500) absorbs it.

### 6.3 Reserved-Instance Pricing (Recommended from Day 1 — No Upfront Payment)

We recommend enabling **1-year Reserved Instances (RI)** for the server (EC2) and database (RDS) **on Day 1** of go-live. A Reserved Instance is simply a 12-month commitment to Amazon to keep the same server running — in exchange, Amazon gives approximately **30 % discount** on those two lines from the very first month.

**AWS offers three RI options:**

1. **No Upfront (recommended)** — pay nothing extra now, just commit to 12 months, discounted price billed monthly. This is the option we recommend since it requires zero additional cash outlay while capturing the full discount.
2. **Partial Upfront** — pay part of the year now, smaller monthly bill for 12 months.
3. **All Upfront** — pay the full 12 months now, no monthly bill for those instances.

For this project, the **No Upfront** option gives the same effective monthly cost with no lump-sum payment required.

| Item | On-Demand (no commitment) | 1-Year RI, No Upfront | Monthly Saving |
|---|---:|---:|---:|
| EC2 (server) | 2,800 | 1,800 | 1,000 |
| RDS (database) | 1,050 | 720 | 330 |
| All other lines | 2,350 | 2,350 | 0 |
| **Effective monthly total** | **₹6,200** | **≈ ₹5,000** | **₹1,330/month** |

**Reserved-Instance annual saving: approx. ₹15,960/year** (from Day 1 onwards).

### 6.4 What Happens After the 12-Month RI Term Ends

At the end of 12 months, the Reserved Instance simply expires and the same server continues running — nothing breaks. AWS then bills that server at the on-demand rate until a new 1-year RI is purchased. Renewing the RI takes 30 seconds in the AWS console, so the effective monthly cost stays at ≈ ₹5,000 permanently for as long as we keep renewing.

---

## 7. Detailed Month-by-Month Cost Breakdown

For clarity, here is exactly what the firm will pay each month.

### 7.1 First Month (Setup Month)

*Assumes 1-year Reserved Instance (No Upfront) activated on Day 1 — recommended option.*

| Item | Paid To | Amount (INR) |
|---|---|---:|
| Professional services — 40 % advance | Logesh P S | 16,000 |
| Professional services — Data migration milestone | Logesh P S | 16,000 |
| Professional services — Go-live milestone | Logesh P S | 8,000 |
| Domain registration (annual) | Registrar | 1,000 |
| AWS infrastructure (first month, with 1-year RI) | AWS India | ~5,000 |
| **Month 1 total outlay** | | **≈ ₹46,000** |

### 7.2 Second Month Onwards (Steady State — With 1-Year RI, Recommended)

| Item | Paid To | Amount (INR) |
|---|---|---:|
| AWS infrastructure with 1-year Reserved Instance | AWS India | ~5,000 |
| **Month 2+ total outlay** | | **≈ ₹5,000/month** |

### 7.3 Second Month Onwards (Alternative — Without Reserved Instance)

If the firm prefers not to make the 12-month commitment, the on-demand pricing applies:

| Item | Paid To | Amount (INR) |
|---|---|---:|
| AWS infrastructure without commitment (on-demand) | AWS India | ~6,200 |
| **Month 2+ total outlay** | | **≈ ₹6,200/month** |

### 7.4 Month 12 / Every Year Renewal

| Item | Paid To | Amount (INR) |
|---|---|---:|
| Domain renewal (annual) | Registrar | ~1,000 |
| AWS infrastructure (that month) | AWS India | ~5,000 (with RI renewal) or ~6,200 (on-demand) |
| **Month 12 total outlay** | | **≈ ₹6,000 – ₹7,200** |

### 7.5 12-Month Total Outlay Forecast

| Scenario | Year 1 | Year 2 |
|---|---:|---:|
| **With 1-year RI activated on Day 1 (recommended)** | **~₹1,01,000** | **~₹61,000** |
| Without Reserved Instance (on-demand) | ~₹1,15,400 | ~₹75,400 |

*Year 1 = ₹41,000 one-time + 12 × AWS monthly. Year 2 = 12 × AWS monthly + ₹1,000 domain renewal.*

### 7.6 Cost Growth Forecast

As the firm's data or team grows, the AWS bill grows proportionally with storage. User count does NOT affect infrastructure cost.

| Total data | Users | Estimated monthly AWS cost (with RI) |
|---|---:|---:|
| 150 GB (today) | 10 | ~₹5,000 |
| 300 GB | 10 | ~₹5,200 |
| 500 GB | 15 | ~₹5,500 |
| 1 TB | 20 | ~₹6,400 |
| 2 TB | 25 | ~₹8,500 |

Adding new users is free on the AWS side.

---

## 8. Payment Terms & Milestones

### 8.1 Professional Services Payment Schedule

| Milestone | Trigger | Amount |
|---|---|---:|
| Advance | Signing of this quotation | 40 % × ₹40,000 = **₹16,000** |
| Data migration complete | Verification of 150 GB successfully migrated to AWS | 40 % × ₹40,000 = **₹16,000** |
| Go-live + training complete | Training sessions delivered & documentation handed over | 20 % × ₹40,000 = **₹8,000** |

### 8.2 Third-Party Payments (Direct)

| Item | Trigger | Amount |
|---|---|---:|
| Domain registration | Day 1 of engagement | ~₹1,000 (paid directly to registrar) |
| AWS infrastructure | Monthly | Billed directly by AWS India to the firm's registered payment method |

### 8.3 Payment Modes for Professional Services

- IMPS / NEFT / UPI to the bank account details provided at signing.
- A signed receipt / invoice will be issued for each payment.

---

## 9. Project Timeline — 20 Working Days to Go-Live

| Phase | Days | Cumulative |
|---|:---:|:---:|
| Pre-work — client provides user list, permission matrix, AWS access authorisation | Days 1 – 3 | Day 3 |
| Phase 1 — Foundation (domain purchase, AWS account, private network, security keys) | Days 4 – 5 | Day 5 |
| Phase 2 — Nextcloud server installation & hardening | Days 6 – 7 | Day 7 |
| Phase 3 — Nextcloud Office + Talk + Groupware + Deck apps enabled | Day 8 | Day 8 |
| Phase 4 — User accounts + group + permission matrix + audit log | Days 9 – 10 | Day 10 |
| Phase 5 — Data migration (150 GB — spread across 3–5 overnight upload windows depending on office bandwidth) | Days 11 – 15 | Day 15 |
| Phase 6 — Integrity verification, backup jobs, monitoring, alarms | Days 16 – 17 | Day 17 |
| Phase 7 — User acceptance testing with partners & staff | Day 18 | Day 18 |
| Phase 8 — Training sessions (admin + end-user) | Day 19 | Day 19 |
| Phase 9 — Go-live, documentation hand-over, credential rollover | Day 20 | Day 20 |

**Overall commitment: go-live within 20 working days of signed proposal + receipt of advance + client-side inputs.**

The 20-day plan builds in realistic buffer for client-side turnaround (user list, permission matrix, credentials), overnight upload windows, and any small fixes discovered during testing. This is an achievable, honest timeline.

---

## 10. Assumptions & Prerequisites

The following are assumed for the delivery to remain within the stated timeline and cost:

1. Client shall open an AWS account in the firm's name and provide authorised access to Logesh P S for setup.
2. Client shall provide the list of users (name + role + assigned client folders) within 2 working days of engagement start.
3. Client shall provide upload access to the source data (150 GB) — either via the office PC that currently holds it or via an external hard disk.
4. Client's office internet has a minimum upload bandwidth of 20 Mbps for the overnight migration; higher speeds shorten the migration window.
5. Firm has decided on a domain name to register.
6. Client will make available 3–5 users for User Acceptance Testing on Day 18 and all users for training on Day 19.

---

## 11. Exclusions

The following are **not** included in this quotation:

- Purchase of the domain name (approx. ₹1,000/year — paid directly to registrar).
- Ongoing AWS infrastructure charges (pass-through — paid directly to AWS India).
- Purchase of any Nextcloud apps that require paid licensing (mentioned scope covers only free open-source apps).

---

## 12. Ongoing Post-Go-Live Support

Once the system is live, Logesh P S provides **ongoing support without any fixed time limit** for any issue arising from the delivered scope. This includes:

- Answering questions from any user or administrator.
- Resolving any defects or configuration issues in the delivered setup.
- Guidance on adding new users, changing folder permissions, restoring deleted files, and running audit-log reports.
- Guidance on browser, desktop-sync, or mobile-app usage.
- Investigating and helping with any error or unexpected behaviour.

**Support channel:** email + phone (WhatsApp acceptable).

**Response commitment:** best effort — typically same day for critical issues, within 1–2 working days for routine queries.

### What is NOT covered under ongoing support

- **New features / new modules** — anything beyond what is delivered in Section 4 above (for example, adding an HR system, integrating a new third-party tool, enabling additional Nextcloud apps beyond the mentioned scope, custom development, or integration with the firm's existing accounting/tally software). These will be quoted separately at the time of request.
- **Additional data migration** — moving data from new sources beyond the initial 150 GB.
- **Major architectural changes** — e.g. moving from single-server to multi-server setup, disaster-recovery site in another region, dedicated video-call backend.
- **Third-party costs** — AWS bill, domain renewal, or any external subscription.

Additional-feature requests will be scoped separately, with an agreed fee before work begins.

---

## 13. Confidentiality

- All firm data, client information, and business processes shared during the engagement will be treated as strictly confidential.
- A separate non-disclosure agreement (NDA) may be signed at the client's request at no additional cost.
- No firm data will be retained by Logesh P S after project completion — all access credentials handed over and personal copies destroyed.

---

## 14. Terms & Conditions

1. This quotation is valid for **30 days** from the date of issue.
2. AWS infrastructure charges are pass-through: Logesh P S does not charge any margin on them; the AWS invoice is raised by AWS India Pvt. Ltd. directly to the firm.
3. Any change in scope (additional users, folders, apps, or data volume beyond 150 GB) will be quoted separately.
4. The firm remains the sole owner of the AWS account, cloud storage bucket, data, and domain at all times.

---

## 15. Acceptance

We acknowledge and accept the terms of this quotation as detailed above.

| For [Client / Firm Name] | For Logesh P S |
|---|---|
| Name: _______________________________ | Name: Logesh P S |
| Designation: _________________________ | |
| Signature: ___________________________ | Signature: ___________________________ |
| Date: _______________________________ | Date: _______________________________ |
| Firm Seal (if applicable) | |

---

## 16. Grand-Total Summary Card

> **One-time professional services fee (payable to Logesh P S):** ₹40,000
> **One-time domain registration (paid to registrar):** ~₹1,000
> **Recurring monthly AWS infrastructure (paid directly to AWS India):** ~**₹5,000/month** *(with 1-year Reserved Instance — recommended, no upfront)*, or ~₹6,200/month *(on-demand, no commitment)*
>
> **Month 1 total outlay:** ~₹46,000 *(one-time fee + domain + first month AWS with RI)*
> **Month 2 onwards:** ~₹5,000/month *(with RI — recommended)* or ~₹6,200/month *(without RI)*
>
> **Year-1 total outlay:** ~₹1,01,000 *(with RI — recommended)* or ~₹1,15,000 *(without RI)*
> **Year-2 onwards annual outlay:** ~₹61,000 *(with RI)* or ~₹75,000 *(without RI) — only AWS + domain renewal*
>
> **User count changes:** ₹0 additional cost on infrastructure.
> **Trainee rotation:** ₹0 additional cost.
> **Ongoing support:** included, no time limit, for the delivered scope.

---

*Document prepared by Logesh P S. For any clarifications, please reach out at any time.*
