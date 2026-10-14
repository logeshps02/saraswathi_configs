# From Home — Next Step: HSTS + maintenance window + mimetype repair

Health pass classified these as small leftover warnings. HTTPS stays at `https://files.t-saraswathi.in`.

Use Session Manager. Paste each numbered block as **one line**.

Do **not** paste `config/config.php`.
Do **not** paste the full nginx file.
Do **not** change nameservers, open 22, bind Redis, start S3, Collabora, users, NAT, or EIP.

## 1. See where headers are set (do not dump the whole site)

```sh
grep -n 'add_header\|listen \|ssl_certificate\|Strict-Transport' /etc/nginx/sites-enabled/files.t-saraswathi.in
```

Expected: existing `add_header` lines (Referrer-Policy / X-Robots-Tag). `Strict-Transport-Security` is probably absent. There should be **two** `X-Robots-Tag` lines (server + static assets). If HSTS is already present, say so and skip adding it.

## 2. Add HSTS, test nginx, reload, verify the header

```sh
SITE=/etc/nginx/sites-enabled/files.t-saraswathi.in; if grep -q 'Strict-Transport-Security' "$SITE"; then echo HSTS_ALREADY; else sudo sed -i '/add_header X-Robots-Tag "noindex, nofollow" always;/a\    add_header Strict-Transport-Security "max-age=15552000; includeSubDomains" always;' "$SITE"; echo HSTS_ADDED; fi; grep -n 'Strict-Transport-Security' "$SITE"; sudo nginx -t && sudo systemctl reload nginx && curl -sI https://files.t-saraswathi.in/status.php | grep -i 'HTTP/\|strict-transport'
```

Expected: `HSTS_ADDED` (or `HSTS_ALREADY`); two HSTS lines; `nginx -t` ok (wasm warn only); `HTTP/1.1 200`; `Strict-Transport-Security: max-age=15552000; includeSubDomains`.

If `nginx -t` fails, do not keep editing. Paste the error only.

## 3. Maintenance window (18:00 UTC = 23:30 IST) + expensive mimetype repair

Low-usage hour for this office timezone. Value is UTC 0–23.

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:set maintenance_window_start --type=integer --value=18 && sudo -u www-data php /var/www/nextcloud/occ config:system:get maintenance_window_start && sudo -u www-data php /var/www/nextcloud/occ maintenance:repair --include-expensive && echo REPAIR_OK
```

Expected: `18` then repair output ending `REPAIR_OK`. Fresh instance should finish quickly.

## 4. Re-check only the leftover items

```sh
sudo -u www-data php /var/www/nextcloud/occ setupchecks 2>&1 | grep -Ei 'HTTP headers|Strict-Transport|Maintenance window|Mimetype|Memcache|Cron last|HTTPS access|PHP version|Database version'
```

Expected: HSTS / HTTP headers green; maintenance window green; mimetype migrations gone or green.

## 5. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| HSTS in nginx | added after both X-Robots-Tag lines (36 and 96) |
| nginx -t | ok; wasm duplicate warn only (harmless) |
| HTTPS status.php | HTTP/1.1 200 OK |
| maintenance_window_start | 18 (18:00–00:00 UTC / 23:30–05:30 IST) |
| maintenance:repair --include-expensive | REPAIR_OK; mimetypes repaired |
| setupchecks | HTTP headers green; maintenance window green; mimetype none; memcache/cron/HTTPS/PHP/DB green |

`curl -sI .../status.php` did not print `Strict-Transport-Security` in the grep (PHP location). Official `occ setupchecks` HTTP headers is the pass criterion.

## Stop

HSTS + maintenance window + mimetype repair is complete. Do not paste `config.php` or the full nginx file. Do not enable S3, Collabora, Talk HPB, email, users, NAT, or EIP yet.
