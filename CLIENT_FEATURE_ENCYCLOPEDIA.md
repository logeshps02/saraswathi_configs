# Feature guide — what each item is and how to use it

**For:** CS. T. Saraswathi & staff
**Website:** https://files.t-saraswathi.in
**Matches:** Feature Overview Document (A1–P4) and Quotation LPS/2026/CDM/001

Search with Ctrl+F and a code (`B8`) or a word (`share`, `trash`).

Each feature has **what it is** and **steps**. A note appears **only** when that item is not live or has a limit. Common problems are collected at the **end** of this file.

## Login and screen (once)

1. Chrome or Edge → `https://files.t-saraswathi.in` → padlock must show.
2. Username the admin gave you (not always email) + password.
3. Two-factor is available but not forced. Use an authenticator if you were given one.
4. Top: search, bell, apps grid, your avatar. Left in Files: All files, Recent, Favorites, Shares, Tags, Deleted files.
5. **Firm** = daily work. **Backup_data** = large company archive. Do not sync all of Backup_data to a laptop.

---

# A — Files and folders

## A1 — Unlimited folder structure

### What it is

Folders inside folders with no practical depth limit. A client can be Client → year → DIR-3 → person → scans.

### Steps to configure / use

1. Staff: Files → + → New folder. Type a clear name. Open it and repeat for subfolders. Admin: no extra switch. Folders work as soon as you can log in.

---

## A2 — Drag-and-drop upload

### What it is

You pull a file from your PC window onto the website. The file is stored in the folder you are looking at.

### Steps to configure / use

1. Open the destination folder first. Drag from File Explorer onto the centre of Files until it highlights. Wait for the progress circle. Alternative: + → Upload file.

---

## A3 — Chunked uploads (large files)

### What it is

A large file is cut into pieces on the way. One dropped Wi-Fi packet does not ruin the whole file. Limit on this server is about 512 MB per browser POST; the desktop app uses smaller chunks so bigger files still work.

### Steps to configure / use

1. Nothing to switch on. Use + → Upload or the desktop client for big PDFs/ZIPs. Admin already set PHP 512M and nginx client_max_body_size 512M.

---

## A4 — Resume-on-failure

### What it is

If the network dies mid-upload, a retry continues instead of always starting at byte 0. Strongest with the desktop app.

### Steps to configure / use

1. If an upload fails, retry the same name into the same folder. Do not keep copies named file (1).pdf. Desktop client: Pause then Resume.

---

## A5 — Bulk download as ZIP

### What it is

The website packs a folder into one .zip on your PC.

### Steps to configure / use

1. Tick the folder (or ⋯) → Download. Extract with Windows Extract All.

---

## A6 — In-browser preview

### What it is

Click a PDF, photo, or Office file and read it without saving to Downloads.

### Steps to configure / use

1. Files → click the name (not the checkbox). Close with X. UAT: office files open.

---

## A7 — Thumbnails

> **Limit on this firm.** Image thumbnails work in Files. SVG/advanced preview may be weak: Overview warned Imagick has no SVG support.

### What it is

Small pictures of images in a folder so you recognise a scan without opening it.

### Steps to configure / use

1. Open a folder of jpg/png. Use grid view (A18). Admin: Imagick SVG is not fully set; photos still thumbnail.

---

## A8 — Full-text search (inside PDFs and Word)

> **Not configured on this firm.** Do not look for this button today.
> Not configured on this firm. Overview/UAT: do not rely on A8 until an indexer app and background jobs are enabled. Extra CPU on the small server. Filename search still works.

### What it is

Proposal promised search inside PDF/Word text, not only the file name.

### Steps to configure / use

1. Admin later: enable Full text search / Elasticsearch or built-in indexer, run occ fulltextsearch:index. Staff today: magnifying glass → type a file name or company name.

---

## A9 — File tags

### What it is

Coloured labels on a file (Urgent, AF-24-25) so you can filter later.

### Steps to configure / use

1. File → Details (i) → Tags → type name → Enter. Left sidebar Tags to filter. Admin can create official tags under Administration → Collaborative tags.

---

## A10 — Favourites / star

### What it is

A personal pin for folders you open every day. Only you see your stars.

### Steps to configure / use

1. Click the star on the row, or ⋯ → Add to favorites. Left → Favorites.

---

## A11 — Comments on files

### What it is

A chat thread attached to the file (not inside Word).

### Steps to configure / use

1. File → Details → Comments → type → Post. Use @name (N5) if you want a bell.

---

## A12 — File activity log

### What it is

A history of this one file: uploaded, renamed, shared, downloaded.

### Steps to configure / use

1. File → Details → Activity.

---

## A13 — Metadata sidebar

### What it is

Size, dates, owner, shares, tags in one panel. UAT: size/date pass.

### Steps to configure / use

1. Select file → i / Details.

---

## A14 — External storage mounts

### What it is

A folder that is not on the small 30 GB server disk. On this firm, Backup_data is Amazon S3 in Mumbai. Daily Firm folders stay on the server disk. Do not enable primary objectstore (would hide existing Files).

### Steps to configure / use

1. Staff: Files → open Backup_data. Admin already: External storage app on; mount ID 1; bucket saraswathi-nextcloud-files-…; auth None (instance role). Administration → External storage to view, not to invent a second mount.

---

## A15 — File locking

> **Limit on this firm.** Lock icon works (UAT). You can still open the file while it is locked. Treat lock as a team signal, not a hard block.

### What it is

Tells others “I am working on this”.

### Steps to configure / use

1. ⋯ → Lock file. Unlock the same way when done.

---

## A16 — Move / copy

### What it is

Move = relocate. Copy = duplicate.

### Steps to configure / use

1. ⋯ → Move or copy → pick folder → Move or Copy.

---

## A17 — Sort by name / size / date

### What it is

Reorder the list in the current folder.

### Steps to configure / use

1. Click Name, Size, or Modified at the top of the list.

---

## A18 — Grid or list view

### What it is

Gallery of pictures vs a table of names.

### Steps to configure / use

1. Toggle the squares/lines icon at the top of Files.

---

# B — Editing Word / Excel / PowerPoint

## B1 — Edit Word (.docx) in browser

### What it is

Microsoft-style editor in the browser (Collabora / Nextcloud Office). UAT: DOCX opens.

### Steps to configure / use

1. Click a .docx. Wait for the ribbon. Type. Close the tab; it saves. Admin: Office app already enabled. Do not install Office on the server.

---

## B2 — Edit Excel (.xlsx)

### What it is

Spreadsheets in the browser: sheets, formulas, basic charts.

### Steps to configure / use

1. Click .xlsx. Same as B1.

---

## B3 — Edit PowerPoint (.pptx)

### What it is

Slides in the browser. UAT: slides reopen pass.

### Steps to configure / use

1. Click .pptx. Use the left filmstrip.

---

## B4 — Open Document formats (ODT/ODS/ODP)

### What it is

LibreOffice-style files open in the same editor.

### Steps to configure / use

1. Click the file. Save in the same format unless you convert (B11).

---

## B5 — Real-time co-authoring

> **Limit on this firm.** Two users can open the same DOCX. This small server (Collabora on t3a.medium, 2 vCPU / 4 GB) may struggle; UAT warned hardware. Try with a copy, not the only original.

### What it is

Two staff type in one document and see each other.

### Steps to configure / use

1. Share as Can edit. Both open the same file. Type in different paragraphs. Wait a few seconds.

---

## B6 — Track changes (redlining)

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED / not available in this Office build. UAT T2 AH: no track-changes.

### What it is

Word-style red marks of who typed what, then Accept/Reject.

### Steps to configure / use

1. There is nothing to enable today. Workaround: Comments (B7) plus a copy named _reviewed.docx. Admin would need a Collabora build that shows Review → Record changes.

---

## B7 — Comments inside the document

### What it is

Comment bubbles on a paragraph or cell. UAT: pass.

### Steps to configure / use

1. Select text → Insert → Comment.

---

## B8 — Export to PDF

> **Not configured on this firm.** Do not look for this button today.
> NOT WORKING on this firm as promised. UAT: Save-as PDF option not there; File → Export PDF fails. Do not use File → Export → PDF.

### What it is

One click from Word/Excel to a PDF.

### Steps to configure / use

1. Workaround for staff: close editor → on the PC, open the downloaded DOCX → Print → Microsoft Print to PDF, then upload the PDF. Or ⋯ → Download and print to PDF.

---

## B9 — Templates library

### What it is

Master letterheads and notices live under Firm/Templates. Partners can edit; trainees should not see Partners (U2 pass).

### Steps to configure / use

1. Copy a template (⋯ → Copy) into the client folder. Rename. Never type over the only master.

---

## B10 — Print from browser

### What it is

Ctrl+P or File → Print in the editor or PDF viewer. UAT print pass.

### Steps to configure / use

1. Open file → Print → choose printer.

---

## B11 — Save as another format

### What it is

Download/save as DOCX, ODT, etc. UAT save-as format pass.

### Steps to configure / use

1. In editor: File → Save as / Download as → pick type.

---

## B12 — Version history in editor / Files

### What it is

Each save can keep an older copy. Restore from Details → Versions.

### Steps to configure / use

1. Files: file → Details → Versions → Restore. Editor: File → version history if shown.

---

## B13 — LibreSign (sign PDF)

> **Limit on this firm.** App is in the stack. Do not sign production MCA PDFs in UAT. Practise on a copy.

### What it is

Draw or upload a signature onto a PDF inside Nextcloud.

### Steps to configure / use

1. Apps → LibreSign (or PDF → Request signature). Use a COPY named _to-sign.pdf. Keep the unsigned original.

---

## B14 — PDF form filling

> **Limit on this firm.** Works on true fillable PDFs. Scanned stamp-paper is only a picture.

### What it is

Type into blue fields on an interactive PDF.

### Steps to configure / use

1. Open PDF → click fields → save.

---

# C — Sharing

## C1 — Share with internal users

### What it is

Give one staff member View or Edit on a file/folder. UAT partner write Templates pass.

### Steps to configure / use

1. ⋯ → Share → type name → View or Edit.

---

## C2 — Share with a group

### What it is

One share to Firm-Partners instead of five people. U2: trainee cannot see Partners.

### Steps to configure / use

1. Share → type group name → permission.

---

## C3 — Public shareable link

> **Limit on this firm.** U3 was skipped or only password+revoke tested. Policy: CS may forbid public links. Expiry date picker was sticky (min=today).

### What it is

A URL anyone with the link can open without a firm login.

### Steps to configure / use

1. Share → Create link → copy. Always add password (C5) and expiry (C4). Do not post in a public WhatsApp group.

---

## C4 — Link expiry date

> **Limit on this firm.** Date picker min=today caused stuck expiry in U3.

### What it is

Link dies after a date.

### Steps to configure / use

1. Link settings → expiration date. Prefer 7 days.

---

## C5 — Link password

### What it is

Recipient must type a password you send separately.

### Steps to configure / use

1. Link settings → Password. Send password by SMS if the link went by email.

---

## C6 — Disable download

### What it is

View in browser, no Save As. Not perfect against screenshots.

### Steps to configure / use

1. Link settings → Allow download off / Hide download.

---

## C7 — Editable public link

> **Limit on this firm.** Same policy as C3. Prefer a Guest user (P4) or internal user.

### What it is

Outsider can edit through the link.

### Steps to configure / use

1. Link permission → Edit. Only for a named auditor you trust.

---

## C8 — File-request (upload only)

> **Limit on this firm.** Same as public links. Folder must be empty of secrets.

### What it is

Outsider drops files; they should not see other files.

### Steps to configure / use

1. Empty folder → Share → File drop / Allow upload. Send only that link.

---

## C9 — Share notifications by email

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED. SMTP / Email test not done (Overview + U3 + U4). Bell (N1) still works if the person is logged in.

### What it is

Email when a share is used or created.

### Steps to configure / use

1. Admin must finish U4 (Amazon SES SMTP).
2. Staff: tell colleagues in Talk or look at the bell.

---

## C10 — Instant revoke

### What it is

Cut access at once. U3 password+revoke pass.

### Steps to configure / use

1. Share panel → … on the person or link → Unshare.

---

## C11 — Federated sharing (another Nextcloud)

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED and not planned. The firm has no second Nextcloud. Skip forever unless CS has one.

### What it is

Share to user@other-company-nextcloud without copying the file.

### Steps to configure / use

1. Do not enable. Use C3/C5 or Guest (P4).

---

## C12 — Share summary dashboard

### What it is

List of what you shared.

### Steps to configure / use

1. Left Shares, or avatar → Sharing.

---

# D — Talk (chat and calls)

## D1 — 1-to-1 text chat

### What it is

Private typed chat. UAT talk extras pass.

### Steps to configure / use

1. Apps → Talk → search a name → type → Enter.

---

## D2 — Group chat rooms

### What it is

A named room for a team or a client job.

### Steps to configure / use

1. Talk → + → Create conversation → add people.

---

## D3 — Voice calls

> **Limit on this firm.** Works for very small calls. No Talk High-performance backend (Overview error). Max about 2–3 people.

### What it is

Audio call inside Talk.

### Steps to configure / use

1. Open chat → phone icon. Allow microphone.

---

## D4 — Video calls

> **Not configured on this firm.** Do not look for this button today.
> NOT FIT FOR TEAM VIDEO. No HPB. Overview: Talk without HPB only scales for 2–3 participants. Do not promise Zoom-like meetings.

### What it is

Camera meeting in the browser.

### Steps to configure / use

1. Do not configure HPB during the 123 GB upload (CPU/cost). For 1:1 try camera icon. For partners meeting, use the firm’s usual video tool.

---

## D5 — Screen sharing

> **Not configured on this firm.** Do not look for this button today.
> NOT RELIABLE HERE. Same HPB/hardware limit. Do not plan training via Talk screen share.

### What it is

Show your screen in a call.

### Steps to configure / use

1. If a 1:1 call is already working, Share screen. Prefer sending a PDF instead.

---

## D6 — Files in chat

### What it is

Attach a file to a message.

### Steps to configure / use

1. Paperclip in Talk → pick file.

---

## D7 — Emoji and reactions

### What it is

Smileys on messages.

### Steps to configure / use

1. Smiley icon on a message.

---

## D8 — Voice messages

### What it is

Short recorded clip, not a call.

### Steps to configure / use

1. Microphone in the composer (not the call button).

---

## D9 — Replies / threads

### What it is

Reply under one message.

### Steps to configure / use

1. On message → Reply.

---

## D10 — Public chat via link

> **Limit on this firm.** Depends on allowing guests. Same caution as public file links. SMTP will not email the invite.

### What it is

Outsider joins one room by URL.

### Steps to configure / use

1. Conversation settings → guest access / link. Remove when done.

---

## D11 — Chat search

### What it is

Search words in Talk.

### Steps to configure / use

1. Magnifying glass in Talk.

---

## D12 — Meeting scheduler with Calendar

> **Limit on this firm.** Calendar events work (E). Mail invites need SMTP (off). Talk room from event if the button exists; do not start video (D4).

### What it is

Put a meeting on the calendar and optionally a Talk room.

### Steps to configure / use

1. Calendar → New event → add Talk room if shown. Tell people in Talk because email may not go.

---

## D13 — Mobile push for Talk

> **Limit on this firm.** Phone app can notify. Overview: Client Push is not installed — notifications may be delayed.

### What it is

Phone buzzes on a new chat.

### Steps to configure / use

1. Install Nextcloud/Talk app (G5/G6). Allow notifications. Admin: Client Push not installed; do not add during ingest.

---

## D14 — Waiting rooms

> **Limit on this firm.** May appear in conversation settings. Not a Zoom webinar product.

### What it is

Host admits each guest.

### Steps to configure / use

1. Conversation ⋯ → lobby / waiting room if listed.

---

## D15 — Kick / mute

### What it is

Host mutes or removes someone in a small call.

### Steps to configure / use

1. Participant list during call → mute / remove.

---

# E — Calendar, Contacts, Tasks

## E1 — Personal calendar

### What it is

Your own dates. Recurring UAT pass.

### Steps to configure / use

1. Apps → Calendar → + New event.

---

## E2 — Shared team calendars

### What it is

A calendar several people see (Firm-Deadlines).

### Steps to configure / use

1. Calendar → New calendar → Share with group.

---

## E3 — Public read-only calendar

> **Limit on this firm.** Possible via public calendar link. Same policy as C3.

### What it is

Outsiders see MCA due dates without editing.

### Steps to configure / use

1. Share calendar → public link, view only.

---

## E4 — Recurring events

### What it is

Weekly/monthly repeat. UAT pass.

### Steps to configure / use

1. Event → Repeat.

---

## E5 — Event reminders by email

> **Not configured on this firm.** Do not look for this button today.
> Email reminders NOT CONFIGURED (no SMTP). In-app reminder may still show if you are logged in.

### What it is

A mail 1 day before a due date.

### Steps to configure / use

1. Staff: keep Calendar open or use phone calendar sync (E6). Admin: U4 SMTP first.

---

## E6 — CalDAV (Outlook / phone)

### What it is

Your phone or Outlook can show the same calendar.

### Steps to configure / use

1. Personal settings → Security → create app password. In Outlook/phone add CalDAV URL shown under Calendar settings. Do not put the password in chat.

---

## E7 — Find a free slot

> **Limit on this firm.** Works if others share busy/free. No mail invite.

### What it is

See when colleagues are busy.

### Steps to configure / use

1. New event → add attendees.

---

## E8 — Attach files to events

### What it is

Agenda PDF on the event.

### Steps to configure / use

1. Event editor → attach / link from Files.

---

## E9 — Talk room from event

> **Limit on this firm.** Button may exist. Do not start video (D4).

### What it is

One click from calendar to a chat room.

### Steps to configure / use

1. Event → Add Talk conversation if shown.

---

## E10 — Shared address book

### What it is

Firm contacts list.

### Steps to configure / use

1. Apps → Contacts. Admin creates a shared address book and shares it with a group.

---

## E11 — CardDAV (phone contacts)

### What it is

Phone can sync Contacts.

### Steps to configure / use

1. Same as E6 with Contacts URL + app password.

---

## E12 — vCard import / export

### What it is

Bring old contacts in. UAT vCard pass.

### Steps to configure / use

1. Contacts → gear → Import .vcf or Export.

---

## E13 — Tasks / to-do

### What it is

Lists of work items, not files.

### Steps to configure / use

1. Apps → Tasks → new list / new task.

---

## E14 — Task due dates and priority

### What it is

UAT due+priority pass.

### Steps to configure / use

1. Open task → due date, priority stars.

---

# F — Deck boards and time

## F1 — Deck Kanban boards

### What it is

Columns To do / Doing / Done. Cards move right as work proceeds.

### Steps to configure / use

1. Apps → Deck → + board. Add stacks. Add cards.

---

## F2 — Cards

### What it is

One card = one job (DIR-3 for X).

### Steps to configure / use

1. In a stack → + card → title.

---

## F3 — Assign cards

### What it is

Owner of the job.

### Steps to configure / use

1. Card → Assign.

---

## F4 — Due dates on cards

### What it is

Deadline on the card.

### Steps to configure / use

1. Card → due date.

---

## F5 — Labels on cards

### What it is

Colour tags on the board.

### Steps to configure / use

1. Card → Labels. Create Urgent / AF-24-25.

---

## F6 — Card comments

### What it is

Talk about that job on the card.

### Steps to configure / use

1. Card → comments.

---

## F7 — Card attachments

### What it is

Link a Nextcloud file to the card.

### Steps to configure / use

1. Card → Attach from Files.

---

## F8 — Checklists

### What it is

Sub-steps on a card.

### Steps to configure / use

1. Card → checklist.

---

## F9 — Share board

### What it is

Who sees the board.

### Steps to configure / use

1. Board menu → Share → user or group.

---

## F10 — Time Manager hours

### What it is

Log billable time. UAT TM hours pass. Do not vendor-patch PHP.

### Steps to configure / use

1. Apps → Time Manager → client → start/stop or type hours.

---

## F11 — Weekly time CSV

### What it is

Export hours for billing.

### Steps to configure / use

1. Time Manager → export CSV.

---

# G — Browser, PC, phone

## G1 — Web browser

### What it is

Chrome or Edge to https://files.t-saraswathi.in — no install.

### Steps to configure / use

1. Use HTTPS only. Padlock must show.

---

## G2 — Windows desktop sync

### What it is

A folder on the PC that mirrors chosen cloud folders. M2 client pass. Do not sync all 123 GB onto a laptop or onto the 30 GB server path.

### Steps to configure / use

1. Install Nextcloud Windows client. Server https://files.t-saraswathi.in. Manual folder: only Firm pieces you need, or virtual files (G9). Pause while the big Backup_data ingest runs if the admin says so.

---

## G3 — macOS client

### What it is

Same as G2 on Mac.

### Steps to configure / use

1. Mac installer from nextcloud.com/install. Same selective sync rules.

---

## G4 — Linux client

### What it is

Same idea on Linux. Unlikely for this office.

### Steps to configure / use

1. Distro package or AppImage. Same URL.

---

## G5 — Android app

### What it is

Phone read/upload.

### Steps to configure / use

1. Play Store Nextcloud → server URL → login. Do not auto-upload the whole Camera to Backup_data.

---

## G6 — iOS app

### What it is

Same on iPhone.

### Steps to configure / use

1. App Store Nextcloud. Same URL.

---

## G7 — Auto photo upload

> **Limit on this firm.** Optional in the phone app. Dangerous if it uploads personal photos into a client folder.

### What it is

Photos go to a chosen folder.

### Steps to configure / use

1. App → Settings → Auto upload → pick one folder such as Firm/Administration/Phone-scans. Keep off for personal albums.

---

## G8 — Offline files on phone

### What it is

Pin a file to open in flight mode.

### Steps to configure / use

1. ⋯ on file → Available offline.

---

## G9 — Virtual files (on-demand)

### What it is

Icons on the PC; content downloads when opened. Saves disk.

### Steps to configure / use

1. Desktop client folder settings → Virtual files.

---

## G10 — Selective sync

### What it is

Tick only some folders.

### Steps to configure / use

1. Client Settings → choose folders. Never tick all of Backup_data on a small disk.

---

## G11 — Bandwidth throttling

### What it is

Cap speed so Zoom/WhatsApp still work.

### Steps to configure / use

1. Client Settings → Network → limit upload. During SAVEPOINT, lower it.

---

## G12 — WebDAV (WinSCP / Cyberduck)

> **Limit on this firm.** Allowed in the proposal. UAT skipped WinSCP (405). Desktop client is enough for staff.

### What it is

Third-party tools speak WebDAV.

### Steps to configure / use

1. If needed: Cyberduck, HTTPS, path /remote.php/dav/files/USERNAME/ , app password. Do not open port 22.

---

# H — Security

## H1 — HTTPS / TLS

### What it is

Yellow lock. Traffic scrambled in transit. Domain files.t-saraswathi.in.

### Steps to configure / use

1. Always type https://. Admin already installed the certificate.

---

## H2 — Encryption at rest (AWS)

### What it is

Disks/S3 use AWS encryption. You do not switch a Files toggle.

### Steps to configure / use

1. No staff action. Do not confuse with H3.

---

## H3 — End-to-end encrypted folders

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED and must not be turned on casually. Breaks Office and search. Policy decision.

### What it is

Even the server cannot read the folder. If you lose the passphrase, files are gone forever.

### Steps to configure / use

1. Do not click Encrypt folder. If a partner insists, implementer designs keys first.

---

## H4 — Password policy

### What it is

Minimum length/complexity. U1 password policy path exists.

### Steps to configure / use

1. Admin: Administration → Security → password settings.
2. Staff: use a long unique password.

---

## H5 — Brute-force protection

### What it is

Too many wrong passwords → slowdown / block.

### Steps to configure / use

1. Automatic. If locked out, wait and ask admin. Do not keep guessing.

---

## H6 — IP allow / deny list

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED as an office-only lock (would block home/travel). Optional later.

### What it is

Only office broadband can log in.

### Steps to configure / use

1. Do not enable without a partner decision (home work would break).

---

## H7 — Session timeout

### What it is

Idle login dies. You sign in again.

### Steps to configure / use

1. Admin: session lifetime in security settings if they want shorter.
2. Staff: log out on shared PCs.

---

## H8 — Rate limiting

### What it is

Stops scripts hammering login/API.

### Steps to configure / use

1. Automatic.

---

## H9 — Trusted domains

### What it is

Only files.t-saraswathi.in is valid. Stops host-header tricks.

### Steps to configure / use

1. Admin already set.
2. Staff: do not use the raw IP in the browser if it warns.

---

## H10 — Content Security Policy

### What it is

Browser shield against injected scripts.

### Steps to configure / use

1. Automatic.

---

## H11 — Anti-virus ClamAV

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED. Extra RAM on t3a.medium. Do not install during ingest.

### What it is

Every upload scanned for malware.

### Steps to configure / use

1. Staff: do not upload EXE/unknown zips. Admin: later package + clamd if partners approve RAM.

---

## H12 — AWS data-centre certifications

### What it is

Mumbai region certifications are Amazon’s. The firm inherits location, not a Nextcloud click.

### Steps to configure / use

1. No click. Account in ap-south-1.

---

## H13 — Private network / no public database

### What it is

RDS is not on the internet. Web is 443 only. No SSH from home.

### Steps to configure / use

1. Admin/implementer only. Staff never get a database password.

---

## H14 — Server hardening (Ubuntu, firewall)

### What it is

Patches, firewall, fail2ban-style controls on the server.

### Steps to configure / use

1. Implementer.
2. Staff: keep Windows updated too.

---

# I — Trash, versions, backup

## I1 — Trash / Deleted files

### What it is

Deleted files sit in Deleted files for a period (often ~30 days). M2 trash pass.

### Steps to configure / use

1. Files → Deleted files → Restore. Do not Empty trash for fun.

---

## I2 — File version history

### What it is

Old copies after edits.

### Steps to configure / use

1. Details → Versions → Restore.

---

## I3 — Self-service version restore

### What it is

You restore without admin.

### Steps to configure / use

1. Same as I2.

---

## I4 — Bulk restore from trash

### What it is

Restore many files at once.

### Steps to configure / use

1. Deleted files → select several → Restore.

---

## I5 — Admin override restore

> **Limit on this firm.** Admin can help after user emptied trash if backups exist. Not magic after Glacier (which is off).

### What it is

Admin uses trash of that user or AWS snapshot.

### Steps to configure / use

1. Staff: message admin with file name, folder, time. Admin: impersonate (K8, audited) or AWS Backup — do not Restore snapshots over production without a plan.

---

## I6 — S3 object versioning

### What it is

AWS bucket versioning is On. This is the safety net for Backup_data objects.

### Steps to configure / use

1. Staff do not click this. Admin: S3 console versioning stays On. Do not turn Off.

---

## I7 — Daily EBS snapshots

### What it is

Server disk snap ~daily, retain 7 days (vault saraswathi-backup-vault). Lock none.

### Steps to configure / use

1. Admin: AWS Backup plan already. Do not Restore for curiosity. Do not Fast Snapshot Restore (cost).

---

## I8 — Daily RDS snapshots

### What it is

Database backups. Point-in-time about 7 days.

### Steps to configure / use

1. Admin only. Do not Apply RDS OS as a ‘fix’. Do not restore over production.

---

## I9 — Glacier Deep Archive 5–10 years

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED. Separate cost. Do not enable as a surprise bill.

### What it is

Monthly cold copy for 5–10 years.

### Steps to configure / use

1. Partner decision + lifecycle policy later.
2. Staff: keep I1–I3 as the daily net.

---

## I10 — Cross-AZ backup

> **Limit on this firm.** AWS regional durability for S3 is inherent. Extra cross-AZ copy of EBS is AWS Backup’s job; do not assume a second city DR site was built.

### What it is

Survive one data-centre failure in Mumbai.

### Steps to configure / use

1. No staff click. Full DR is I12.

---

## I11 — Ransomware immutable backups

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED. Vault lock none. Object Lock / MFA delete not in current design.

### What it is

Attacker cannot wipe backups.

### Steps to configure / use

1. Do not tick Object Lock in S3 without implementer (can lock you out). Hygiene: disable leavers (K5), strong passwords.

---

## I12 — Disaster-recovery write-up

> **Limit on this firm.** A technical DR runbook exists for implementer/admin, not a 4-hour staff click. Rebuild is specialist work.

### What it is

Written steps to rebuild.

### Steps to configure / use

1. Staff: call admin. Do not try AWS Restore alone.

---

# J — Audit trail

## J1 — Every login recorded

### What it is

User, time, IP in logs/activity.

### Steps to configure / use

1. Staff: nothing. Admin: Logging / Audit if enabled.

---

## J2 — Failed logins recorded

### What it is

Wrong password attempts.

### Steps to configure / use

1. Admin reviews after an incident.

---

## J3 — File events recorded

### What it is

View, download, edit, delete, share.

### Steps to configure / use

1. File → Activity (A12). Admin: broader logs.

---

## J4 — Share events recorded

### What it is

Link created/revoked.

### Steps to configure / use

1. Activity on that file.

---

## J5 — Admin actions recorded

### What it is

New user, permission change.

### Steps to configure / use

1. Admin audit. Impersonation must be written down (J14).

---

## J6 — Filter log by user

> **Limit on this firm.** Activity can be filtered. Full CSV audit app may be limited.

### What it is

See one person’s actions.

### Steps to configure / use

1. Admin: Audit/Activity filters.
2. Staff: you see your own activity.

---

## J7 — Filter by date

> **Limit on this firm.** Same as J6.

### What it is

April 2026 only.

### Steps to configure / use

1. Date controls in Activity if present.

---

## J8 — Filter by action type

> **Limit on this firm.** Depends on audit app filters.

### What it is

Only downloads.

### Steps to configure / use

1. Admin tools.
2. Staff: read Activity and scan.

---

## J9 — Filter by file

### What it is

One file’s history = A12.

### Steps to configure / use

1. Open the file → Activity.

---

## J10 — CSV export of audit

> **Limit on this firm.** May require admin_audit download. Not a one-click for all staff.

### What it is

Excel for committee.

### Steps to configure / use

1. Admin: Logging → download if offered. Do not paste logs in WhatsApp (names inside).

---

## J11 — AWS CloudTrail

### What it is

AWS API calls logged independently of Nextcloud.

### Steps to configure / use

1. Admin AWS console. Staff never need it.

---

## J12 — S3 data event logging

> **Limit on this firm.** Do not enable data events on all buckets (cost/noise). Files bucket only if used.

### What it is

Who read which object in S3.

### Steps to configure / use

1. Admin/implementer. Staff use J3.

---

## J13 — Indefinite log retention

> **Limit on this firm.** Proposal said forever. Practice: keep what AWS/Nextcloud retention is set to; confirm with admin. Do not assume 10 years unless billed.

### What it is

Logs never auto-delete.

### Steps to configure / use

1. Admin reviews retention. Staff cannot set this.

---

## J14 — Impersonation audited

### What it is

If admin logs in as you, it is recorded. UAT: do not impersonate without writing it down.

### Steps to configure / use

1. Admin: Users → impersonate only for support, then log out.

---

# K — Users (admin)

## K1 — Create users one by one

### What it is

U1 extra user pass. 10 accounts in the quotation (5 + 5 trainees).

### Steps to configure / use

1. Admin: Users → New user → name, password, group. Tell them the URL. Never paste passwords in chat.

---

## K2 — Bulk create via CSV

> **Limit on this firm.** Possible in Users. Not required if you only have 10 people.

### What it is

Many trainees at once.

### Steps to configure / use

1. Users → import CSV template.

---

## K3 — Groups (Partners / Trainees…)

### What it is

U2 groups work: partner write Templates; trainee cannot see Partners.

### Steps to configure / use

1. Users → Groups. Put people in groups. Share folders to groups.

---

## K4 — Storage quota

### What it is

Cap per user so one person cannot fill the 30 GB disk.

### Steps to configure / use

1. Users → quota. Keep quotas small. Bulk data belongs in Backup_data, not home.

---

## K5 — Disable user

### What it is

Same-day offboarding.

### Steps to configure / use

1. Users → ⋯ → Disable. Then change shared passwords they knew.

---

## K6 — Admin password reset

### What it is

Force a new password.

### Steps to configure / use

1. Users → reset. If SMTP off, tell them the temporary password verbally.

---

## K7 — Sub-admin

> **Limit on this firm.** Can delegate group admin. Do not give everyone full admin.

### What it is

HR adds trainees only.

### Steps to configure / use

1. Users → group admin checkbox.

---

## K8 — Impersonation

### What it is

Admin sees the user’s Files. Audited (J14).

### Steps to configure / use

1. Users → impersonate. Write in a register. Log out.

---

## K9 — Per-folder permission matrix

### What it is

Different rights per folder per group. U2 is the model.

### Steps to configure / use

1. On folder → Share → group → View or Edit. Do not share Backup_data widely until mount sharing is enabled (A14).

---

## K10 — App management

### What it is

Turn apps on/off.

### Steps to configure / use

1. Admin → Apps. Do not enable random games. Do not enable E2E (H3) or ClamAV (H11) without a plan.

---

## K11 — System health overview

### What it is

Yellow/red warnings. Current known: no Talk HPB, no Client Push, no email test, 2FA not enforced, Imagick SVG, opcache, AppAPI daemon, PHP getenv.

### Steps to configure / use

1. Admin → Overview. Do not ‘fix’ by growing EBS or Apply RDS OS.

---

## K12 — Log viewer in admin UI

### What it is

Read logs without Linux.

### Steps to configure / use

1. Admin → Logging. Do not export to WhatsApp.

---

# L — India and ownership

## L1 — Data in India (Mumbai)

### What it is

ap-south-1. Files and database in India.

### Steps to configure / use

1. No click. Do not create resources in Singapore/Virginia.

---

## L2 — Firm owns the AWS account

### What it is

Partners hold root with MFA. Implementer should be IAM, not root.

### Steps to configure / use

1. Partners: MFA on root, no root access keys. Rotate if a vendor leaves.

---

## L3 — Firm owns the files

### What it is

Download any time. No Nextcloud GmbH lock-in of your PDFs.

### Steps to configure / use

1. Download (A5). Keep an office copy policy if partners want.

---

## L4 — Full data export

> **Limit on this firm.** A user can zip their visible files. Whole 123 GB export is an admin/rclone job, not a browser zip.

### What it is

Take a copy of ‘everything I see’.

### Steps to configure / use

1. Staff: zip a client folder. Admin: rclone/desktop for Backup_data.

---

## L5 — Standard formats (PDF/DOCX)

### What it is

Files stay Word/PDF, not a secret container.

### Steps to configure / use

1. No click.

---

# M — Look and language

## M1 — Custom firm logo

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED as a go-live branding pack. Planned after go-live look-and-feel. Default Nextcloud/firm mark may show.

### What it is

Logo on login and top-left.

### Steps to configure / use

1. Admin later: Theming → upload PNG logo (not SVG, Imagick SVG weak).

---

## M2 — Custom brand colours

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED (same as M1).

### What it is

Colours match letterhead.

### Steps to configure / use

1. Admin → Theming → colour. Later.

---

## M3 — Custom login page

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED (same as M1).

### What it is

Background image and disclaimer on login.

### Steps to configure / use

1. Theming → login background, slogan. Later.

---

## M4 — Dark / light mode

### What it is

UAT theme pass.

### Steps to configure / use

1. Avatar → Appearance → Dark or Light.

---

## M5 — Multi-language

### What it is

English / Hindi / Tamil interface.

### Steps to configure / use

1. Personal settings → Language.

---

## M6 — Custom email footer

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED — no SMTP, so no system emails to brand.

### What it is

Firm name at the bottom of notification mails.

### Steps to configure / use

1. After U4: Theming / email footer. Until then N/A.

---

## M7 — Configurable dashboard

### What it is

Home widgets.

### Steps to configure / use

1. Dashboard → Customise → tick widgets.

---

# N — Notifications

## N1 — In-app bell

### What it is

Top-right bell. Works without SMTP.

### Steps to configure / use

1. Click the bell. Open the file from the notice.

---

## N2 — Email notifications

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED. Overview Email test not set. U4 not finished.

### What it is

Mail for shares, comments, calendar.

### Steps to configure / use

1. Admin: SES SMTP (do not paste secrets).
2. Staff: use bell and Talk.

---

## N3 — Mobile push

> **Limit on this firm.** See D13. Client Push missing → delay.

### What it is

Phone notification.

### Steps to configure / use

1. Install app, allow OS notifications.

---

## N4 — Web push (browser)

> **Limit on this firm.** Browser may ask Allow notifications. Not a replacement for SMTP.

### What it is

Even without the tab focused, a pop-up.

### Steps to configure / use

1. Allow when the browser asks. Windows Focus Assist may hide it.

---

## N5 — @mention in comments

### What it is

Type @name in a file comment. They get a bell if logged in. No email until N2.

### Steps to configure / use

1. Comments → @ → pick user.

---

## N6 — Notification preferences

### What it is

U6 notification prefs page saves.

### Steps to configure / use

1. Personal settings → Notifications → toggles.

---

# O — Automation

## O1 — Auto-tagging rules

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED. Flow/rules not part of current UAT.

### What it is

Files in 2025-26 auto-tag Current FY.

### Steps to configure / use

1. Admin later: Flow / files_automated. Do not auto-delete (O3) on client files.

---

## O2 — Auto-move by filename

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED (same as O1).

### What it is

Incoming scan named MCA-* goes to Statutory.

### Steps to configure / use

1. Do not build this during ingest. Staff file by hand (A16).

---

## O3 — Retention auto-delete

> **Not configured on this firm.** Do not look for this button today.
> NOT CONFIGURED and dangerous for MCA papers.

### What it is

Delete working files after N days.

### Steps to configure / use

1. Do not enable. Statutory retention is years, not days.

---

## O4 — File-request folders

> **Limit on this firm.** Same as C8. Not a separate magic app.

### What it is

Upload-only public folder.

### Steps to configure / use

1. See C8.

---

## O5 — Command-line automation

> **Not configured on this firm.** Do not look for this button today.
> NOT FOR STAFF. occ commands are implementer-only. No port 22 from home.

### What it is

Scripts for admin.

### Steps to configure / use

1. Staff never run occ. If someone sends you a Linux command, ignore.

---

## O6 — Background job scheduler

### What it is

Cron/systemd runs Nextcloud jobs (previews, etc.).

### Steps to configure / use

1. Admin/implementer already.
2. Staff: if previews are slow, wait.

---

# P — Optional extra apps

## P1 — Analytics app

> **Not configured on this firm.** Do not look for this button today.
> OPTIONAL, not shown as enabled for the firm.

### What it is

Charts from data.

### Steps to configure / use

1. Do not enable for fun. Excel + B2 is enough.

---

## P2 — Forms

> **Not configured on this firm.** Do not look for this button today.
> OPTIONAL extra. Not in the core 10-user go-live proof.

### What it is

Surveys, CSV of answers.

### Steps to configure / use

1. Admin can enable Forms later. Until then use Word/Excel.

---

## P3 — Bookmarks

> **Not configured on this firm.** Do not look for this button today.
> OPTIONAL. Not required.

### What it is

Shared ROC URLs.

### Steps to configure / use

1. Use a Firm/Administration/Links.txt or enable Bookmarks later.

---

## P4 — Guest accounts

> **Not configured on this firm.** Do not look for this button today.
> OPTIONAL. Guests need extra app. Prefer this later instead of forever public links.

### What it is

Auditor logs in with a tight folder.

### Steps to configure / use

1. Admin enables Guests app, creates guest, shares one folder. Not done as default.

---

# Sample problems and solutions

Use this section when something goes wrong. Ctrl+F the feature code or the problem text.

| Code | Problem | What to do |
|---|---|---|
| Login | Wrong website / no padlock | Type `https://files.t-saraswathi.in`. Do not continue past a certificate warning. |
| Login | Locked after many wrong passwords | Wait about 30 minutes; ask admin if still blocked. |
| Login | No password-reset email | Mail is not set up. Admin must tell you a password in person. |
| A1 | Name already exists | add year or (2) only if it is really a second pack. |
| A1 | Cannot create inside Backup_data | ask admin; S3 mount may be read-only for your user. |
| A1 | Forbidden characters | avoid leading dots and trailing spaces. |
| A2 | Dropped in the wrong folder | Move (A16), do not upload again. |
| A2 | Browser refuses a huge folder | use desktop app (G2), never browser-upload the whole disk. |
| A2 | 0-byte file | retry; check the PC file is not empty. |
| A3 | Browser stops at ~512 MB | use Nextcloud desktop app, not the website. |
| A3 | Whole 123 GB tree in browser | forbidden; use desktop/rclone as the implementer does. |
| A4 | Two copies appear | delete the 0 KB one after the full one is present. |
| A4 | SAVEPOINT / server error during mass upload | pause, wait 2 minutes, slower upload (implementer). |
| A5 | Zip of Backup_data / whole firm | browser will hang. Download one company or one year only. |
| A5 | Zip incomplete | retry; do not extract a half-downloaded zip. |
| A6 | Click does nothing | try ⋯ → Open. PDF is a scan of handwriting → preview shows image, search inside will not find words (A8). |
| A7 | Grey icon instead of photo | wait; first view builds thumbs. SVG logo looks wrong → use PNG for logos (M1). |
| A8 | I typed a sentence from a PDF and got nothing | expected today. Search the file name or open the folder. |
| A8 | Indexer would slow the 30 GB server during 123 GB ingest | do not enable during the big upload. |
| A9 | Tag missing for colleagues | use a collaborative tag, not a private one. |
| A9 | Too many random tags | partners should publish a short list. |
| A10 | Star missing for a colleague | they must star it themselves. It is not a team pin. |
| A11 | Colleague sees no comment | they have no access to the file (share first, C1). |
| A11 | No email about the comment | SMTP not configured (N2); use the bell. |
| A12 | Empty activity | file is on S3 Backup_data and some events are thinner; open, download, then check again. Firm-wide audit is J. |
| A13 | Size 0 | upload failed; delete stub and upload again. |
| A14 | Red mount / DNS bucket error | do not rename the AWS bucket; implementer fixes occ config. |
| A14 | Sharing inside Backup_data fails | U3: Enable sharing on mount 1 is still missing. Use Firm folders for shares until admin ticks sharing on the mount. |
| A14 | Uploading 123 GB into Firm home | fills 30 GB disk. Bulk must stay in Backup_data. |
| A15 | I locked it but a colleague still opened it | known on this version. Agree in Talk who edits. Use copies named _working. |
| A16 | Cannot move into Backup_data | permission or S3 share-off (A14). |
| A16 | Copy of huge tree | do not; it doubles storage. |
| A17 | Sort does not apply to search results the same way | open the folder instead. |
| A18 | Preference resets | it is per browser; set again. |
| B1 | Read-only | share is View only (C1). |
| B1 | Editor blank | pop-up blocked; allow. Two heavy editors at once on this small server can crash — close extra tabs. |
| B2 | Huge workbook / pivot very slow | download and use desktop Excel, then upload. |
| B2 | Macros (.xlsm) | not a full Excel; do not expect macros. |
| B3 | Heavy animations missing | use desktop PowerPoint for show-night. File still stores. |
| B4 | Colleague cannot open ODT | B11 save as DOCX. |
| B5 | Second user kicked / read-only | close one session; check share is Edit. |
| B5 | CODE crash | save, wait, one user at a time. |
| B6 | I cannot find Track Changes | expected on this firm. Do not promise redlining to clients until Office is upgraded. |
| B7 | Comment not visible to other user | they must have Edit or at least open the same file. |
| B8 | Export PDF grey/error | known Collabora limit. Use print-to-PDF on the PC. |
| B9 | Trainee sees Partners | permission bug; tell admin (U2 was pass — should not happen). |
| B9 | Lost master | restore version (I2) or trash (I1). |
| B10 | No printers listed | it is your PC’s printers, not the cloud. |
| B11 | Need PDF | B8 is broken; use print-to-PDF (B8 workaround). |
| B12 | No versions on Backup_data file | S3 versioning is at AWS; Nextcloud sidebar versions are richer on disk files under Firm. Ask admin for AWS restore only if the file is gone. |
| B13 | Signed the only original | stop; restore version if any (I2). Certificate/DSC of ICAI class → this is not a replacement for emSigner/MCA DSC unless legal confirms. |
| B14 | Cannot type on a scan | it is an image. Use a Word cover or print and scan. |
| C1 | They still cannot see it | wrong user name; check Groups (K3). |
| C1 | They can edit a folder you wanted view-only | change permission, do not rely on honour. |
| C2 | New trainee not in group | they see nothing; add to group (K3), do not share 20 folders by hand. |
| C3 | Link opens for the whole internet | add password or revoke (C10). |
| C3 | Expiry stuck on today | type tomorrow’s date or ask admin to set default 7 days. |
| C4 | Cannot pick a future date | known glitch; try another browser or admin default. |
| C5 | Forgot password | revoke and make a new link. You cannot ‘see’ the old password. |
| C6 | They still screenshot | expected. Use for courtesy, not for secrets. |
| C7 | Random person edited | revoke immediately (C10); restore version (I2). |
| C8 | They can see other clients | wrong folder; revoke; tell admin. |
| C9 | I shared and they got no email | expected today. Call them or use Talk. |
| C10 | They still have a downloaded copy | revoke cannot erase their PC. That is why public links are dangerous. |
| C11 | Looking for Federated | it will not appear usefully. Ignore. |
| C12 | Empty list | you have not shared, or look under another account. |
| D1 | No user listed | they have no account (K1). |
| D2 | Too many rooms | archive or leave unused ones. |
| D3 | No sound | browser permission. Call with 8 people → will fail; use phone conference. |
| D4 | Video freezes with 4+ people | expected. Stop and use another product. |
| D5 | Black screen | browser blocked; or server too small — send the file. |
| D6 | Huge attach | upload to Files first, then share link. |
| D8 | No mic permission | allow in browser. |
| D10 | Unknown people in the room | disable guest access. |
| D11 | Old messages missing | they were in another room. |
| D12 | No invite in Outlook inbox | SMTP off (C9/N2). |
| D13 | Message arrives only when I open the app | expected delay without Client Push. |
| D14 | No lobby option | do not admit random public links. |
| D15 | Cannot kick | you are not the moderator. |
| E1 | Event in the wrong timezone | Personal settings → timezone Asia/Kolkata (server is Kolkata). |
| E2 | Partner cannot edit | share was View only. |
| E4 | Need one skip date | set exception / delete one instance, not the series. |
| E5 | No reminder email | expected. |
| E6 | Outlook 405/auth fail | app password, not login password. WebDAV skip on WinSCP does not block CalDAV. |
| E7 | Everyone looks free | they never shared calendars. |
| E8 | Attach too big | put in Files and paste a share link. |
| E9 | No button | create the Talk room by hand (D2). |
| E10 | Empty book | nobody imported yet (E12). |
| E11 | Duplicates on phone | disable iCloud contacts for that account or merge once. |
| E12 | Gmail export | export as vCard, then import. |
| E13 | Task not on phone | enable Tasks sync if the app offers it. |
| F1 | Board missing for colleague | share the board (F9). |
| F2 | Too much text | put the paper in Files and attach (F7). |
| F3 | Cannot assign | person not on the board share. |
| F4 | No email ping | SMTP off; look at Deck daily. |
| F7 | Attached the only original and then deleted in Files | restore (I1). |
| F9 | Trainee saw Partners board | unshare; U2 style groups. |
| F10 | App missing | admin enable Time Manager. Do not install random time apps. |
| F11 | Excel shows junk characters | open via Data → From text UTF-8. |
| G1 | Not secure / wrong host | you typed a different address. Never ignore the certificate warning. |
| G2 | Disk full | you ticked too many folders. Untick Backup_data. |
| G2 | SAVEPOINT errors | Pause; do not Remove the pair. |
| G5 | 2FA code | use authenticator; SMTP will not send codes by mail if mail is off. |
| G6 | Files app integration: enable Nextcloud in Files | Browse → ⋯. |
| G7 | Personal photos in a client folder | delete (I1) and turn auto upload off. |
| G8 | Stale copy | open online to refresh. |
| G9 | Office on PC says file is 0 bytes | wait for hydrate, or make available locally. |
| G10 | Missing company on laptop | it was not ticked, not lost in cloud. |
| G12 | WinSCP 405 | use desktop client or Cyberduck. Do not ask for SSH. |
| H1 | Browser warning | stop; tell admin. Do not click Advanced → proceed. |
| H3 | I encrypted a folder and Office will not open | expected. Restore from backup if you have one; otherwise data may be lost. |
| H4 | Password rejected | add length, not your company name. |
| H5 | I am blocked | wait 30 minutes; admin unban if needed. |
| H6 | Cannot log in from home after a change | this feature; admin must allow your IP or turn it off. |
| H7 | Kicked while working | save more often; idle was long. |
| H8 | App scripts fail | slow down; not a reason to disable security. |
| H9 | Access through untrusted domain | wrong URL. |
| H10 | A browser extension breaks the page | try Incognito without extensions. |
| H11 | Virus scan not running | expected. Scan doubtful files on the PC first. |
| H13 | Someone asks you to open port 22 | refuse. |
| I1 | Not in trash | expired or never deleted (wrong folder). Ask admin (I5). |
| I2 | No versions | file never changed, or S3 object without NC versions (B12). |
| I3 | Restore button missing | no permission or no versions. |
| I4 | Select limit | restore in batches. |
| I5 | Admin says no copy | it is gone; this is why we do not empty trash. |
| I6 | S3 console looks empty of ‘files as folders’ | normal; use Nextcloud, never dump via console. |
| I7 | Need a file from last month on the OS disk | 7-day window may have expired. |
| I8 | SAVEPOINT errors | pause uploads; not a restore drill. |
| I9 | I thought MCA papers were in Glacier | they are not, unless a new project is signed. |
| I10 | Bombay-wide outage | wait on AWS; this is not a second country copy. |
| I11 | We have immutable backups | not true today. |
| J6 | No CSV | J10. |
| J10 | No button | implementer exports; not a staff feature today. |
| J13 | Committee asks for 2019 logs | may not exist if retention is shorter. |
| J14 | I did not do that download | ask admin if someone impersonated. |
| K1 | User syncs 123 GB to a 256 GB laptop and fills it | teach G10. |
| K2 | CSV encoding | save UTF-8. |
| K3 | Person in two groups with different rights | the wider right usually wins; test with a dummy file. |
| K4 | Quota exceeded | delete from home or raise quota carefully — not by growing EBS. |
| K5 | Disabled but desktop client still uploads | wait session expiry; revoke app passwords (Security). |
| K6 | Reset mail never arrives | SMTP off; use verbal. |
| K7 | Sub-admin deleted a partner | too much power; remove sub-admin. |
| K8 | Used on a partner without asking | governance issue, not a glitch. |
| K9 | Everyone can see Partners | fix shares now. |
| K10 | App broke login | disable it. |
| K11 | Red HPB | ignore for files work; see D4. |
| L2 | Implementer asks for root password in chat | refuse. |
| L4 | Browser zip of Backup_data hangs | expected; ask admin. |
| M1 | Old logo | cache; Ctrl+F5. |
| M6 | No branded mail | no mail at all today. |
| N1 | Empty bell | no events, or you were the actor. |
| N2 | Committee wants email audit of shares | not until SMTP. |
| N3 | Delayed push | expected. |
| N5 | They were offline and got nothing | tell them in Talk. |
| N6 | Turning everything off | you will miss shares; keep files + mentions on. |
| O1 | Tags do not appear by themselves | tag by hand (A9). |
| O3 | Files vanished after 30 days | check trash (I1) and whether someone enabled retention. |
| O6 | Jobs stuck | implementer, not a staff click. |
| P1 | No Analytics menu | expected. |
| P4 | No Guest type in Users | expected today; use C5 password links carefully or create a normal user with quota 0.1 GB. |

If a feature note says **Not configured**, stop looking in menus — it is not live. If a live feature is missing for you, you probably lack Share permission; ask a partner. Server, AWS, disk size, Glacier, virus scan, and large video meetings are implementer work, not staff clicks.
