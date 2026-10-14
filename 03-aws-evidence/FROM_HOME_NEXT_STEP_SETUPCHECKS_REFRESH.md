# From Home — Next Step: occ status + setupchecks refresh

Phase 6 AWS/app safety nets are live (alarms OK, backup vault + recovery point, versions/trash, S3 versioning, activity, admin_audit, CloudTrail data events + validation digest). Extra users and SMTP stay deferred.

Next: one Session Manager health refresh. Do **not** paste `config.php`. Do **not** paste certificates or passwords. Do **not** create users, NAT, EIP, or SMTP.

Sign in as `logesh.implementer`. Region: **Asia Pacific (Mumbai) / ap-south-1**.

## 1. Session Manager one-liner

EC2 → `i-002509b77963fd5fc` → Connect → Session Manager.

Paste as **one line**:

```sh
systemctl is-active nginx php8.3-fpm redis-server fail2ban && echo --- && sudo -u www-data php /var/www/nextcloud/occ status && echo --- && sudo -u www-data php /var/www/nextcloud/occ config:app:get core backgroundjobs_mode && echo --- && curl -sI https://files.t-saraswathi.in/status.php | head -n 1 && echo --- && sudo -u www-data php /var/www/nextcloud/occ setupchecks
```

## 2. Paste back

- four services active
- occ status (installed / version / maintenance)
- backgroundjobs_mode
- HTTPS status line
- full `setupchecks` output (redact any secret if one appears)

Do not try to fix every warning. Email / Talk HPB / AppAPI are expected later.

### Confirmed (2026-08-26)

| Item | Value |
|---|---|
| nginx / php8.3-fpm / redis-server / fail2ban | all **active** |
| occ status | installed true, **34.0.3.2**, maintenance false, needsDbUpgrade false |
| background jobs | **cron** (last run 4 minutes ago, no errors) |
| HTTPS status.php | HTTP/1.1 **200 OK** |
| PHP | 8.3.6; memory 512 MB |
| RDS | MySQL 8.4.9; 4-byte unicode; read committed |
| Code integrity | no altered files |
| Memcache / HSTS headers / WebDAV / data dir | pass |
| Maintenance window | 18:00–00:00 UTC |
| Mimetype migrations | none |
| LibreSign tools | Java 21.0.8 / JSignPdf 2.3.0 / PDFtk 3.3.3 / Poppler 24.02.0 |

**Expected later (do not treat as blockers):** AppAPI daemon; brute-force / Forwarded-for remote address; 2FA not enforced; email SMTP; overwrite CLI suggested localhost (keep current URL); config server ID; Imagick SVG; Talk HPB; Talk Client Push.

**Note:** `Errors in the log: 8` since 2026-08-19 — classify next (redacted). Time Manager guest 500 is already known.

## Stop

Do not paste `config.php`. Do not enable SMTP, users, NAT, or EIP from this output. Log-error classify is the next guide.
