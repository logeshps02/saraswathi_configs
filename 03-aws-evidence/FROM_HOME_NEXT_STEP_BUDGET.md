# From Home — Next Step: Monthly AWS Budget

RDS backups are Enabled 7 days. EBS snapshot `snap-0a1d21b760e5e6bf6` was created. Confirm that snapshot **Completed** first (see backup guide §4).

Then create a **cost budget**. Do not create extra users. Do not enable Fast Snapshot Restore. Do not create DLM this step.

Sign in as `logesh.implementer`. Region can stay Mumbai; Budgets is a billing feature (account-wide).

## Values

| Item | Value |
|---|---|
| Budget name | `Saraswathi-Monthly-AWS-Budget` |
| Type | Cost budget |
| Period | Monthly |
| Amount | `80` USD (alert ceiling; not a spend target) |
| Alerts | 50%, 80%, 100% actual |
| Email | firm billing contact already used for the AWS account — type it in the console; **do not paste it in chat** |

## 1. Create budget

1. Search **AWS Budgets** (or Billing → **Budgets**).
2. If `Saraswathi-Monthly-AWS-Budget` already exists, skip create; paste name + amount + last updated.
3. **Create budget**.
4. **Customize** (not a template) if offered.
5. Budget type: **Cost budget**.
6. Name: `Saraswathi-Monthly-AWS-Budget`
7. Period: **Monthly**. Recurring.
8. Budget amount: **Fixed** `80` USD.
9. Scope: **All AWS services** in this account. Do not filter to one service yet.
10. Alerts:
    - 50% of budgeted amount, **Actual**
    - 80% of budgeted amount, **Actual**
    - 100% of budgeted amount, **Actual**
11. Email: the firm billing address only. Do not paste that address into chat.
12. Tags: `Project=Nextcloud`, `Owner=Saraswathi`, `Environment=Production` if the form has tags.
13. **Create**.

## 2. Paste back (no email)

- Budget name
- Amount
- Period
- Alert thresholds (50/80/100)
- Status: Active or similar

Do not paste the notification email. Do not create a second budget.

## 3. Observed (2026-08-26)

Two budgets exist. Keep **one**.

| Name | Amount | MTD spend | Health |
|---|---|---|---|
| `Saraswathi-Monthly-AWS-Budget` | **$40** monthly | $9.44 (23.60%) | Healthy |
| `Saraswathi-Monthly-AWS-Budget_2` | **$50** monthly | $10.05 (20.10%) | Healthy |

Guide asked for **one** budget at **$80**. Duplicate `_2` was created by accident.

## 4. Delete the duplicate

1. Billing → **Budgets**.
2. Open `Saraswathi-Monthly-AWS-Budget_2`.
3. **Delete**. Confirm.
4. Leave `Saraswathi-Monthly-AWS-Budget` ($40). Optional: **Edit** amount to `80` if you want the original ceiling. $40 is a tighter alert; either is OK if only **one** remains.
5. Paste: remaining budget **name**, **amount**, and that `_2` is gone.

Do not buy Savings Plans or Reserved Instances.

## 5. Confirmed (2026-08-26)

Console: `"Saraswathi-Monthly-AWS-Budget_2" has been deleted successfully.`

| Item | Value |
|---|---|
| Remaining budget | `Saraswathi-Monthly-AWS-Budget` |
| Type | Cost budget |
| Amount | **$60.00** monthly (edited from $40; original guide $80) |
| Period | Monthly from 2026-08-01 |
| Health | Healthy |
| MTD | $9.44 of $60.00 (**15.73%**) |
| Forecasted vs budgeted (MTD) | 0.00% |
| Duplicate `_2` | **deleted** |

One budget remains. $60 is between the first $40 and the guide $80. Do not create another.

## Stop

Do not create a third budget. Do not paste notification emails. Do not buy Savings Plans or Reserved Instances.
