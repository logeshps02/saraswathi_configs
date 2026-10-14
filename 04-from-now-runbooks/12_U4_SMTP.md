# U4 — SMTP (mail invites, calendar, share mail)

**Who:** `saraswathi.admin` + `logesh.implementer` if SES/DNS needed
**When:** After U1 (users exist). Can be before or after M3.
**Do not:** put SMTP password, SES secret, or recipient emails in git/chat. Do not enable NAT to “make SMTP work” without asking. Do not create a third budget.

There is **no NAT** today. Many SMTP hosts need outbound 587. From this VPC, **direct SMTP to the internet may fail**. Typical working options:

| Option                                       | Notes                                                                                                    |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Amazon SES** in `ap-south-1`       | Fits AWS; may need SES sandbox lift; SMTP user IAM. Outbound 587 to SES endpoint —**test first**. |
| Existing firm mailbox (Gmail/Workspace/M365) | App password; may block EC2 IPs.                                                                         |
| Skip mail                                    | In-app notifications still work. Invites given verbally.                                                 |

**SSM launch:** AWS MFA as `logesh.implementer` → Mumbai → EC2 → `saraswathi-nextcloud-app` → **Connect** → **Session Manager** → **Connect**. `sh`, one line. No port 22.

**Why no mail when you share:** Overview already said **Email test** is not configured. Share **email** needs U4. The **bell** in Nextcloud is in-app only (recipient must be logged in). No NAT. Do not put passwords in chat.

**Test outbound before buying anything (SSM):**

```sh
timeout 5 bash -c 'echo >/dev/tcp/email-smtp.ap-south-1.amazonaws.com/587' ; echo SMTP_TCP:$?
```

If this hangs/fails, **ask Copilot** before creating SES. Do not open security group 587 inbound. Outbound is the question.

**Live:** `SMTP_TCP:0` (2026-09-02). TCP to SES Mumbai works. Next = create the **relay** (or skip mail). Do **not** open inbound 587. Do **not** NAT.

---

## 0. Amazon SES (after TCP 0) — or skip

Pick **one**. Do not put emails, SMTP user names, or passwords in chat/git.

### Skip

Write `U4 provider: skipped`. In-app bell still works. Invites verbal. Go U5.

### SES (preferred on this account)

1. AWS `logesh.implementer` MFA → Region **Mumbai** `ap-south-1` → **Amazon SES**.
2. **Configuration: Identities** → **Create identity**.

**This form (exact):**

| Field | Set |
|---|---|
| Identity type | **Domain** (not Email address) |
| Domain | `t-saraswathi.in` — type it; no space; no `www` |
| Assign a default configuration set | **off** |
| Assign to a tenant | **off** |
| Use a custom MAIL FROM domain | **off** for first test (DMARC later) |
| DKIM | **Easy DKIM** (not BYODKIM / Deterministic) |
| DKIM signatures | **Enabled** |
| Advanced → Publish DNS records to Route53 | **on** (domain is already in Route 53). This adds **CNAME** DKIM records only |
| Tags | leave empty. Do not Add new tag |

3. **Create identity**. Wait until identity **Verification** is **Verified** (minutes). Do **not** edit NS, delete the hosted zone, or transfer the domain. Do **not** touch the `files` A record.
5. If verification stays **Pending** (live 2026-09-02: identity created, **DKIM configuration Pending**, MAIL FROM not started — OK):

**Publish the three DKIM CNAMEs (do not change NS):**

1. Same identity page → **Authentication** → DKIM → **Publish DNS records** (or **Publish DNS records to Route53**).
2. Confirm. SES writes **three CNAME** `*._domainkey.t-saraswathi.in` into the **existing** hosted zone.
3. If that button is missing: Route 53 → Hosted zones → `t-saraswathi.in` → **Create record** is **not** first choice. Prefer SES publish. Manual only if SES shows the three CNAME **name / value** pairs — create **CNAME** only. Do **not** edit NS, SOA, or the `files` A record.
4. Wait 5–30 minutes. Refresh the identity. **Identity status** must become **Verified** and DKIM **Successful**.
5. Skip **Custom MAIL FROM**, **Delete**, **Virtual Deliverability Manager**, **Send test email** in SES until Verified.
6. Do not paste ARN, full CNAME values, or emails in chat. Record only: `U4 SES identity: pending / verified`.
5. Sandbox: you can send **only** to verified addresses until production access. Optional: also create an **Email address** identity for the From mailbox CS owns (same page, type Email address) if CS does not want whole-domain From yet.
4. Still sandbox until AWS **production access** is approved. Sandbox = From and To must both be verified. Request production only if CS wants mail to arbitrary staff. Do not invent a support ticket text with personal data in git.
6. SES left menu → **SMTP settings**. You need **Create SMTP credentials** (IAM user for Nextcloud).

**Wrong page (2026-09-02):** wizard **Step 2 Advanced settings** with Traffic policy / Rule set / IAM role / Network type Public|Private / Ingress / TLS policy. That is **Mail Manager / email receiving**, not outbound SMTP. Click **Cancel**. Do **not** Next. Do **not** create a traffic policy, rule set, ingress endpoint, or PrivateLink.

**Right page (live 2026-09-02):** SES → **SMTP settings** shows two boxes.

| Box | Button | Use? |
|---|---|---|
| **Mail Manager SMTP** (Secrets Manager, traffic policies, extra charges) | Create SMTP credentials | **No.** That wizard is Mail Manager. Cancel if opened. |
| **IAM SMTP credentials** (manual, no traffic policies) | **Create IAM credentials** | **Yes.** Classic SES SMTP user for Nextcloud. |

1. Click **Create IAM credentials** (lower box only).
2. IAM user name can stay the default → create.
3. Copy SMTP username + password to the **password manager only**. Never paste here. Never put in RESULTS. Do not save the CSV in this git folder.
4. Endpoint in Nextcloud: `email-smtp.ap-south-1.amazonaws.com` port **587** STARTTLS.

**If credentials were pasted in chat:** they are burned. Do **not** use that pair in Nextcloud.

1. IAM (can be Global) → **Users** → the `ses-smtp-user.*` just created → **Delete** (or SES SMTP settings → IAM credentials → delete that user).
2. SES Mumbai → SMTP settings → **Create IAM credentials** again.
3. Save the **new** pair only in the password manager. Never paste in chat.

If CS already has Workspace/M365 SMTP: use that host instead; EC2 public IP may still be blocked by Google/Microsoft — then SES is easier.

---

## 1. Nextcloud mail settings (when a relay exists)

Administration settings → **Basic settings** → **Email server** (Hub 26 layout). Do not enable **Mail Providers**. Do not change Background jobs / cron. Do not turn on Windows filename restriction for this.

**If CS only has personal mailboxes (no firm inbox on t-saraswathi.in):**

- **From** may still be `noreply` + domain `t-saraswathi.in` (domain identity is **Verified**). Nobody needs to *receive* at that From.
- **Send test** / staff mail in **sandbox** can only go to a **verified SES identity**. Verify the personal address as an **Email** identity (SES → Create identity → Email address → click the Amazon mail). Do **not** type that address in chat.
- Later production access: can send to any staff mailbox. Still prefer From `@t-saraswathi.in`.

| Field | Set |
|---|---|
| Send mode | **SMTP** |
| Encryption | **None / STARTTLS** (this is STARTTLS) |
| From → Email | `noreply` or `files` (no `@`) |
| From → Domain | `t-saraswathi.in` |
| Server address → Host | `email-smtp.ap-south-1.amazonaws.com` |
| Port | **587** |
| Authentication | **on** |
| Login | SES **SMTP user name** (new pair after rotate; password manager) |
| Password | SES **SMTP password** (never paste in chat) |

1. **Save settings**.
2. **Before Send test email:** Nextcloud sends the test **to the logged-in user’s account email**. If you see *You need to set your account email… /settings/user* — that is **not** an SES fail.

   1. Open https://files.t-saraswathi.in/settings/user (or avatar → **Personal settings** → **Personal info**).
   2. **Email** field: the **same personal mailbox** you verified in SES as an **Email address** identity (sandbox). Do not put it in chat.
   3. Save. Stay logged in as `saraswathi.admin`.
   4. Back to Administration → Basic settings → **Send test email**.

3. Leave **Mail provider** / Collaborative tags / cron alone.

**Pass:** “Email sent” and that inbox receives it (spam).
**Fail:** timeout / 454 / 535 / MessageRejected sandbox → error **text only**, no addresses. If sandbox reject: that To is not a verified SES identity yet.

**If UI says** `Email could not be sent. Check your mail server log` **(2026-09-02):** account email is set; SMTP handshake or SES rejected. Do not paste passwords.

Confirm on the form (values stay in the browser, not in chat):

- Encryption is **STARTTLS** (not None), port **587**
- Host is exactly `email-smtp.ap-south-1.amazonaws.com` (no `https://`)
- Login is the **SMTP user name** from SES (looks like `AKIA…`), **not** `logesh.implementer` and **not** the IAM user name `ses-smtp-user.…`
- Password is the **SMTP password** from the **rotated** create (not the pair that was in chat)
- From domain `t-saraswathi.in`

SSM, one line (redacts `@…` so addresses stay out of chat):

```sh
sudo grep -E 'mailer|SMTP|Swift_|MessageRejected|Could not authenticate' /opt/nextcloud/data/nextcloud.log | tail -n 8 | sed 's/@[^ ]*/@REDACTED/g' ; echo MAILLOG:$?
```

Paste **MAILLOG** plus the error words only (`MessageRejected`, `535`, `454`, `Could not authenticate`). No host user, no addresses.

**Live MAILLOG (2026-09-02):** old lines `127.0.0.1:25` are **before** SES was saved — ignore. Latest **Send test** is **554** from SES Mumbai: SMTP login **works**. Sandbox rejected **From and/or To** as not verified identities. Do not paste addresses from the log into chat.

**Fix 554 sandbox (do this, then Send test again):**

1. SES Mumbai → **Identities** → `t-saraswathi.in` still **Verified**. If not, stop.
2. **Create identity** → type **Email address** (not Domain) → the **exact** mailbox in Personal settings for `saraswathi.admin` (same spelling). Do not type it in chat.
3. Open that inbox → Amazon “verify email address” → click. SES identity **Verified**.
4. Nextcloud From stays `noreply` @ `t-saraswathi.in` (domain already verified).
5. Personal email **must match** that verified identity. Save Personal info if you change it.
6. Administration → Basic settings → **Save settings** → **Send test email**.

Until SES **production access** is approved, every **To** (staff) must be a verified Email identity. Domain verify covers **From** `@t-saraswathi.in` only.

---

## 1b. Request SES production access (CS chose this 2026-09-02)

**What it does:** after AWS approves, sandbox **To** restriction lifts. Nextcloud can mail existing staff inboxes. **From** stays `noreply@t-saraswathi.in`. No extra monthly SES fee. No new mailboxes. No MX.

**Do not:** Mail Manager, WorkMail, ingress/PrivateLink, NAT, change NS/MX/`files` A, paste addresses or SMTP secrets in the form, chat, or git.

**Console (Mumbai only):**

1. AWS as `logesh.implementer` MFA → Region **Mumbai** `ap-south-1` → **Amazon SES**.
2. Left: **Account dashboard** (sometimes **Get set up**).
3. **Request production access** (or **Edit your production access**). If the page is Traffic policy / Ingress / Mail Manager, **Cancel**.
4. Fill **only** this. Type; do not paste staff mailboxes.

| Field | Set |
|---|---|
| Mail type | **Transactional** (not Marketing) |
| Website URL | `https://files.t-saraswathi.in` |
| Use case | `Transactional mail from Nextcloud document system: share notifications, password reset, calendar reminders. Low volume, firm staff only. Not bulk marketing. From address on verified domain t-saraswathi.in. Recipients opt-in as account holders. Bounces/complaints will be acted on; sending stops if complaint rate is high.` |
| Additional contact | leave empty (or firm ops inbox if CS already uses it — do not type it in chat) |
| Checkboxes | accept SES sending / AUP as shown |

5. **Submit**. Do not open a Support case with personal addresses. Do not attach user lists.
6. Record only: `U4 SES production: requested` (date). Wait until Account dashboard **Production access** = **Enabled** (hours, sometimes 1 business day). If **Denied**, stop and ask — do not resubmit with emails in the text.
7. After **Enabled**: Nextcloud SMTP unchanged (same host 587, same From). Administration → Users → put each user’s **existing** mailbox in the email field (do not paste here). Then section 3 share mail.

**Pass:** dashboard Enabled, not Sandbox. **Cost:** still pay per email sent only (~$0.10 / 1,000 in Mumbai). Not a new budget line.

**Live 2026-09-02:** Support case **SES: Production Access**, region `ap-south-1`, Mail Type TRANSACTIONAL, website `https://files.t-saraswathi.in`. Status **Pending customer action**. AWS asked for sending process (frequency, lists, bounces/complaints, sample content). Domain `t-saraswathi.in` is already **Verified**. Reply in **that same case** (Support Center → Reply). Do not open a second case. Do not paste recipient addresses, SMTP secrets, or the case “Opened by” mailbox in chat/git.

**Reply text (copy into the case; type, do not add mailboxes):**

```
Follow-up for SES production access, region ap-south-1.

Use case: Transactional email only from our firm document system (Nextcloud) at https://files.t-saraswathi.in. Not marketing, not bulk, not purchased lists.

Identity: Domain t-saraswathi.in is already Verified in ap-south-1 with Easy DKIM. From address will be noreply@t-saraswathi.in. We do not send as unverified domains.

Volume and frequency: Low. Typical events are (1) user-initiated share notifications when a file/folder is shared, (2) password-reset mail when a user requests it, (3) optional calendar reminders the user set. Expected volume is tens of messages per week at go-live, not thousands per day. No campaigns, no newsletters.

Recipients: Only people who already have a user account on that system (firm staff). Addresses are entered by an administrator on the account, not scraped or bought. No third-party lists.

How lists are maintained: Recipients are the email field on Nextcloud user accounts. When a person leaves, the account is disabled/removed and mail to that address stops. No separate marketing list.

Bounces, complaints, unsubscribes: These are transactional notices for an internal tool, not subscription mail. If SES reports a bounce or complaint, we will stop sending to that address, correct or remove the account email, and investigate. We will not retry hard bounces. Unsubscribe links are not applicable the same way as marketing; users can clear the email on their account or ask admin to remove it.

Sample content (no personal data):
Subject: File shared with you
Body: A folder was shared with your account on https://files.t-saraswathi.in. Sign in to view it. If you did not expect this, contact your administrator.

Please enable production access in ap-south-1. Thank you.
```

After submit, record `U4 SES production: reply sent`. Wait for **Enabled**. If they ask for a recipient list or sample with real inboxes, **stop** and ask Copilot — do not attach user emails.

**Live:** follow-up **sent** 2026-09-02. No AWS reply yet is **normal** (they said initial response within 24 hours; grant may be same day or later). Do not send a second reply. Do not open a new case. Do not chase with extra mailboxes. Refresh Support Center later. Meanwhile **U5** (devices) does not need production. Share-mail UAT waits until dashboard **Enabled**.

If 554 still lists `noreply@` / `files@` after domain Verified: From Domain field has a typo/space — retype `t-saraswathi.in` with no space.

**If Send test still fails after Email identity Verified:** identities do not match, or SES still lists From. Do not paste addresses.

SSM (latest test only):

```sh
sudo grep mailtest /opt/nextcloud/data/nextcloud.log | tail -n 1 | sed 's/@[^ "\\]*/@REDACTED/g' | grep -oE '554[^"]*|535[^"]*|Message rejected[^"]*|Could not authenticate[^"]*|Email sent' ; echo MAILTEST:$?
```

If `MAILTEST:1` and no text: last line had no 554/535 (or no new `mailtest` row). SSM is `sh` — paste **one** python line (not a multi-line block; `>` means the previous line did not finish).

If python prints only `Email could not be sent. Check your mail server log` that is the **UI** string. SES 554 is in `exception.Previous.Message`. Walk Previous (one line):

```sh
sudo python3 -c "import json,re; last=None
[None for line in open('/opt/nextcloud/data/nextcloud.log') if ('mailtest' in line or 'Email setting test' in line) and (last:=line)]; d=json.loads(last); msgs=[]; ex=d.get('exception');
while ex: msgs.append(ex.get('Message') or ''); ex=ex.get('Previous');
print(re.sub(r'[\w.+-]+@[\w.-]+','REDACTED',' | '.join([m for m in msgs if m]) or d.get('message',''))[:800]); print('MAILPY3:0')"
```

SMTP codes without dumping the JSON (one line):

```sh
sudo grep -oE '554[^"\\]{0,120}|535[^"\\]{0,80}|Expected response code[^"\\]{0,160}|Could not authenticate[^"\\]{0,80}' /opt/nextcloud/data/nextcloud.log | tail -n 5 ; echo SMTPCODE:$?
```

Mail is **system** config, not `config:app:get core` (`HOST:1` was expected). Do **not** `config:list`. Do **not** get `mail_smtpname` / `mail_smtppassword`.

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:get mail_smtphost ; echo HOST:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:get mail_smtpport ; echo PORT:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:get mail_smtpmode ; echo MODE:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:get mail_smtpsecure ; echo SECURE:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:get mail_from_address ; echo FROMLOCAL:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:get mail_domain ; echo FROMDOM:$?
```

Keys only (no values, no password):

```sh
sudo grep -oE "'mail_[a-z_]+'" /var/www/nextcloud/config/config.php ; echo MAILKEYS:$?
```

**Pass:** host `email-smtp.ap-south-1.amazonaws.com`, port `587`, mode `smtp`, secure `tls` or empty/`ssl`, from local `noreply` or `files`, domain `t-saraswathi.in` (no space). `HOST:1` / empty host = **Save settings** did not write — fill Email server, Save, then Send test.

**Live 2026-09-02:** HOST/PORT/MODE/FROMLOCAL pass. `SECURE:1` (unset). `FROMDOM` printed `t-saraswathi.in` plus **ZWSP** (browser paste). SMTPCODE: `554` AP-SOUTH-1 identity failed starting `Nextcl` (truncated From display `Nextcloud <noreply@…>`). MAILKEYS includes password/name — do not print those values.

If `FROMDOM` looks like `t-saraswathi.in` but SES 554 still names From: measure length (must be **16**). Then rewrite domain and STARTTLS with **typed** values (do not paste the domain):

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:get mail_domain | python3 -c "import sys; s=sys.stdin.read().strip(); print('DOMLEN',len(s))"
```

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:set mail_domain --value=t-saraswathi.in ; echo SETDOM:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:set mail_smtpsecure --value=tls ; echo SETTLS:$?
```

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:get mail_domain | python3 -c "import sys; s=sys.stdin.read().strip(); print('DOMLEN',len(s)); print('DOMOK' if s=='t-saraswathi.in' else 'DOMBAD')"
```

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:get mail_smtpsecure ; echo SECURE:$?
```

**Pass:** `t-saraswathi.in` is **15** chars. Live: first `DOMLEN 16` (ZWSP), after `occ set` `DOMLEN 15` `DOMOK`, `tls` / `SECURE:0`. Do **not** paste Domain in the Email server form (reintroduces ZWSP). Send test now. If the form still shows a pasted domain, **type** `t-saraswathi.in`, Encryption STARTTLS, Save, then Send test.

Do not dump `config.php`. Do not get `mail_smtpname` / `mail_smtppassword`.

**Match check (browser, say yes/no only):**

1. SES Identities: domain `t-saraswathi.in` **Verified**.
2. SES Identities: **one Email address** row **Verified** (the personal inbox).
3. Nextcloud Personal info email is **character-for-character** that SES Email identity (same mailbox, no extra space). If you verified a different Gmail than the one in Personal settings, 554 continues.
4. From Email `noreply` Domain `t-saraswathi.in` — no space, no `www`.
5. Save settings again, then Send test.

Optional: SES → that Email identity → **Send test email** from the AWS console (To = itself). If AWS console send works but Nextcloud fails, it is From/Personal mismatch. If AWS console also 554, identity is not Verified in **ap-south-1**.

---

**Live 2026-09-02:** NC send-test **yes** after `mail_domain` DOMLEN 15 + `mail_smtpsecure=tls`. Do not paste Domain in the form.

---

## 2. User email on accounts

1. Administration → Users → each user → **email** field.
2. Save. They will get reset/share mail only if SMTP passed.
3. **Sandbox:** each **To** must be a SES **Email address** identity **Verified** in `ap-south-1`, or share mail 554. Domain verify covers From only. Do not paste addresses. Skip this section until production access if staff mailboxes stay unverified.

---

## 3. Share notification mail (C9)

1. Admin share a dummy folder `_uat-share-mail` to `partner1`.
2. Partner mailbox: share mail arrived **or** only in-app bell.
3. Record which.

---

## 4. Calendar reminder (E5)

1. Calendar → `_uat-event` → reminder **email** 5 minutes (or 1 hour).
2. If SMTP down, skip. In-app reminder is optional.

---

## Paste / record

```
U4 outbound 587 test: 0 / fail / skip
U4 provider: SES / firm mailbox / skipped
U4 NC send-test: yes/no
U4 SES production: requested / Enabled / Denied / skip
U4 share mail to partner: yes / in-app only / skip
U4 calendar email reminder: yes/skip
```

Never write the SMTP password.
Next: [13_U5_DESKTOP_MOBILE_WEBDAV.md](13_U5_DESKTOP_MOBILE_WEBDAV.md)
