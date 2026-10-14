# From Home — Phase 6 batch (do all three, one paste)

Trash + versions are **working** on `_restore-drill.txt`. Do not create users. Do not enable SMTP/HPB/NAT/EIP. Do not restore AWS snapshots.

Do **A then B then C**. One reply at the end.

## A. Activity (browser)

1. Still logged in as `saraswathi.admin`.
2. Open **Activity**.
3. Confirm events exist for `_restore-drill.txt` (created / deleted / restored / changed). Any of those is enough.

Paste: Activity shows drill events yes/no.

## B. admin_audit (Session Manager, one line)

```sh
sudo -u www-data php /var/www/nextcloud/occ app:list --enabled | grep -E 'admin_audit|activity|files_versions|files_trashbin' && echo --- && sudo -u www-data wc -l /var/www/nextcloud/data/audit.log /opt/nextcloud/data/audit.log 2>/dev/null; sudo -u www-data php /var/www/nextcloud/occ config:app:get admin_audit logfile; echo AUDIT_LOG_EXIT:$?
```

Need: four apps listed; logfile path or empty + exit code. Do **not** paste log contents.

## C. Leave the drill file

Leave `_restore-drill.txt` in Files. Do not empty Deleted files.

## Paste once

- A yes/no
- B four app names + logfile line/exit
- C left in Files yes/no

### Confirmed (2026-08-26)

| Item | Value |
|---|---|
| A Activity | **working** (drill events) |
| B apps | activity **7.0.0**, admin_audit **1.24.0**, files_trashbin **1.24.0**, files_versions **1.27.0** |
| B audit.log | `/opt/nextcloud/data/audit.log` **0** lines |
| B `admin_audit` logfile | unset (`AUDIT_LOG_EXIT:1`) — default (nextcloud.log). Do not set a custom path |
| C | leave `_restore-drill.txt` in Files |

## Stop

Phase 6 UI/audit batch is complete. Do not create users. Do not SMTP. Do not NAT/EIP. Do not dump audit log. Do not restore snapshots. Do not set `admin_audit` logfile.
