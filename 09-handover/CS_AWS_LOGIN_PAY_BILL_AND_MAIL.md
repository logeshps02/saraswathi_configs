# CS handout — AWS login, pay the bill, add mail

**For:** CS Saraswathi / billing partner (sit together at the office PC)  
**Written:** 2026-09-19  
**Account:** Saraswathi **055855670388**  
**Region to keep on screen:** Asia Pacific (Mumbai) / `ap-south-1`  
**Seller:** AISPL (AWS India) — invoices in **INR**

**This file never contains passwords, OTP, card numbers, CVV, MFA codes, or SMTP secrets.**  
Type those only on the AWS page. Do **not** put them in WhatsApp, email, or this folder.

Print this (or keep it on a second screen). Chrome or Edge. Padlock on every page.

---

## 0. Three different logins (say this first)

These are **not** the same username.

| What | URL | Who | Username | What it is for |
|---|---|---|---|---|
| **Files (staff daily)** | https://files.t-saraswathi.in | Staff + CS admin | e.g. `saraswathi.admin`, Sneka, Jayalakshmi… | Papers, Calendar, Deck, Tasks |
| **AWS IAM (implementer)** | Account-ID sign-in (below) | Logesh only | `logesh.implementer` + **his** MFA | Servers, trail, SES console |
| **AWS Root (firm owner)** | Root user sign-in | **Partner / CS** | **Root email** of this AWS account + **partner** MFA phone | Pay bills, add card, unlock billing |

**Staff do not log in to AWS.**  
**CS does not use** `logesh.implementer` unless Logesh is on the call and that is agreed.

**Root email:** the official mailbox used when this AWS account was created (firm-controlled). It is **not** written here on purpose. If CS forgot which mailbox: Logesh tells it **verbally**, not in chat/git.

**Passwords:** password manager / paper in the partner’s drawer. Change them if they were ever sent on WhatsApp.

---

## 1. How to log in to AWS (partner / CS)

### 1A. Prefer this for **pay bill / add card** — Root user

1. Close extra AWS tabs. If someone is already logged in as `logesh.implementer`: top-right **Saraswathi** → **Sign out**.
2. Open: `https://console.aws.amazon.com/`
3. Choose **Root user** (not IAM user).
4. Enter the **root email** (firm AWS mailbox).
5. Enter the **root password** (partner types it).
6. Enter the **MFA code** from the **partner’s** authenticator phone (not Logesh’s phone).
7. After login, top-right should show **Saraswathi** and must **not** show `logesh.implementer`.
8. Confirm account: top-right → **Account**. Account ID must be **055855670388**.
9. Top bar region: **Asia Pacific (Mumbai)**. If it shows N. Virginia / Ohio, change it to Mumbai. Billing still works either way; Mumbai avoids mistakes on SES later.

**If login fails:** stop guessing. Do not try Logesh’s IAM password as root. Recover only with the partner present (AWS “Forgot password” goes to the root email).

### 1B. IAM user login (Logesh, or CS only if you created an IAM user for her)

Use this URL (account ID already filled):

`https://055855670388.signin.aws.amazon.com/console`

| Field | Value |
|---|---|
| Account ID | `055855670388` |
| IAM user name | `logesh.implementer` (implementer) |
| Password | implementer password (not in this file) |
| MFA | that user’s authenticator app |

There is **no** documented extra IAM user named `saraswathi` for the console. Until you create one, **CS uses Root** for money.

### 1C. After any AWS session

Top-right → **Sign out**. Do not leave root logged in on a staff PC. Do not take the root password home on a USB note.

---

## 2. Pay the bill + turn on Auto-pay

**Fact as of 2026-09-12 (not re-checked in this file):** past due **₹900.39**, health `AWS_BILLING_ACCOUNT_PAST_DUE` **9 Sep 2026**, August **2026** invoice. Pay that first.

**Budget already exists:** `Saraswathi-Monthly-AWS-Budget` **$60**. Do **not** create another budget. Do **not** stop the server to “save money”.

**Who clicks:** partner as **Root** if IAM shows **Access denied**. Logesh as `logesh.implementer` only after IAM billing access is on (section 2D).

### 2A. Open Billing

1. Logged in (Root or IAM).
2. Top search: type **Billing** → **Billing and Cost Management**.  
   Or paste: `https://console.aws.amazon.com/billing/home`
3. If **Access denied**: skip to **2D**, then come back.

### 2B. Confirm the firm card

Paste:

`https://console.aws.amazon.com/billing/home#/paymentmethods`

| What you see | What to do |
|---|---|
| A card (last 4 only) | Keep it. Set **Default** if not already. Note last 4 on paper. |
| Expired / declined | Partner **adds a new card**. Do not keep two defaults. |
| Empty | **Add payment method** → credit/debit card. Partner types number, expiry, CVV, OTP. Billing address = firm. |

Do **not** add a second card if a valid default already exists.  
Do **not** type the card number into chat or this file.

### 2C. Pay the unpaid invoice

1. Left: **Bills**  
   or `https://console.aws.amazon.com/billing/home#/bills`
2. Period: **August 2026** (that was the past-due invoice).
3. Open the bill **Unpaid / Past due / Payment due**. Amount about **₹900.39** (small rounding OK).
4. **Pay** / **Make payment** / **Pay invoice**.
5. Payment method = the **default** Saraswathi card.
6. Partner completes bank **OTP** on their phone.
7. Wait until **Paid** / **Payment successful**.
8. The red past-due banner can take a few minutes to clear.

**September invoice** if still Open = current month, not the ₹900 past due. Pay **Unpaid/Past due** first. September can wait until month-end unless CS wants to pay early.

**If Pay is grey:** no valid default card, or this IAM user cannot pay → Root + add card (2B / 2D).

Prefer the card on **Payment methods**. Do not pay random GPay/UPI outside this page unless AISPL itself shows an official India option **on that invoice**.

### 2D. If IAM user cannot see Billing (one-time, Root)

Partner stays on Root:

1. Top-right **Saraswathi** → **Account**.
2. Scroll to **IAM user and role access to Billing information**.
3. **Edit** → tick **Activate IAM access** → **Update**.
4. Sign out of Root.
5. Logesh signs in as `logesh.implementer` + MFA and opens Payment methods again.

If still denied: IAM → User groups → `Firm-Implementers` → attach AWS managed policy **Billing**. CS does not need to do this alone.

### 2E. Auto-pay (so this does not happen every month)

1. Left: **Payments** → **Payment preferences**  
   or `https://console.aws.amazon.com/billing/home#/paymentpreferences`
2. **Default payment method** = same card (last 4).
3. **Pay invoices automatically** / **Auto-pay** → **On** → Save.

Same area or **Billing preferences**:

- PDF invoice by email **On**
- Billing alerts **On** (partner / firm email, not only implementer Gmail)

Auto-pay charges the default card when AWS issues the invoice. It does **not** undo September usage already accrued. It does **not** replace the $60 budget.

### 2F. What CS can write on a slip (no secrets)

- August 2026 invoice: Paid yes/no; amount  
- Auto-pay: On yes/no  
- Default card: last 4 only  
- Past-due banner: gone yes/no  

---

## 3. Add mail (so Files can email staff)

**What “mail” is here**

- Nextcloud (https://files.t-saraswathi.in) sends **share**, **password reset**, and optional **calendar/activity** mail.
- The From address is **`noreply@t-saraswathi.in`**.
- Amazon **SES** in **Mumbai** is the mail engine. Domain **`t-saraswathi.in`** is already **Verified** (Easy DKIM). Do **not** edit Route 53 NS, MX, or the `files` A record.

**Current limit (2026-09-19):** SES is still **sandbox**.  
AWS **denied** production access (case 5 Sep 2026). Do **not** reopen that case now. Retry about **3–5 Oct 2026**.  
Sandbox = you can send **only** to mailboxes that are **Verified identities** in SES. The **bell** in Files always works even when email does not.

**Wrong page:** anything named **Mail Manager**, Traffic policy, Ingress, PrivateLink. **Cancel**. That is not outbound mail.

### 3A. Add one person’s mailbox so they can receive mail (sandbox)

Do this **once per person** until production is approved.

**In AWS (Mumbai):**

1. Login (IAM `logesh.implementer` is enough for SES; Root also works).
2. Region **Mumbai**.
3. Search **Amazon SES** → **Amazon SES**.
4. Left: **Configuration** → **Identities** (not Mail Manager).
5. Confirm `t-saraswathi.in` is **Verified**. If not, **stop** and call Logesh.
6. **Create identity**.
7. Identity type: **Email address** (not Domain — domain already exists).
8. Type the staff mailbox **exactly** as they use it. Do not put that address in WhatsApp after the meeting.
9. Create. Staff opens that inbox → Amazon “verify email address” → click the link.
10. Refresh Identities until that email is **Verified**.

**In Files (admin):**

1. Login https://files.t-saraswathi.in as `saraswathi.admin`.
2. Users: `https://files.t-saraswathi.in/settings/users`
3. Open that staff user → **Email** field = the **same** mailbox just verified in SES.
4. Save. Do not screenshot the page with other people’s mail.

**Staff themselves:** avatar → **Personal settings** → **Personal info** → Email = same address.

Until production is **Enabled**, unverified inboxes **will not** get share/reset mail. Tell them to use the **bell**.

### 3B. What CS should **not** click for mail

| Do not | Why |
|---|---|
| Mail Manager / Create SMTP credentials (upper box) | Extra product, extra cost |
| Request production access this week | Already **Denied** 5 Sep 2026; wait ~3–5 Oct |
| New Support case with a list of staff emails | Do not paste addresses |
| WorkMail / new MX / change `files` DNS | Breaks the site |
| NAT Gateway | Not needed; costs money |
| Create a new SES domain | `t-saraswathi.in` already verified |

SMTP user for the server already exists. **Do not** create a new IAM SMTP user unless Logesh says the old pair was burned. **Never** paste SMTP username/password here.

### 3C. After SES production is one day **Enabled** (later)

Then you do **not** need a SES identity for every Gmail. You only:

1. Put each user’s mailbox on their Nextcloud user.
2. Keep From `noreply@t-saraswathi.in`.
3. Still: email is **not** sent on every file edit. Default is **bell**. Optional noisy activity emails are a Personal setting.

---

## 4. Do not touch (same sitting)

- Do **not** Stop / Terminate EC2 `i-002509b77963fd5fc` (the Files server).
- Do **not** Delete or Stop logging trail `Saraswathi-management-trail`.
- Do **not** Save **Edit trail** if the page is **Data events** (that turns costly logging back on) → **Cancel**.
- Do **not** grow the 30 GiB disk.
- Do **not** create a third budget.
- Do **not** empty the S3 files bucket.

---

## 5. Who holds what (fill in ink)

| Item | Name |
|---|---|
| AWS root email mailbox | (verbal — not in git) |
| Root password | Partner |
| Root MFA phone | Partner |
| Card / Auto-pay | Partner |
| IAM `logesh.implementer` | Logesh P S |
| Nextcloud `saraswathi.admin` | CS / admin |

---

## 6. 15-minute office script (CS + Logesh)

1. Explain table in **§0** (Files vs AWS).  
2. Partner: **§1A** Root login; confirm account **055855670388**.  
3. **§2B–2E** card, pay ₹900.39 if still unpaid, Auto-pay On.  
4. Sign out of Root.  
5. Logesh: SES **§3A** only for people CS wants to receive mail **now**.  
6. Tell staff: URL is **files.t-saraswathi.in**; AWS console is **not** their daily login.

If anything on Billing or SES does not match this page, **stop** and ask — do not invent a second account or a second domain.
