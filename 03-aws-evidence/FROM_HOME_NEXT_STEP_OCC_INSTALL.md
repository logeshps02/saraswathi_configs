# From Home — Next Step: CLI install (RDS + data dir)

HTTP Nginx + PHP-FPM already serve Nextcloud 34.0.3 (`installed:false`).
Use Session Manager. Paste one command at a time with Ctrl+V.

Do **not** open the browser wizard.
Do **not** put the RDS password or admin password in chat, in the command line as plain text, or in this file.
Do **not** paste `config/config.php`.
Do **not** add DNS or Certbot in this step.

## Values (no secrets)

| Item | Value |
|---|---|
| App dir | `/var/www/nextcloud` |
| Data dir | `/opt/nextcloud/data` |
| Database | mysql |
| DB host | `saraswathi-nextcloud-db.c5giuu4c6ye6.ap-south-1.rds.amazonaws.com` |
| DB port | 3306 |
| DB name | `nextcloud` |
| DB user | `ncadmin` (RDS master; password from password manager) |
| Nextcloud admin | `saraswathi.admin` (new app account; different from RDS) |
| Trusted domain later | `files.t-saraswathi.in` |

Create the Nextcloud admin password in the password manager before the install command. Do not reuse the RDS password.

## 1. Confirm occ is ready and still not installed

```bash
sudo -u www-data php /var/www/nextcloud/occ status
```

Expected: `installed: false` and version `34.0.3.2`. If already `true`, stop.

Result (2026-08-25): `installed: false`, version `34.0.3.2`.

## 2. Confirm data dir is outside the web root

```bash
test -d /opt/nextcloud/data && test ! -f /var/www/nextcloud/config/config.php && echo DATA_DIR_OK || echo DATA_DIR_OR_CONFIG_BAD
```

Expected: `DATA_DIR_OK`.

Result (2026-08-25): `DATA_DIR_OR_CONFIG_BAD`. Diagnose before install. Do not print `config.php`.

```bash
test -d /opt/nextcloud/data && echo DATA_DIR_EXISTS || echo DATA_DIR_MISSING
```

Result (2026-08-25): `DATA_DIR_EXISTS`.

```bash
if test -f /var/www/nextcloud/config/config.php; then echo CONFIG_PHP_EXISTS; else echo CONFIG_PHP_ABSENT; fi
```

Result (2026-08-25): `CONFIG_PHP_EXISTS` while `occ status` is still `installed: false`. Do not print the file.

```bash
ls /var/www/nextcloud/config
```

Result (2026-08-25): `CAN_INSTALL`, `config.php`, `config.sample.php`. `CAN_INSTALL` means CLI install is still allowed. Do not print `config.php`.

```bash
stat -c '%s %U:%G' /var/www/nextcloud/config/config.php
```

Result (2026-08-25): `0 www-data:www-data`. Empty leftover, not an installed instance. Remove only if still 0 bytes. Do not print file contents.

```bash
test "$(stat -c %s /var/www/nextcloud/config/config.php)" = 0 && sudo rm -f /var/www/nextcloud/config/config.php && echo EMPTY_CONFIG_REMOVED || echo CONFIG_NOT_EMPTY_STOP
```

Result (2026-08-25): `EMPTY_CONFIG_REMOVED`. Empty leftover only. `CAN_INSTALL` remains. Ready for password-safe CLI install.

## 3. Read the RDS password (hidden)

SSM is `sh` (not bash). Do **not** use `read -s` (illegal option). Type the **RDS `ncadmin`** password from the password manager. It will not show. Press Enter.

```sh
stty -echo; IFS= read -r NEXTCLOUD_DB_PASS; stty echo; printf '\n'; test -n "$NEXTCLOUD_DB_PASS" && echo DB_PASS_SET || echo DB_PASS_EMPTY
```

Reply `DB_PASS_SET` or `DB_PASS_EMPTY`. Never paste the password.

Result (2026-08-25): `read -s` failed (`sh: read: Illegal option -s`); `DB_PASS_EMPTY`. Retry with `stty -echo`.

Result (2026-08-25): `DB_PASS_SET`. Password is only in this SSM session. Never pasted.

## 4. Read the new Nextcloud admin password (hidden)

Type the **new** `saraswathi.admin` password from the password manager. It will not show. Press Enter. SSM is `sh` — do not use `read -s`.

```sh
stty -echo; IFS= read -r NEXTCLOUD_ADMIN_PASS; stty echo; printf '\n'; test -n "$NEXTCLOUD_ADMIN_PASS" && echo ADMIN_PASS_SET || echo ADMIN_PASS_EMPTY
```

Reply `ADMIN_PASS_SET` or `ADMIN_PASS_EMPTY`. Never paste the password.

Result (2026-08-25): `ADMIN_PASS_SET`. Password is only in this SSM session. Never pasted.

## 5. Run official CLI install

Run this only after both `DB_PASS_SET` and `ADMIN_PASS_SET`. It uses the variables already in this SSM session. Do not type passwords here.

```bash
cd /var/www/nextcloud && sudo -E -u www-data php occ maintenance:install --database mysql --database-name nextcloud --database-host saraswathi-nextcloud-db.c5giuu4c6ye6.ap-south-1.rds.amazonaws.com --database-port 3306 --database-user ncadmin --database-pass "$NEXTCLOUD_DB_PASS" --admin-user saraswathi.admin --admin-pass "$NEXTCLOUD_ADMIN_PASS" --data-dir /opt/nextcloud/data
```

Expected: `Nextcloud was successfully installed`.

Result (2026-08-25): `Nextcloud was successfully installed`. User then pressed Ctrl+C at the `$` prompt (harmless).

Then immediately:

```bash
unset NEXTCLOUD_DB_PASS NEXTCLOUD_ADMIN_PASS
```

Result (2026-08-25): `SECRETS_CLEARED`.

## 6. Confirm installed (no secrets)

```bash
sudo -u www-data php /var/www/nextcloud/occ status
```

Expected: `installed: true`, version `34.0.3.2`.

Result (2026-08-25): `installed: true`, version `34.0.3.2`, maintenance false.

```bash
curl -s -H 'Host: files.t-saraswathi.in' http://127.0.0.1/status.php
```

Expected JSON with `"installed":true`.

Result (2026-08-25): `{"error": "Trusted domain error.", "code": 15}` with Host `files.t-saraswathi.in`. Expected until trusted_domains is set.

Result after trusted_domains (2026-08-25): `status.php` JSON `"installed":true` version `34.0.3.2`. `datadirectory` = `/opt/nextcloud/data`. Remaining set/get lines were mashed by SSM paste; re-run labeled wrap-up.

Result (2026-08-25): second wrap-up paste also mashed. `trusted_domains` confirmed `files.t-saraswathi.in`. Region/timezone/cli.url not confirmed. Use one-line `&&` chain.

Result (2026-08-25): `default_phone_region=IN`, `default_timezone=Asia/Kolkata`, `overwrite.cli.url=http://files.t-saraswathi.in`. CLI install step complete. No TLS/DNS yet.

## 7. Trusted domain only (after install)

```bash
sudo -u www-data php /var/www/nextcloud/occ config:system:set trusted_domains 0 --value=files.t-saraswathi.in
```

Result (2026-08-25): `System config value trusted_domains => 0 set to string files.t-saraswathi.in`.

Do not dump `config.php`. Do not set HTTPS overwrite URL until TLS exists.

## Stop

CLI install step is complete after the wrap-up checks below. Never passwords. Never `config.php`.
