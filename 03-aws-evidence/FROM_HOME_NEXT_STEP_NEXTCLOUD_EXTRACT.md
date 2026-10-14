# From Home — Next Step: Extract Nextcloud 34.0.3

Tarball SHA256 is OK. Unpack the code and create a data directory outside the web root.
Use Session Manager. Paste one command at a time with Ctrl+V.

Do **not** run the install wizard, `occ maintenance:install`, Certbot, or Nginx site changes in this step.
Do **not** put the database password in chat.

Official layout:

| Path | Role |
|---|---|
| `/var/www/nextcloud` | Application (web root later) |
| `/opt/nextcloud/data` | Data directory outside the web root |

## 1. Confirm the web tree is empty

```bash
test ! -e /var/www/nextcloud && echo NC_PATH_FREE || echo NC_PATH_EXISTS
```

Expected: `NC_PATH_FREE`. If `NC_PATH_EXISTS`, stop and reply with that line.

## 2. Extract the verified tarball

```bash
sudo mkdir -p /var/www
```

Ubuntu 24.04 minimal images do not always include `bzip2`. First extract failed with `bzip2: Cannot exec`. Install it, then extract. Do not re-download the tarball.

```bash
sudo DEBIAN_FRONTEND=noninteractive apt install -y bzip2
```

```bash
bzip2 --version | head -n 1
```

```bash
sudo tar -xjf /tmp/nextcloud-34.0.3.tar.bz2 -C /var/www
```

Wait until the prompt returns. There must be no `Cannot exec` line.

## 3. Create the data directory and set ownership

```bash
sudo mkdir -p /opt/nextcloud/data
```

```bash
sudo chown -R www-data:www-data /var/www/nextcloud /opt/nextcloud
```

## 4. Confirm files and owner only

```bash
test -f /var/www/nextcloud/occ && test -f /var/www/nextcloud/version.php && echo NC_FILES_OK || echo NC_FILES_MISSING
```

```bash
stat -c '%U:%G %n' /var/www/nextcloud /opt/nextcloud/data
```

```bash
php -r 'require "/var/www/nextcloud/version.php"; echo implode(".", $OC_Version), "\n";'
```

Expected version: `34.0.3.x` (the fourth number is the internal build). Do not run `occ maintenance:install`.

## Stop

Reply with:
- `NC_PATH_FREE` or `NC_PATH_EXISTS`
- `NC_FILES_OK` or `NC_FILES_MISSING`
- the two `stat` lines (`www-data:www-data` expected)
- the version line

Do not open a browser installer. Next step after this is the Nginx PHP-FPM site for `files.t-saraswathi.in` (still HTTP-only until TLS).

## Result (2026-08-25)

| Check | Value |
|---|---|
| First extract | Failed: bzip2 missing |
| bzip2 | 1.0.8 |
| Retry extract | Success |
| Files | NC_FILES_OK |
| Owners | www-data:www-data on `/var/www/nextcloud` and `/opt/nextcloud/data` |
| Version | 34.0.3.2 |
