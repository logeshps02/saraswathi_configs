# From Home — Next Step: PHP 8.3 FPM only

Redis is local-only. Pin PHP to **8.3** (Ubuntu 24.04 default; Nextcloud stable supports 8.3 and 8.4).
Do **not** install PHP 8.5, Apache, MariaDB server, Certbot, or Nextcloud.
Use Session Manager. Paste one command at a time with Ctrl+V.

## 1. Confirm Ubuntu will install 8.3

```bash
apt-cache policy php8.3-fpm | head -n 5
```

You should see a Candidate version starting with `8.3`.

## 2. Install PHP-FPM and Nextcloud modules

```bash
sudo DEBIAN_FRONTEND=noninteractive apt install -y php8.3-fpm php8.3-cli php8.3-curl php8.3-gd php8.3-mbstring php8.3-xml php8.3-zip php8.3-intl php8.3-bcmath php8.3-gmp php8.3-imagick php8.3-mysql php8.3-redis php8.3-apcu php8.3-opcache
```

## 3. Enable and check

```bash
sudo systemctl enable --now php8.3-fpm
```

```bash
php -v
```

```bash
systemctl is-active php8.3-fpm
```

Expected: PHP **8.3.x**, and `active`.

## 4. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| PHP CLI | 8.3.6 NTS |
| OPcache | Zend OPcache 8.3.6 |
| php8.3-fpm | enabled and active |
| Note | A stray `^M` / `: not found` after enable is harmless |

## 5. Confirm required modules

Paste one line:

```bash
php -m
```

Then paste:

```bash
php -m | grep -Ei 'ctype|curl|dom|fileinfo|gd|json|libxml|mbstring|openssl|posix|session|simplexml|xmlreader|xmlwriter|zip|zlib|pdo_mysql|intl|bcmath|gmp|imagick|redis|apcu|Zend OPcache'
```

## 6. Modules confirmed (2026-08-25)

Present: apcu, bcmath, ctype, curl, dom, fileinfo, gd, gmp, imagick, intl, json, libxml, mbstring, openssl, pdo_mysql, posix, redis, session, SimpleXML, xmlreader, xmlwriter, Zend OPcache, zip, zlib.

PHP step is done. Next: [FROM_HOME_NEXT_STEP_PHP_LIMITS.md](FROM_HOME_NEXT_STEP_PHP_LIMITS.md).
