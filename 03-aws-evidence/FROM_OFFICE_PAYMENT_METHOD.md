# Office — Unlock billing and add the Saraswathi card

`logesh.implementer` cannot add a card until root turns on IAM billing access.
The partner signs in as root. You point at the screen. Never write the card number in this file.

## A. Sign out of the IAM user

1. Top-right: click **Saraswathi**.
2. Click **Sign out**.
3. Close extra AWS tabs.

## B. Partner signs in as root

1. Open `https://console.aws.amazon.com/`
2. Choose **Root user**.
3. Root email = the Saraswathi account email.
4. Partner types the root password.
5. Partner types the MFA code from **their** phone.
6. After login, top-right should still show **Saraswathi** and must **not** show `logesh.implementer`.

## C. Allow IAM users to see billing

1. Top-right: click **Saraswathi**.
2. Click **Account**.
3. Scroll to **IAM user and role access to Billing information**.
4. Click **Edit**.
5. Tick **Activate IAM access**.
6. Click **Update**.

## D. Add or confirm the payment card

1. Paste this and press Enter:

`https://console.aws.amazon.com/billing/home#/paymentmethods`

2. If a card is already listed, do not add another unless it is expired. Note last 4 digits only.
3. If no card:
   - Click **Add a payment method** or **Add credit or debit card**
   - Cardholder name = Saraswathi / partner name on the card
   - Number, expiry, CVV = partner types these
   - Billing address = Saraswathi address
   - Phone = partner phone
   - Save
4. Complete bank OTP / small verification charge if asked.
5. Default payment method must be this Saraswathi card.

## E. Make sure invoices can be emailed

1. Left menu: **Billing preferences**.
2. Enable **PDF invoice by email** if shown.
3. Enable **Receive billing alerts** if shown.
4. Save.

## F. Create a budget if none exists

1. Left menu: **Budgets**.
2. If a budget already exists, skip this section.
3. Click **Create budget**.
4. Use a template or **Customize** → **Cost budget**.
5. Name: `Saraswathi-Monthly-AWS-Budget`
6. Period: Monthly.
7. Amount: `10000` INR unless the partner chose another ceiling.
8. Alerts at 50%, 80%, 100%.
9. Email = partner / Saraswathi billing email. Not only your Gmail.
10. Create budget.

## G. Sign out of root

1. Top-right: **Saraswathi** → **Sign out**.
2. Do not take the root password home.

## H. Confirm your IAM user can now see Payments

1. Sign in as `logesh.implementer` + your MFA.
2. Open `https://console.aws.amazon.com/billing/home#/paymentmethods`
3. You should see the card last 4 digits, not the Access denied banner.

If it still says no permission:

1. Search `IAM` → User groups → `Firm-Implementers`
2. Permissions → Add permissions → Attach policies
3. Search `Billing`
4. Tick the AWS managed policy **Billing**
5. Add, then refresh Payment methods.

## Stop

Do not create EC2. Do not change the domain. Go home after the card is visible.
