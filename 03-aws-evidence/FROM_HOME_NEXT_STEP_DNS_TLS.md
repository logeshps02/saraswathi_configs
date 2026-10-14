# From Home — Next Step: DNS A record + TLS

Nextcloud is installed on HTTP only. Hostname will be `https://files.t-saraswathi.in`.

Sign in as `logesh.implementer`. Region for EC2: **Mumbai**. Route 53 is global.

Do **not** change nameservers.
Do **not** delete, transfer, or unlock the domain.
Do **not** create a second hosted zone.
Do **not** create an Elastic IP in this step (current public IPv4 is enough).
Do **not** run Certbot until the A record exists and this host sees that name.

## 1. Read the current public IPv4 (SSM)

```sh
TOKEN=`curl -s -X PUT http://169.254.169.254/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 60"` && curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4; echo
```

Reply with that IPv4 only.

Result (2026-08-25): `3.111.213.217` (auto-assigned; not an Elastic IP).

## 2. Create the A record (console)

1. Search `Route 53` → **Hosted zones**.
2. Open **t-saraswathi.in** only. Do not open another zone.
3. Confirm NS records are still the AWS name servers. Do not edit NS or SOA.
4. **Create record**.
5. Record name: `files` (full name must be `files.t-saraswathi.in`).
6. Type: **A**.
7. Value: the public IPv4 from step 1.
8. TTL: `300`.
9. Routing: Simple.
10. Do not create a CNAME for the same name.
11. **Create records**.

Result (2026-08-25): Route 53 change `C09702172G2CLD1D4TXOC` submitted 02:31 IST, status **PENDING**. Confirm the record is `files.t-saraswathi.in` type **A** value `3.111.213.217`. Do not edit NS/SOA.

## 3. Check DNS from the app host (SSM, after the record exists)

```sh
getent hosts files.t-saraswathi.in
```

Expected: the same public IPv4 as step 1. If empty, wait 1–2 minutes and run it again. Do not run Certbot until this matches.

Result (2026-08-25): `3.111.213.217   files.t-saraswathi.in`.

## 4. Install Certbot (SSM, after DNS matches)

```sh
sudo DEBIAN_FRONTEND=noninteractive apt install -y certbot python3-certbot-nginx
```

## 5. Issue the certificate (SSM)

This talks to Let's Encrypt on port 80. Do not paste any private key.

```sh
sudo certbot --nginx -d files.t-saraswathi.in --redirect --non-interactive --agree-tos --register-unsafely-without-email --key-type ecdsa
```

Expected: success and nginx reloaded. If it fails, paste the error only.

Result (2026-08-25): Certbot success. Certificate expires 2026-11-22. Auto-renew scheduled. Deployed to `/etc/nginx/sites-enabled/files.t-saraswathi.in`. Do not paste privkey.pem.

Then:

```sh
sudo nginx -t && sudo grep -n 'ssl_certificate\|return 301\|listen 443\|fastcgi_param HTTPS' /etc/nginx/sites-enabled/files.t-saraswathi.in
```

If Certbot left `fastcgi_param HTTPS off`, we will change that next. Do not edit blindly.

## 6. Point Nextcloud at HTTPS (SSM, after cert works)

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:set overwrite.cli.url --value=https://files.t-saraswathi.in && sudo -u www-data php /var/www/nextcloud/occ config:system:set overwriteprotocol --value=https
```

```sh
curl -sI https://files.t-saraswathi.in/status.php
```

```sh
curl -s https://files.t-saraswathi.in/status.php
```

Expected: HTTPS 200 and JSON `"installed":true`.

Result (2026-08-25): `nginx -t` ok (wasm warn only). `overwrite.cli.url=https://files.t-saraswathi.in`. `overwriteprotocol=https`. `https://files.t-saraswathi.in/status.php` = HTTP 200 JSON `"installed":true` version `34.0.3.2`. Secure cookies present.

## Stop

DNS + TLS step is complete. Do not change nameservers. Do not transfer the domain. Do not create EIP yet.
