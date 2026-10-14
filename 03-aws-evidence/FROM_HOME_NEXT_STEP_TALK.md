# From Home — Next Step: Talk confirm (no HPB)

Time Manager 0.3.25 is enabled. Guest HEAD 500 is a null `$userId` TypeError in `PageController.php` line 135 — keep the app. Do not patch vendor PHP.

Next quotation extra: **Talk**. Built-in app id is `spreed`. Confirm it is enabled. **Do not** install a high-performance backend / signaling server.

Use Session Manager. Paste each numbered block as **one line**.

Do **not** paste `config.php`.
Do **not** paste Set-Cookie.
Do **not** create extra users.
Do **not** open extra UDP/TCP ports.
Do **not** install Docker or a second EC2.

## 1. Confirm Talk is enabled

```sh
sudo -u www-data php /var/www/nextcloud/occ app:list --enabled | grep -Ei 'spreed|talk'
```

If `spreed` is not enabled:

```sh
sudo -u www-data php /var/www/nextcloud/occ app:enable spreed && sudo -u www-data php /var/www/nextcloud/occ app:list --enabled | grep -Ei 'spreed|talk'
```

## 2. HTTPS surface (no cookies)

```sh
curl -sI https://files.t-saraswathi.in/apps/spreed/ | head -n 6
```

Need not nginx 404. 401/302/303 is OK. Do not paste Set-Cookie.

## 3. Signaling still local (no HPB)

```sh
sudo -u www-data php /var/www/nextcloud/occ config:app:get spreed signaling_servers; echo SIG_EXIT:$?
```

Empty / not set is OK. Do not set a signaling URL.

## 4. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| spreed | **24.0.4** already enabled |
| `/apps/spreed/` anonymous | HTTP **303** See Other (present; not 404) |
| `signaling_servers` | not set (`SIG_EXIT:1`) — no HPB |
| status.php | HTTP 200 JSON |
| `migrations:status` | not a Nextcloud 34 occ command (ignore) |

## Stop

Do not install Talk HPB. Do not create chat rooms yet. Do not create extra users.
