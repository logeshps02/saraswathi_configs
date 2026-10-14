# From Home — Next Step: Redis cache + system cron

HTTPS is live at `https://files.t-saraswathi.in`. Redis already listens on localhost and answers `PONG`. PHP already has `redis` and `apcu` modules.

Use Session Manager. Paste each numbered block as **one line**. Do not paste multi-line scripts (SSM is `sh` and will mash them).

Do **not** paste `config/config.php`.
Do **not** set a Redis password in chat.
Do **not** bind Redis to `0.0.0.0`.
Do **not** open port 6379 in UFW or security groups.
Do **not** start S3, Collabora, users, NAT, or EIP in this step.

## Values (no secrets)

| Item | Value |
|---|---|
| App dir | `/var/www/nextcloud` |
| Redis | `127.0.0.1:6379` local only |
| Local cache | APCu |
| Distributed + locking | Redis |
| Cron | `www-data` every 5 minutes, `/usr/bin/php -f /var/www/nextcloud/cron.php` |

## 1. Confirm Redis, PHP modules, and installed instance

```sh
redis-cli ping && ss -ltn | grep 6379 && php -m | grep -Ei '^(redis|apcu)$' && sudo -u www-data php /var/www/nextcloud/occ status
```

Expected: `PONG`; listen `127.0.0.1:6379` and/or `[::1]:6379` only; both `redis` and `apcu`; `installed: true` version `34.0.3.2`.

If Redis is on `0.0.0.0:6379`, stop and tell me. Do not continue.

## 2. Enable APCu for CLI (needed by occ) and reload FPM

```sh
printf '%s\n' 'apc.enable_cli=1' | sudo tee /etc/php/8.3/mods-available/saraswathi-apcu-cli.ini && sudo phpenmod -v 8.3 -s ALL saraswathi-apcu-cli && sudo systemctl reload php8.3-fpm && php -r 'echo (extension_loaded("apcu") && ini_get("apc.enable_cli")) ? "APCU_CLI_OK\n" : "APCU_CLI_BAD\n";' && php -r 'echo extension_loaded("redis") ? "PHP_REDIS_OK\n" : "PHP_REDIS_BAD\n";'
```

Expected: `APCU_CLI_OK` and `PHP_REDIS_OK`.

## 3. Point Nextcloud at Redis + APCu

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:set redis host --value=127.0.0.1 && sudo -u www-data php /var/www/nextcloud/occ config:system:set redis port --value=6379 --type=integer && sudo -u www-data php /var/www/nextcloud/occ config:system:set redis timeout --value=0.0 --type=float && sudo -u www-data php /var/www/nextcloud/occ config:system:set memcache.local --value='\OC\Memcache\APCu' && sudo -u www-data php /var/www/nextcloud/occ config:system:set memcache.distributed --value='\OC\Memcache\Redis' && sudo -u www-data php /var/www/nextcloud/occ config:system:set memcache.locking --value='\OC\Memcache\Redis' && sudo -u www-data php /var/www/nextcloud/occ config:system:get memcache.local && sudo -u www-data php /var/www/nextcloud/occ config:system:get memcache.distributed && sudo -u www-data php /var/www/nextcloud/occ config:system:get memcache.locking && sudo -u www-data php /var/www/nextcloud/occ config:system:get redis host && sudo -u www-data php /var/www/nextcloud/occ config:system:get redis port
```

Expected printed values only:

- `\OC\Memcache\APCu`
- `\OC\Memcache\Redis`
- `\OC\Memcache\Redis`
- `127.0.0.1`
- `6379`

Do not dump the full config file.

## 4. Switch background jobs to system cron and install the crontab

```sh
sudo -u www-data php /var/www/nextcloud/occ background:cron && (sudo crontab -u www-data -l 2>/dev/null | grep -v '/var/www/nextcloud/cron.php'; echo '*/5 * * * * /usr/bin/php -f /var/www/nextcloud/cron.php') | sudo crontab -u www-data - && sudo crontab -u www-data -l && sudo -u www-data /usr/bin/php -f /var/www/nextcloud/cron.php && echo CRON_RUN_OK && sudo -u www-data php /var/www/nextcloud/occ config:app:get core backgroundjobs_mode
```

Expected: crontab line `*/5 * * * * /usr/bin/php -f /var/www/nextcloud/cron.php`; `CRON_RUN_OK`; mode `cron`.

## 5. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| Redis listen | 127.0.0.1:6379 and [::1]:6379 only |
| redis-cli | PONG |
| PHP modules | apcu, redis |
| occ status | installed true, 34.0.3.2, maintenance false |
| APCu CLI | APCU_CLI_OK (`apc.enable_cli=1`) |
| PHP Redis | PHP_REDIS_OK |
| memcache.local | `\OC\Memcache\APCu` |
| memcache.distributed | `\OC\Memcache\Redis` |
| memcache.locking | `\OC\Memcache\Redis` |
| redis host/port | 127.0.0.1 / 6379 |
| background jobs | cron |
| crontab www-data | `*/5 * * * * /usr/bin/php -f /var/www/nextcloud/cron.php` |
| first cron run | CRON_RUN_OK |

## Stop

Redis cache + system cron step is complete. Do not paste `config.php`. Do not open Redis to the network. Do not start S3, Collabora, users, NAT, or EIP yet.
