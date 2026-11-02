# Session 2026-11-02 — AWS cost optimisation (October bill)

**Operator:** Logesh P S (`logesh.implementer`), executed with Copilot via AWS CLI + SSM (no SSH, no port 22)  
**Account / region:** 055855670388 / ap-south-1 (Mumbai)  
**Approval:** client approved the plan on 2026-11-02 ("no one is using now, go ahead")  
**Result:** expected monthly bill **~$53–54** (was **$82.77** in October 2026), same performance, 24×7 kept.

No passwords, keys, or `config.php` contents are recorded here.

---

## 1. Why the bill went up

| Month | AWS usage | Credits | Tax | Paid |
|---|---|---|---|---|
| Aug 2026 | $19.20 | −$19.20 | – | $0 |
| Sep 2026 | $145.75 (ingest: S3 API + CloudTrail data events) | **−$120.39** | $4.56 | ~$30 |
| Oct 2026 | $70.14 | **none left** | $12.63 | **$82.77** |

October was the first full month without free credits. It shows the true run-rate.

October line items: EC2 t3.medium $33.09, RDS db.t4g.micro + gp3 $18.12, S3 $6.95, EBS volume + snapshots $5.75, public IPv4 $3.70, KMS $1.99, Route 53 $0.53, data transfer $0.88.

## 2. Read-only findings (before any change)

| Check | Value |
|---|---|
| EC2 CPU (30 days) | avg **2.6%**, CPU credit balance always full (576), no surplus credits charged |
| EC2 memory (CloudWatch agent) | avg 29%, peak **60%** of 3.7 GiB → keep 4 GiB RAM |
| RDS CPU / connections | avg 4.5% / avg <1 |
| S3 `saraswathi-nextcloud-files-055855670388` | 236 GB total, versioning on, no lifecycle rule |
| EBS snapshots | 7 daily AWS Backup + 1 manual (Aug) `snap-0a1d21b760e5e6bf6` not used by any AMI |
| Savings Plans / RIs | none |
| Budget | `Saraswathi-Monthly-AWS-Budget` $60 (exceeded: $82.20 actual) |
| Hard-coded old IP | `wopi_allowlist` contained `3.111.213.217` |

## 3. Changes made

| # | Time (IST) | Change | IDs | Effect |
|---|---|---|---|---|
| 0 | 18:24 | Backup of Nextcloud config on server | `/root/config.php.before-t3a-202611021254` | Safety only |
| 0 | 18:25 | Pre-change EBS snapshot | `snap-006094f30c8419f2a` (`saraswathi-pre-t3a-20261102`) | Safety only — delete after ~1 week stable |
| 1 | 18:25 | Allocated **Elastic IP 13.234.211.7** | `eipalloc-0cb0b191a0994190f` (`saraswathi-nextcloud-eip`) | Fixed public IP; same $0.005/hr as before |
| 2 | 18:26 | Office `wopi_allowlist` added new IP (old kept temporarily) | `richdocuments` app config | No break during IP move |
| 3 | 18:27 | Associated EIP to `i-002509b77963fd5fc` | `eipassoc-0e5928a0172ddb2eb` | Old auto IP `3.111.213.217` released |
| 4 | 18:27 | Route 53 `files.t-saraswathi.in` A → `13.234.211.7` (TTL 300) | change `C10319213ESNLUUVEI11Q` INSYNC | Users reach the new IP |
| 5 | 18:33 | Deleted manual snapshot from August | `snap-0a1d21b760e5e6bf6` | Daily AWS Backup (7 days) untouched |
| 6 | 18:34–18:35 | Stop → type **t3.medium → t3a.medium** → start | `i-002509b77963fd5fc` | **~47 s downtime**; same 2 vCPU / 4 GiB, AMD EPYC; private IP 10.20.1.144 unchanged |
| 7 | 18:37 | Final `wopi_allowlist` = `127.0.0.1,::1,10.20.1.144,13.234.211.7` | `richdocuments` | Old IP removed |
| 8 | 18:38 | **1-yr EC2 Instance Savings Plan**, t3a, ap-south-1, No Upfront, $0.0155/hr | `358b5613-3e8e-4db9-b9b5-92acf54ea648` (2026-11-02 → 2027-11-02) | Billing only; **active** |
| 9 | 18:38 | **1-yr RDS Reserved Instance**, db.t4g.micro MySQL Single-AZ, No Upfront, $0.017/hr | `saraswathi-nextcloud-db-ri-1yr` | Billing only; **payment-failed** (seen 23:29 IST). Not charged, not active — RDS still billed on-demand. Re-buy after AISPL payment is fixed (§7) |

## 4. Verification after the switch

| Check | Result |
|---|---|
| EC2 | `t3a.medium` running, `13.234.211.7` / `10.20.1.144`, status checks OK |
| CPU | AMD EPYC 7571, 2 vCPU; RAM 3844 MiB |
| Services | nginx, php8.3-fpm, redis-server, cron, CloudWatch agent, SSM agent — all active |
| Nextcloud | `status.php` 200, 34.0.4.1, maintenance false, DB connected |
| S3 mount `/Backup_data` | `files_external:verify 1` → status ok |
| Office | `proxy.php?req=/hosting/discovery` 200 (54 KB), capabilities 200, COOLWSD running |
| Cron | `cron.php` ran OK |
| DNS | Google 8.8.8.8 and office PC resolve `13.234.211.7`; HTTPS 200 from outside |
| Nextcloud log | no new errors after reboot |

Known/pre-existing: `occ richdocuments:activate-config` reports `/hosting/discovery 404` because `wopi_url` is the site root — same as recorded on 2026-08-25 (built-in CODE). Real Office endpoints return 200. Kernel line `piix4_smbus ... SMBus base address uninitialized` on AMD is harmless.

## 5. Not changed (by decision)

- S3 bucket, files, old object versions, lifecycle — **untouched** (production data; client decision).
- Nextcloud external storage "check for changes" — untouched (10 users upload daily).
- RDS instance, storage, KMS keys, AWS Backup plan, CloudTrail, budget.
- No smaller instance (memory peak too high), no Graviton (built-in CODE is x86), no stopping EC2 at night (24×7).

## 6. Savings (monthly, incl. 18% GST)

| Item | Before | After | Saving |
|---|---|---|---|
| EC2 compute | $32.70 (t3.medium on-demand) | $11.32 (t3a Savings Plan) | ~$25.2 |
| RDS instance | $15.33 | $12.41 (RI — **pending re-purchase**, payment failed) | ~$3.4 (not yet) |
| Aug manual snapshot | ~$0.3–0.8 | $0 | ~$0.3–0.8 |
| **Total** | | | **~$29–30 / month** |

Expected bill: **~$53–54/month** (under the $60 budget).

## 7. Commitments and follow-ups

- Savings Plan and RDS RI are **12-month commitments** (No Upfront → billed monthly, nothing paid in advance). Renew or let expire on **2027-11-02**.
- Savings Plan covers **t3a** family in Mumbai only. If the server type changes family, the plan stops applying.
- Do **not** release Elastic IP `13.234.211.7` (DNS + Office allowlist depend on it). An unattached EIP is also billed.
- Delete `snap-006094f30c8419f2a` after ~1 week of stable running.
- **RDS RI saraswathi-nextcloud-db-ri-1yr = payment-failed.** Partner/root must: pay all Unpaid/Past due AISPL invoices (Aug ₹900.39 if still open; Oct invoice 2899262217 = $83.34), confirm a valid default card with Auto-pay, then buy the RI again with a new ID (e.g. saraswathi-nextcloud-db-ri-1yr-b). Saving ~$3.45/mo is not active until then.
- Any external firewall / client allowlist using `3.111.213.217` must use `13.234.211.7`.

## 8. Rollback

1. Stop EC2 → change type back to `t3.medium` → start (≈1 min). The Savings Plan would then not apply.
2. If the disk is damaged: restore `snap-006094f30c8419f2a` to a **new** volume (never overwrite prod blindly).
3. Restore config from `/root/config.php.before-t3a-202611021254` if needed.
