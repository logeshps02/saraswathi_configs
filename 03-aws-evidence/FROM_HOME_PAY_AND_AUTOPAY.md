# From Home — Pay past due + turn on Auto-pay (AISPL)

**Account:** Saraswathi `055855670388`  
**Seller:** AISPL (AWS India) — invoices in **INR**  
**Past due (as of this chat):** **₹900.39** — Health `AWS_BILLING_ACCOUNT_PAST_DUE` **9 Sep 2026**  
**Invoice to look for:** Bills period **August 2026**  
**Who:** try `logesh.implementer` + MFA first. If **Access denied**, partner as **root** (same as [FROM_OFFICE_PAYMENT_METHOD.md](FROM_OFFICE_PAYMENT_METHOD.md)).  
**Do not** type card number, CVV, OTP, or passwords in chat or git. Partner types those on screen.

Do **not** stop EC2. Do **not** create a third budget. Budget `Saraswathi-Monthly-AWS-Budget` $60 already exists.

---

## 0. Open Billing

1. Sign in AWS (Mumbai can stay; Billing is global).
2. Top search: **Billing** → **Billing and Cost Management**.
3. If you see **Access denied**, stop. Partner does root + IAM billing access (office payment-method file), then you retry.

---

## 1. Confirm a card exists (needed for both pay and Auto-pay)

Paste:

`https://console.aws.amazon.com/billing/home#/paymentmethods`

| What you see | What to do |
|---|---|
| A card, last 4 only | Keep it. Note last 4. Set as **Default** if not already. |
| Expired / declined | Partner adds a new card. Do not keep two defaults. |
| Empty | **Add payment method** → credit/debit card. Partner types number/expiry/CVV/OTP. Billing address = firm. |

Do **not** add a second card if a valid default already exists.

---

## 2. Pay the past-due invoice (₹900.39)

1. Left: **Bills** (or paste `https://console.aws.amazon.com/billing/home#/bills`).
2. Period: **August 2026** (past due was the August invoice).
3. Open the bill whose status is **Unpaid** / **Past due** / **Payment due**. Amount should be about **₹900.39** (small rounding OK).
4. Click **Pay** / **Make payment** / **Pay invoice** (wording varies).
5. Confirm payment method = the **default** Saraswathi card.
6. Partner completes bank **OTP** if asked.
7. Wait until status is **Paid** / **Payment successful**.
8. Top Health / Billing banner `AWS_BILLING_ACCOUNT_PAST_DUE` should clear (sometimes after a few minutes).

**If there is also a September invoice** still Open: that is current month, not the ₹900 past due. Pay **Unpaid/Past due** first. September can wait until month-end unless they want to pay early.

**If Pay is grey:** no valid default card, or IAM cannot pay — use root / add card.

Do **not** pay from a personal GPay/UPI outside AWS unless AISPL shows an official India payment option on that invoice page. Prefer the card on **Payment methods**.

---

## 3. Turn on Auto-pay

1. Left: **Payments** → **Payment preferences**  
   or paste `https://console.aws.amazon.com/billing/home#/paymentpreferences`
2. **Default payment method** = the same card (last 4).
3. Find **Pay invoices automatically** / **Auto-pay** / **Automatically pay invoices**.
4. Turn **On**.
5. Save / Update.

Also useful on the same or **Billing preferences** page:

- PDF invoice by email **On**
- Billing alerts **On** (partner/firm email, not only implementer Gmail)

Auto-pay charges the default card when each invoice is issued. It does **not** reverse September usage already accrued. It does **not** replace the $60 budget.

---

## 4. Paste back (no secrets)

- August 2026 invoice: Paid yes/no; amount
- Auto-pay: On yes/no
- Default card: last 4 only
- Past-due Health banner: gone yes/no

---

## Stop

Do not stop/terminate `i-002509b77963fd5fc`. Do not delete CloudTrail. Do not grow EBS. Do not recopy `F:\f`.
