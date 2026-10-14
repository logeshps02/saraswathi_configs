# From Home — Next Step: admin_audit

Activity **7.0.0** is already enabled. SMTP stays off.

Next: enable **Auditing / Logging** (`admin_audit`) for admin and file actions in the Nextcloud log. Do **not** create extra users. Do **not** paste `config.php`, cookies, or log file contents.

Use Session Manager. One line each.

## 1. Enable

```sh
sudo -u www-data php /var/www/nextcloud/occ app:enable admin_audit && sudo -u www-data php /var/www/nextcloud/occ app:list --enabled | grep -Ei 'admin_audit'
```

Need `admin_audit` and a version.

## 2. Logfile setting (read only)

```sh
sudo -u www-data php /var/www/nextcloud/occ config:app:get admin_audit logfile; echo AUDIT_LOG_EXIT:$?
```

Empty / `AUDIT_LOG_EXIT:1` means audit lines go to the default Nextcloud log. Do **not** set a path. Do **not** `cat` the log.

### Confirmed (2026-08-26)

| Item | Value |
|---|---|
| admin_audit | **1.24.0** enabled |
| logfile | unset (`AUDIT_LOG_EXIT:1`) — default Nextcloud log |

## Stop

Do not paste log contents. Do not configure SMTP. Do not create users. CloudTrail S3 data events (files bucket only) is the next guide.
