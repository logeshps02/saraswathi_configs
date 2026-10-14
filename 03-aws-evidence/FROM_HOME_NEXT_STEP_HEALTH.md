# From Home — Next Step: Health / setup checks

Redis cache and system cron are in place. HTTPS is `https://files.t-saraswathi.in`.

Use Session Manager. Paste each numbered block as **one line**.

Do **not** paste `config/config.php`.
Do **not** paste certificates or passwords.
Do **not** start S3, Collabora, users, NAT, or EIP in this step.

Expected: some warnings are normal (mail not configured, S3/office apps not enabled yet). Paste the full outputs. Do not try to “fix everything” until we classify them.

## 1. Services, occ status, HTTPS, cache, cron

```sh
systemctl is-active nginx php8.3-fpm redis-server fail2ban && systemctl --failed --no-legend; echo ---; sudo -u www-data php /var/www/nextcloud/occ status && echo --- && sudo -u www-data php /var/www/nextcloud/occ config:system:get overwrite.cli.url && sudo -u www-data php /var/www/nextcloud/occ config:system:get overwriteprotocol && sudo -u www-data php /var/www/nextcloud/occ config:system:get memcache.local && sudo -u www-data php /var/www/nextcloud/occ config:system:get memcache.distributed && sudo -u www-data php /var/www/nextcloud/occ config:system:get memcache.locking && sudo -u www-data php /var/www/nextcloud/occ config:app:get core backgroundjobs_mode && echo --- && curl -sI https://files.t-saraswathi.in/status.php | head -n 1 && curl -s https://files.t-saraswathi.in/status.php
```

Expected: four `active`; no failed units (or empty); `installed: true` `34.0.3.2`; URL `https://files.t-saraswathi.in`; protocol `https`; APCu + Redis + Redis; jobs `cron`; HTTPS `200` JSON `"installed":true`.

## 2. Official setup checks (warnings expected)

```sh
sudo -u www-data php /var/www/nextcloud/occ setupchecks
```

Paste the full output. Do not paste any secret if one appears; redact it.

## 3. Enabled apps only (names, no config)

```sh
sudo -u www-data php /var/www/nextcloud/occ app:list --enabled
```

## 4. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| nginx / php8.3-fpm / redis-server / fail2ban | all active; no failed units |
| occ status | installed true, 34.0.3.2, maintenance false |
| overwrite.cli.url | https://files.t-saraswathi.in |
| overwriteprotocol | https |
| memcache | APCu local; Redis distributed + locking |
| background jobs | cron (last run 4 minutes ago, no errors) |
| HTTPS status.php | 200 JSON installed true |
| PHP | 8.3.6, memory 512 MB |
| RDS | MySQL 8.4.9, 4-byte unicode, read committed |
| Code integrity | no altered files |
| WebDAV / .well-known / data dir protected | pass |

### Classification

**Fix soon (small, no new products):**

- HSTS header missing (`Strict-Transport-Security` ≥ 15552000)
- Maintenance window not set
- Mimetype migrations pending (`occ maintenance:repair --include-expensive`)
- 3 errors in logs since 2026-08-18 (review, do not dump secrets)

**Expected later / do not treat as blockers now:**

- Email not configured
- AppAPI deploy daemon not set
- Talk High-performance backend missing (`spreed` is enabled by default)
- Client Push not installed
- Brute-force / Forwarded-for: remote address not determined (no reverse proxy yet)
- 2FA available but not enforced
- Imagick SVG support
- Configuration server ID (single host; optional)
- Suggested overwrite URL `https://localhost` is a false CLI hint; keep `https://files.t-saraswathi.in`

**Enabled apps:** default Hub set including `spreed` 24.0.4. No Collabora / calendar / contacts / S3 yet.

## Stop

Health pass is complete. Do not paste `config.php`. Do not enable S3, Collabora, users, NAT, or EIP from this output.
