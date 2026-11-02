# From Home — Next Step: Nextcloud Office (built-in CODE)

> **Update 2026-11-02 (cost optimisation):** Host is now **t3a.medium**; `wopi_allowlist` is now `127.0.0.1,::1,10.20.1.144,13.234.211.7`. Results below mentioning `3.111.213.217` are the original 2026-08-25 record. See [SESSION_2026-11-02_COST_OPTIMISATION.md](../10-change-log/SESSION_2026-11-02_COST_OPTIMISATION.md).

S3 IAM is proven. Nextcloud still uses local `/opt/nextcloud/data`.
This step enables **Nextcloud Office** (`richdocuments`) plus the **built-in CODE** app (`richdocumentscode`) on the same host.

Do **not** install Docker Collabora.
Do **not** create a second EC2, NAT, or EIP.
Do **not** paste `config.php`.
Do **not** create extra users.
Do **not** open port 22.

Use Session Manager. Paste each numbered block as **one line**. App download can take several minutes; wait for `$`.

## Values

| Item | Value |
|---|---|
| Hostname | `https://files.t-saraswathi.in` |
| Office app | `richdocuments` |
| Built-in CODE | `richdocumentscode` (x86_64; not `_arm64`) |
| Host | t3.medium, already running Nextcloud |

## 1. Memory and current Office apps

```sh
free -h && nproc && sudo -u www-data php /var/www/nextcloud/occ app:list | grep -Ei 'richdocuments|documentserver_community' || true
```

Expected: some free RAM (CODE needs extra). Apps likely not enabled yet.

If `Mem available` is under ~400 MiB, stop and tell me. Do not enable CODE.

## 2. Enable Nextcloud Office + built-in CODE

Downloads from the Nextcloud app store. Wait.

```sh
sudo -u www-data php /var/www/nextcloud/occ app:enable richdocuments && sudo -u www-data php /var/www/nextcloud/occ app:enable richdocumentscode && sudo -u www-data php /var/www/nextcloud/occ app:list --enabled | grep -Ei 'richdocuments'
```

Expected: both apps enabled. `richdocumentscode` listed (not `richdocumentscode_arm64`).

## 3. Point Office at this HTTPS host

Built-in CODE is proxied through Nextcloud. Same hostname. Local WOPI needs `allow_local_remote_servers`.

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:set allow_local_remote_servers --type=boolean --value=true && sudo -u www-data php /var/www/nextcloud/occ config:app:set richdocuments wopi_url --value=https://files.t-saraswathi.in && sudo -u www-data php /var/www/nextcloud/occ config:app:set richdocuments public_wopi_url --value=https://files.t-saraswathi.in && sudo -u www-data php /var/www/nextcloud/occ richdocuments:activate-config && sudo -u www-data php /var/www/nextcloud/occ config:app:get richdocuments wopi_url && sudo -u www-data php /var/www/nextcloud/occ config:app:get richdocuments public_wopi_url && sudo -u www-data php /var/www/nextcloud/occ config:system:get allow_local_remote_servers
```

Expected: activate-config success (or already active); both URLs `https://files.t-saraswathi.in`; `true`.

## 4. Confirm CODE proxy answers on HTTPS

```sh
curl -sI https://files.t-saraswathi.in/apps/richdocumentscode/proxy.php | head -n 5; echo ---; sudo -u www-data php /var/www/nextcloud/occ setupchecks 2>&1 | grep -Ei 'Office|Collabora|WOPI|richdocuments|HTTPS access|Memcache' || true
```

Expected: HTTP from the proxy (not nginx 404). Setupchecks may still be quiet about Office.

## 5. Partial result (2026-08-25)

| Item | Value |
|---|---|
| RAM | 3.7 GiB total, 3.1 GiB available |
| richdocuments | 11.1.0 enabled |
| richdocumentscode | 26.4.104 enabled |
| allow_local_remote_servers | true |
| First WOPI URL | `https://files.t-saraswathi.in` — **wrong for built-in CODE** |
| activate-config | Failed: `/hosting/discovery` 404 |
| proxy.php HEAD | 400 (expected without `req=`) |

Built-in CODE discovery is under `/apps/richdocumentscode/proxy.php?req=/hosting/discovery`, not `/hosting/discovery` on the Nextcloud root.

## 6. Fix WOPI to the CODE proxy (SSM)

```sh
sudo -u www-data php /var/www/nextcloud/occ config:app:set richdocuments wopi_url --value='https://files.t-saraswathi.in/apps/richdocumentscode/proxy.php' && sudo -u www-data php /var/www/nextcloud/occ config:app:set richdocuments public_wopi_url --value='https://files.t-saraswathi.in/apps/richdocumentscode/proxy.php' && sudo -u www-data php /var/www/nextcloud/occ config:app:set richdocuments wopi_allowlist --value='127.0.0.1,::1,10.20.1.144,3.111.213.217' && sudo -u www-data php /var/www/nextcloud/occ richdocuments:activate-config && sudo -u www-data php /var/www/nextcloud/occ config:app:get richdocuments wopi_url && sudo -u www-data php /var/www/nextcloud/occ config:app:get richdocuments public_wopi_url
```

Expected: activate-config **without** 404. URLs end with `/apps/richdocumentscode/proxy.php`.

## 7. Confirm discovery XML

```sh
curl -sI 'https://files.t-saraswathi.in/apps/richdocumentscode/proxy.php?req=/hosting/discovery' | head -n 8 && echo --- && curl -s 'https://files.t-saraswathi.in/apps/richdocumentscode/proxy.php?req=/hosting/discovery' | head -c 200; echo
```

Expected: HTTP 200 and XML starting with `wopi-discovery` (first 200 chars only). First call may take 30–60s while CODE starts.

Result (2026-08-25): `activate-config` still failed: it requested `proxy.php/hosting/discovery` (400). Direct `proxy.php?req=/hosting/discovery` returned **HTTP 200**, `text/xml`, `COOLWSD HTTP Server 26.04.1.4`, body starts with `<wopi-discovery>`. Custom `wopi_url` without `?req=` is wrong for built-in CODE. Clear those app values so Office uses the built-in server.

## 8. Use built-in CODE (clear custom WOPI URLs)

Do not set an external Collabora URL. Keep `allow_local_remote_servers` and `wopi_allowlist`.

```sh
sudo -u www-data php /var/www/nextcloud/occ config:app:delete richdocuments wopi_url && sudo -u www-data php /var/www/nextcloud/occ config:app:delete richdocuments public_wopi_url && echo WOPI_URLS_CLEARED && sudo -u www-data php /var/www/nextcloud/occ config:app:get richdocuments wopi_url; sudo -u www-data php /var/www/nextcloud/occ config:app:get richdocuments public_wopi_url; sudo -u www-data php /var/www/nextcloud/occ config:app:get richdocuments wopi_allowlist && sudo -u www-data php /var/www/nextcloud/occ config:system:get allow_local_remote_servers && curl -sI 'https://files.t-saraswathi.in/apps/richdocumentscode/proxy.php?req=/hosting/discovery' | head -n 5
```

Expected: `WOPI_URLS_CLEARED`; empty `wopi_url` / `public_wopi_url`; allowlist still the four addresses; `allow_local_remote_servers` true; discovery still HTTP 200.

Result (2026-08-25): custom `wopi_url` and `public_wopi_url` deleted. Allowlist `127.0.0.1,::1,10.20.1.144,3.111.213.217`. `allow_local_remote_servers=true`. Discovery still HTTP 200 XML 50411 bytes.

## 9. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| richdocuments | 11.1.0 enabled |
| richdocumentscode | 26.4.104 enabled (x86) |
| COOLWSD | 26.04.1.4 via proxy.php |
| Discovery | HTTP 200 `text/xml` `<wopi-discovery>` |
| Custom wopi_url | deleted (built-in CODE) |
| allow_local_remote_servers | true |
| wopi_allowlist | 127.0.0.1, ::1, 10.20.1.144, 3.111.213.217 |
| Docker / extra EC2 | not used |

Browser check later as `saraswathi.admin`: Files → + → New document. If public IP changes, update `wopi_allowlist`.

## Stop

Nextcloud Office (built-in CODE) step is complete. Do not install Docker Collabora. Do not paste `config.php`. Do not start Talk HPB, extra users, NAT, or EIP yet.
