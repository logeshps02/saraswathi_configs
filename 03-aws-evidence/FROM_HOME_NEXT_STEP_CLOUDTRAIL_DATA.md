# From Home — Next Step: CloudTrail S3 data events (files bucket only)

`admin_audit` **1.24.0** is enabled. Logfile unset = default Nextcloud log. Do **not** paste logs.

Next: add **S3 data events** on the files bucket to the **existing** trail. Management events already log. Data events cost extra — **one bucket only**.

Sign in as `logesh.implementer`. Region: **Asia Pacific (Mumbai) / ap-south-1**.

## Values

| Item | Value |
|---|---|
| Trail | `Saraswathi-management-trail` (existing; do not create a second trail) |
| Data resource | S3 bucket `saraswathi-nextcloud-files-055855670388` |
| API | Read and Write |
| Insights | **Off** |

Do **not** select all S3 buckets. Do **not** add Lambda, DynamoDB, or S3 Express. Do **not** log the CloudTrail log bucket.

## 1. Edit the existing trail

1. Search **CloudTrail** → **Trails**.
2. Open **`Saraswathi-management-trail`** only. Status must stay **Logging**.
3. **Event types** (or **Edit** near Data events).
4. Enable **Data events**.
5. Data event type: **S3**.
6. Browse / specify bucket: `saraswathi-nextcloud-files-055855670388` (current and future objects in that bucket).
7. Read **and** Write.
8. Do not tick “Log all S3 buckets”.
9. Insights: leave **off**.
10. Save.

### Basic selectors (2026-08-26 console)

If the page says **Basic event selectors** (not Advanced):

1. Do **not** tick **All current and future S3 buckets** Read/Write.
2. Use **Individual bucket selection**.
3. **Browse** → pick only `saraswathi-nextcloud-files-055855670388`.
4. Tick **Read** and **Write** on that bucket row.
5. Do **not** Add data event type. Do not add the CloudTrail logs bucket.
6. **Save changes**.

Leave Advanced unused if basic + one bucket works.

## 2. Paste back

- Trail still **Logging**
- Data events: S3 **yes/no**
- Bucket name (files bucket only)
- Insights off yes/no

Do not paste the trail S3 log bucket policy. Do not disable management events.

### Observed (2026-08-26) — fix all-buckets

| Item | Value |
|---|---|
| Trail | `Saraswathi-management-trail` **Logging** (multi-region) |
| Management events | All (Read/Write) |
| Insights | Off |
| Data events | S3 **(2)** — too many |
| Row 1 | **All current and future S3 buckets** — **remove** (cost) |
| Row 2 | `saraswathi-nextcloud-files-055855670388` Read+Write **Enabled** — keep |

## 3. Remove all-buckets only

1. Trail → Data events → **Edit**.
2. Uncheck / remove **All current and future S3 buckets**.
3. Keep **only** `saraswathi-nextcloud-files-055855670388` Read and Write.
4. Do not Stop logging. Do not add Insights. Do not add the CloudTrail logs bucket.
5. **Save changes**.
6. Paste: Data events S3 count **1**, files bucket only, Logging yes.

Recheck 2026-08-26 19:44 IST: still **S3 (2)** with All current and future S3 buckets. Not fixed yet.

On **Edit** data events (basic):

1. **All current and future S3 buckets** — clear **Read** and clear **Write** (both empty).
2. Individual row `saraswathi-nextcloud-files-055855670388` — **Read** and **Write** stay ticked.
3. Save. Detail page must say **Data events : S3 (1)** and must **not** list All current and future S3 buckets.

### Accepted (2026-08-26)

Basic selectors always show an **All current and future S3 buckets** line. That is OK if Read/Write are **not Enabled**. `S3 (2)` can still appear (two table rows). Only the files bucket collects data events.

| Row | Need |
|---|---|
| All current and future S3 buckets | Read/Write **blank** |
| `saraswathi-nextcloud-files-055855670388` | Read **Enabled**, Write **Enabled** |
| Insights | Off |
| Trail | Logging |

## Stop

Do not create a second trail. Do not enable Insights. Do not add data events on the CloudTrail logs bucket. Do not fill the files bucket. Log file validation on this trail is the next guide.

## Superseded 2026-09-12 — data events OFF

After rclone ingest, S3 data events were **removed** to cut cost. Trail stays **Logging**; management events stay **All**.

Observed on trail detail: **Data event collection is not configured for this trail.**

Do **not** follow the enable clicks above unless a later written change says so. Disable/confirm: [FROM_HOME_CLOUDTRAIL_DATA_EVENTS_OFF.md](FROM_HOME_CLOUDTRAIL_DATA_EVENTS_OFF.md). If Edit trail shows Event type = Data events only, **Cancel** (Save would turn them back on).
