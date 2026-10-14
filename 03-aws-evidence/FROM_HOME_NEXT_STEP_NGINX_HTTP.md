# From Home — Next Step: HTTP-only Nginx for Nextcloud 34.0.3

Files are at `/var/www/nextcloud` (34.0.3.2). Data dir is `/opt/nextcloud/data`.
Use Session Manager. Paste one command at a time with Ctrl+V.

Do **not** run Certbot, add TLS, create DNS, or complete the install wizard.
Do **not** put the database password in chat.

This site is HTTP only. Official TLS redirect is added after a certificate exists.

## 1. Confirm the PHP-FPM socket

```bash
ss -lntp | grep php-fpm || true
```

```bash
test -S /run/php/php8.3-fpm.sock && echo FPM_SOCK_OK || echo FPM_SOCK_MISSING
```

Expected: `FPM_SOCK_OK`. If missing, stop.

Result (2026-08-25): `FPM_SOCK_OK`.

## 2. Write the site file

Paste this whole block once (it is one command). It writes `/etc/nginx/sites-available/files.t-saraswathi.in`.

```bash
sudo tee /etc/nginx/sites-available/files.t-saraswathi.in >/dev/null <<'EOF'
# Saraswathi Nextcloud HTTP-only site
# Based on official nginx-root.conf.sample (2026-06-09)
# TLS / HTTPS redirect is added later. Do not add ssl_* or return 301 https here yet.

upstream php-handler {
    server unix:/run/php/php8.3-fpm.sock;
}

map $arg_v $asset_immutable {
    "" "";
    default ", immutable";
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name files.t-saraswathi.in;
    server_tokens off;
    root /var/www/nextcloud;

    client_max_body_size 512M;
    client_body_timeout 300s;
    fastcgi_buffers 64 4K;
    client_body_buffer_size 512k;

    gzip on;
    gzip_vary on;
    gzip_comp_level 4;
    gzip_min_length 256;
    gzip_proxied expired no-cache no-store private no_last_modified no_etag auth;
    gzip_types application/atom+xml text/javascript application/javascript application/json application/ld+json application/manifest+json application/rss+xml application/vnd.geo+json application/vnd.ms-fontobject application/wasm application/x-font-ttf application/x-web-app-manifest+json application/xhtml+xml application/xml font/opentype image/bmp image/svg+xml image/x-icon text/cache-manifest text/css text/plain text/vcard text/vnd.rim.location.xloc text/vtt text/x-component text/x-cross-domain-policy;

    add_header Referrer-Policy "no-referrer" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Permitted-Cross-Domain-Policies "none" always;
    add_header X-Robots-Tag "noindex, nofollow" always;
    fastcgi_hide_header X-Powered-By;

    include mime.types;
    types {
        text/javascript mjs;
        application/wasm wasm;
    }

    index index.php index.html /index.php$request_uri;

    location = / {
        if ( $http_user_agent ~ ^DavClnt ) {
            return 302 /remote.php/webdav/$is_args$args;
        }
    }

    location = /robots.txt {
        allow all;
        log_not_found off;
        access_log off;
    }

    location ^~ /.well-known {
        location = /.well-known/carddav { return 301 /remote.php/dav/; }
        location = /.well-known/caldav  { return 301 /remote.php/dav/; }
        location /.well-known/acme-challenge    { try_files $uri $uri/ =404; }
        location /.well-known/pki-validation    { try_files $uri $uri/ =404; }
        return 301 /index.php$request_uri;
    }

    location ~ ^/(?:build|tests|config|lib|3rdparty|templates|data)(?:$|/)  { return 404; }
    location ~ ^/(?:\.|autotest|occ|issue|indie|db_|console)                { return 404; }
    location ~ ^/(?:composer\.(?:json|lock)|package(?:-lock)?\.json|core/shipped\.json)$ { return 404; }

    location ~ \.php(?:$|/) {
        rewrite ^/(?!index|remote|public|cron|status|ocs\/v[12]|ocs-provider\/.+|core\/ajax\/update|updater\/.+|.+\/richdocumentscode(_arm64)?\/proxy) /index.php$request_uri;
        fastcgi_split_path_info ^(.+?\.php)(/.*)$;
        set $path_info $fastcgi_path_info;
        try_files $fastcgi_script_name =404;
        include fastcgi_params;
        fastcgi_pass php-handler;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param PATH_INFO $path_info;
        fastcgi_param HTTPS off;
        fastcgi_param modHeadersAvailable true;
        fastcgi_param front_controller_active true;
        fastcgi_intercept_errors on;
        fastcgi_request_buffering on;
        fastcgi_max_temp_file_size 0;
    }

    location ~ \.(?:css|js|mjs|svg|gif|ico|jpg|png|webp|wasm|tflite|map|ogg|flac|mp4|webm)$ {
        try_files $uri /index.php$request_uri;
        add_header Cache-Control "public, max-age=15778463$asset_immutable";
        add_header Referrer-Policy "no-referrer" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Permitted-Cross-Domain-Policies "none" always;
        add_header X-Robots-Tag "noindex, nofollow" always;
        access_log off;
    }

    location ~ \.(otf|woff2?)$ {
        try_files $uri /index.php$request_uri;
        expires 7d;
        access_log off;
    }

    location /remote {
        return 301 /remote.php$request_uri;
    }

    location / {
        try_files $uri $uri/ /index.php$request_uri;
    }
}
EOF
```

You should return to a `$` prompt with no error.

Result (2026-08-25): tee returned to `$`. Paste showed SSM wrap `>` mid-line (including `root /> var/www/nextcloud`). Treat as unverified until `SITE_FILE_OK`.

## 2b. Verify the file is not wrap-corrupted

```bash
sudo grep -q 'root /var/www/nextcloud;' /etc/nginx/sites-available/files.t-saraswathi.in && sudo grep -q 'server unix:/run/php/php8.3-fpm.sock;' /etc/nginx/sites-available/files.t-saraswathi.in && sudo grep -q 'fastcgi_param HTTPS off;' /etc/nginx/sites-available/files.t-saraswathi.in && echo SITE_FILE_OK || echo SITE_FILE_BAD
```

Expected: `SITE_FILE_OK`. If `SITE_FILE_BAD`, do not enable the site.

Result (2026-08-25): `SITE_FILE_OK`.

## 3. Enable the site, disable Ubuntu default

```bash
sudo ln -sfn /etc/nginx/sites-available/files.t-saraswathi.in /etc/nginx/sites-enabled/files.t-saraswathi.in
```

Result (2026-08-25): `SITE_ENABLED` (command returned `$` twice; `-sfn` is idempotent).

```bash
sudo rm -f /etc/nginx/sites-enabled/default
```

Result (2026-08-25): `DEFAULT_REMOVED`.

```bash
sudo nginx -t
```

Expected: `syntax is ok` and `test is successful`. If not, stop and paste the error.

Result (2026-08-25): syntax ok, test successful. Harmless warn: duplicate extension `wasm` (Ubuntu mime.types already defines it).

```bash
sudo systemctl reload nginx
```

Result (2026-08-25): `NGINX_RELOADED`.

```bash
systemctl is-active nginx php8.3-fpm
```

Expected: `active` twice.

Result (2026-08-25): `active` / `active`.

## 4. Local HTTP check only

```bash
curl -sI -H 'Host: files.t-saraswathi.in' http://127.0.0.1/status.php
```

Result (2026-08-25): `HTTP/1.1 200 OK`, `Content-Type: application/json`. PHP-FPM is serving Nextcloud.

```bash
curl -s -H 'Host: files.t-saraswathi.in' http://127.0.0.1/status.php
```

Expected: HTTP 200 and JSON that includes `"installed":false` (or similar not-installed text). That is correct.

Do not open the public IP in a browser and do not click Install.

Result (2026-08-25):

```json
{"installed":false,"maintenance":false,"needsDbUpgrade":false,"version":"34.0.3.2","versionstring":"34.0.3","edition":"","productname":"Nextcloud","extendedSupport":false}
```

HTTP-only Nginx + PHP-FPM for Nextcloud 34.0.3 is complete. Do not run `occ maintenance:install` yet.

## Stop

This step is done. Next later (not now): CLI install against RDS and `/opt/nextcloud/data`, then DNS + TLS.
