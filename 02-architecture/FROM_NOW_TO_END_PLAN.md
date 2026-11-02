# From now to end — updated delivery plan (2026-08-31 quotation path)

**Live URL:** https://files.t-saraswathi.in  
**Operator:** Logesh P S (`logesh.implementer`)  
**Do not** put passwords, keys, emails, or `config.php` here.

This replaces the “what’s next” picture after Phase 6 close and admin UAT through batch 4. It does **not** change the quotation: 10 users, ~150 GB, AWS Mumbai, Nextcloud.

Click-by-click operator files: [../04-from-now-runbooks/00_READ_ME_FIRST.md](../04-from-now-runbooks/00_READ_ME_FIRST.md) and [../04-from-now-runbooks/16_PLAN_S3_FOLDER_INDEX.md](../04-from-now-runbooks/16_PLAN_S3_FOLDER_INDEX.md). Fill [../04-from-now-runbooks/RESULTS_SHEET.md](../04-from-now-runbooks/RESULTS_SHEET.md) after **each** file. Ask only when a step fails.

**Locked 2026-08-31:** keep **30 GiB** EBS. Do **not** grow to 200 GiB (budget). Do **not** enable primary objectstore (hides existing Files). **F:\Final (~132 GB)** goes to S3 via Nextcloud **External storage** folder **Backup_data**. UAT `_uat-*` may be deleted. Keep Firm/{Partners,Administration,Clients,Statutory,Templates,Trainee-Workspace,Archive}.

---

## 1. Why 132 GB cannot go in today (even though it was always planned)

The **business plan** was always:

- files live on **S3** (cheap, grows to 150 GB+)
- Nextcloud is the UI
- migrate **after** the platform is secure and a **pilot** folder works

The **system that is live today** is:

- Nextcloud writes file bytes to **local disk** `/opt/nextcloud/data`
- that disk is **30 GiB** gp3
- S3 bucket exists, IAM Put/Get proven, versioning on
- Nextcloud **objectstore is not configured** — the app does not use S3 for user files

So 132 GB is still in scope. It is **not** blocked as a product idea. It is blocked b**Do not console-dump.** Upload through Nextcloud (external S3 folder **Backup_data**), then Files shows real names the volume, break Office/Talk on the same instance, and leave no room for versions/trash.

Putting 132 GB into the S3 console would also **not** show those files in Nextcloud. Objectstore (or a documented import) is a planned cutover, not a toggle.

Original order (still correct):

1. Foundation + HTTPS  
2. Secure before bulk data  
3. Apps + groups  
4. **Small pilot**, then full 150 GB  
5. Backup/audit (done)  
6. Feature UAT on **samples**, then on real data  
7. Train / hand over  

Do not invert that: bulk data last among platform steps, not first.

---

## 2. Why we test before “all config” and before 132 GB

Testing now is **not** go-live UAT of the whole firm. It is **admin smoke tests** so we do not load 132 GB onto a path that already fails.

Already found **without** 132 GB:

| Finding | If we had uploaded first |
|---|---|
| Collabora File → Export PDF hangs; Save-as-PDF works | 132 GB of DOCX would still not export via that menu |
| CODE status: insufficient hardware / no bind-mount | Same t3.medium would be worse with bulk files + Office |
| Talk HPB missing | Video would still fail after migration |
| Time Manager guest 500 / leftover log errors | Same bugs after 132 GB |
| Extra users deferred | Sharing/co-authoring cannot be proven on real client folders yet |

If we wait until “every later item” (S3, SMTP, HPB, 10 users, NAT, EIP) **then** test, we learn the same defects months later, with business data already on the box.

**Two test layers (keep both):**

| Layer | When | Data | Who |
|---|---|---|---|
| **A. Platform UAT** (now) | After each config batch | Tiny `_uat-*` files | `saraswathi.admin` only |
| **B. Migration UAT** | After storage cutover + pilot | Real sample client folder | Admin, then one extra user |
| **C. Go-live UAT** | After 10 users + shares + SMTP | Agreed feature codes | Firm roles |

132 GB is **Phase 5**, not Phase 7. Phase 6 backup/monitoring is already closed so a failed upload does not mean “no backups.”

---

## 3. What is already done vs still later

### Done (do not redo)

- AWS Mumbai, VPC, private RDS, EC2, HTTPS `files.t-saraswathi.in`, PHP 8.3, Nextcloud 34.0.3
- Groups + Firm/ folder tree
- Office CODE (built-in), groupware apps, LibreSign, Deck, Talk (no HPB)
- Budget $60, SNS, five CloudWatch alarms OK, CloudTrail management trail Logging; **S3 data events off 2026-09-12** (were files-bucket only during ingest)
- AWS Backup vault + daily EBS; RDS 7-day backups
- Trash + versions drills; S3 versioning on (bucket empty of NC files)
- Admin UAT G–Z except batch 5 still open (AA–AE)

### Open now

- Phase 7 **batch 5**: pptx, save-as ODT, metadata, lock, recurring calendar

### Later (required before 132 GB)

- **Storage (quotation):** External storage S3 folder **Backup_data** on existing bucket (IAM, no keys). **Not** grow EBS. **Not** primary objectstore.
- PHP/nginx upload size + timeouts (already 512M; reconfirm M1C)
- Desktop client / WebDAV for tree upload (not browser zip of 132 GB)
- Pilot `/Backup_data/_pilot`, then full `F:\Final` → `/Backup_data/Final`

### Later (required for quotation completeness, not for first byte of 132 GB)

- Extra users (10), quotas, share matrix, password policy
- SMTP (mail invites, Talk/calendar mail)
- Talk HPB / video
- Full-text search indexer (A8)
- Co-authoring with two users (B5)
- Public links only if policy allows (C3)
- Branding, ClamAV if still in scope
- NAT only if a later design needs it (Elastic IP `13.234.211.7` done 2026-11-02)
- Do **not** Apply pending RDS OS until a maintenance window
- File → Export PDF remains known-broken until CODE resources are addressed

---

## 4. Storage decision (locked 2026-08-31)

Pick **one**. Do not do both. **Chosen: S3 as a Nextcloud folder (External storage).** Not objectstore. Not 200 GiB EBS.

### Option S-folder — quotation path (DO THIS)

**What:** Keep `/opt/nextcloud/data` on 30 GiB. Mount bucket `saraswathi-nextcloud-files-055855670388` as Files folder **Backup_data** using **None/builtin** auth (instance role). `F:\Final` uploads there via desktop client. Names in S3 are real keys.

**Why it matches the quote:** 150 GB on S3 (~₹320); 30 GB OS disk (~₹250); budget $60. Existing Firm tree stays visible on disk.

**Needs:**

1. IAM already proven (`HEAD_BUCKET:0` `S3_PROBE:0`)
2. Enable External storage app
3. Mount Amazon S3, empty keys, region `ap-south-1`, SSL on
4. Proof file in Files **and** S3
5. PHP 512M already; tiny upload into Backup_data
6. Pilot then 132 GB via **desktop client** into `/Backup_data/Final`

**Do not:** access keys; objectstore in `config.php`; S3 console dump; grow volume.

### Option S-objectstore — SKIP

Would hide current Files on this existing install. Not used.

### Option E — Grow local disk — CANCELLED

200 GiB + 7-day snapshots is **not** in the quote and would blow $60. Volume stays **30 GiB**.

---

## 5. Plan from now to handover (detailed)

Work in this order. Each phase has an exit test. Do not start 132 GB until Phase M2 exit is green.

### Phase T — Finish admin platform UAT (no extra users, no 132 GB)

**T1. Batch 5 (open)** — `saraswathi.admin`

| ID | Test | Pass |
|---|---|---|
| AA | New presentation `_uat-slides`, text `uat`, reopen | text remains |
| AB | `_uat-office` **Save as** near filename → ODT (not File → Export PDF) | new file in Templates |
| AC | `_restore-drill.txt` Details sidebar | size and/or date |
| AD | Lock then Unlock, or no lock menu | recorded either way |
| AE | Calendar repeat Daily/Weekly on `_uat-event` | recurring mark |

**T2. Optional admin-only leftovers** (still no users)

- PowerPoint already in AA; skip File → Export PDF
- Password policy (H) when ready to create users
- Skip public share until policy
- Skip video until HPB
- Skip full-text A8 until indexer installed
- Skip co-authoring B5 until second user

**Exit T:** batch 5 pasted; known defects listed (Export PDF, HPB, TM log, CODE hardware). `_uat-*` left in place.

---

### Phase M0 — Freeze migration inputs (can overlap T)are tests; may be deleted (runbook 17)

1. Confirm the 132 GB tree is the in-scope set (path, folder count, file count, bytes).
2. Note exclusions (duplicates, `~$` Office locks, tmp).
3. Agree target Nextcloud folder: e.g. `Firm/Archive/...` or `Firm/Clients/...` — not admin home dump.
4. Agree **Option S or E**.
5. Recalculate AWS monthly vs $60 **after** the storage choice (S3 150 GB vs 200 GB EBS).

**ETarget Nextcloud folder: **Backup_data** (S3 mount), not admin home, not 30 GB `Firm/`.
4. Storage: **S-folder** (locked). Not grow EBS.
5. Cost: S3 150 GB vs $60; do not add 200 GB EBS

### Phase M1 — Make the platform able to hold the data (S-folder)

1. Optional delete `_uat-*` (runbook 17). Keep seven Firm folders.
2. Enable External storage app (18).
3. Mount Amazon S3 as **Backup_data**, auth None, no keys (19).
4. Proof `_s3-proof.txt` in Files and in the bucket (20).
5. PHP/nginx 512M; tiny browser upload **into Backup_data** (06).
6. Disk stays ~30G. S3 holds bulk. Do not Apply RDS OS.

**Exit M1:** proof file on S3 folder + small upload. Local disk does **not** need > 132 GB free.

---

### Phase M2 — Pilot (mandatory, still not 132 GB)

Upload **one** small real folder only (templates + mixed PDF/DOCX/XLSX, tens or hundreds of MB, not tens of GB).

Use **Nextcloud desktop client** or WebDAV (WinSCP/rclone with app password). Not browser drag of the whole tree.

**Pilot tests**

| Check | Pass |
|---|---|
| Folder names match source | yes |
| File count / bytes within agreed tolerance | recorded |
| Preview PDF + open DOCX | yes |
| Save-as PDF on one DOCX | yes (Export PDF may still fail) |
| Trash delete + restore one pilot file | yes |
| Search by **filename** | yes |
| Permissions: still admin-only until users exist | yes |

**Exit M2:** signed “pilot OK”. Then full load.

---

### Phase M3 — Full 132 / 150 GB

1. Freeze source (no edits during the window, or a delta pass after).
2. Desktop client sync of the agreed tree into the agreed Firm folder.
3. Run overnight if needed; do not use phone hotspot as the only path.
4. Log failures (path too long, blocked chars, 0-byte, locks).
5. Re-run failures only.
6. Final counts: folders, files, bytes source vs Nextcloud (and S3 if Option S).
7. Spot-check 10 files from different subfolders (open/download).

**Exit M3:** reconciliation sheet. Exceptions listed, not silent.

---

### Phase U — Users, sharing, remaining features (after or in parallel with M2, not before M1)

Do **not** create 10 users on 30 GB local disk if they will sync 132 GB.

1. Password policy + brute-force (already partly default).
2. Create users into existing Firm-* groups; quotas if required.
3. Share matrix: group shares on Firm/Partners, Clients, etc. (C1/C2).
4. Public links (C3/C4) only if the firm allows.
5. SMTP for invites and calendar (N).
6. Desktop + mobile login for one Partner + one Trainee (G).
7. Talk video only after HPB decision (cost/CPU).
8. Two-user co-authoring B5 on a **copy**, not on the only original.
9. Full-text search A8 if still promised (extra app + index job; CPU).
10. LibreSign on a **sample** PDF (not production MCA forms first).
11. Branding M if still in scope.

**UAT with users (go-live set)** — one paste per batch, same as now:

| Batch | Codes | Need |
|---|---|---|
| Shares | C1 C2 C5 C6 | second user |
| Link | C3 C4 | policy yes |
| Co-edit | B5 B6 B7 | two browsers |
| Devices | G1–G8 | desktop + phone |
| Mail | N1–N3 | SMTP |
| Video | D4 | HPB |
| Search body | A8 | indexer |
| Admin | K1–K8 | users exist |
| Audit | J CSV / filters | after real actions |

**Exit U:** sharing matrix signed; known defects still listed (Export PDF until CODE sized).

---

### Phase H — Handover

1. Training: Files, Office Save-as, Deck, Calendar, shares, trash/versions.
2. Runbook already at `02-architecture/DR_RUNBOOK.md` — add S3 restore if Option S.
3. Admin contacts, budget owner, “do not use root”, SSM only.
4. Credential handover record (not in git).
5. Support boundary per quotation.

**Exit H:** firm can add a user, restore a file from trash, and know who pays AWS.

---

## 6. What we will not do in the same breath as 132 GB

- NAT, RDS OS Apply now, FSR, Object Lock, all-S3 data events, PHP 8.5, port 22, passwords in chat (Elastic IP was added later, 2026-11-02)
- Browser upload of the entire 132 GB tree
- Filling S3 in the AWS console hoping Nextcloud sees it
- Creating 10 users who then sync 132 GB onto 30 GB EBS
- Fixing Collabora Docker/second EC2 in the upload window

---

## 7. Suggested sequence (short)

```
Now:     T1 batch 5 AA–AE
Then:    M0 numbers + pick S or E
Then:    M1 storage cutover + PHP limits
Then:    M2 pilot folder + tests
Then:    M3 full 132 GB + reconcile
Parallel after M1: U users/shares/SMTP (video/search later)
Last:    H training + handover
```

**Next operator action (unchanged until M0 is chosen):** finish **AA–AE** as `saraswathi.admin`, one paste. Then decide **S3 objectstore vs disk grow**.
