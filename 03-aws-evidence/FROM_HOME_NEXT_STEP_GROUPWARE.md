# From Home — Next Step: Calendar, Contacts, Tasks

Office (built-in CODE) is live. Enable Nextcloud groupware apps on the same host.

Use Session Manager. Paste each numbered block as **one line**.

Do **not** paste `config.php`.
Do **not** create extra users.
Do **not** install Docker, NAT, EIP, or Talk HPB in this step.

## Values

| Item | Value |
|---|---|
| Apps | `calendar`, `contacts`, `tasks` |
| Timezone already | Asia/Kolkata |
| CalDAV / CardDAV | `https://files.t-saraswathi.in/.well-known/caldav` and `.../carddav` |
| Shared calendar later | after users exist |

## 1. Enable the three apps

Downloads from the app store. Wait for `$`.

```sh
sudo -u www-data php /var/www/nextcloud/occ app:enable calendar && sudo -u www-data php /var/www/nextcloud/occ app:enable contacts && sudo -u www-data php /var/www/nextcloud/occ app:enable tasks && sudo -u www-data php /var/www/nextcloud/occ app:list --enabled | grep -Ei 'calendar|contacts|tasks'
```

Expected: all three enabled with version numbers.

## 2. Confirm CalDAV / CardDAV redirects

```sh
curl -sI https://files.t-saraswathi.in/.well-known/caldav | head -n 12; echo ---; curl -sI https://files.t-saraswathi.in/.well-known/carddav | head -n 12
```

Expected: HTTP 301 (or 302) to `/remote.php/dav/` on both. Not 404.

## 3. Default calendar for the admin (no extra users)

```sh
sudo -u www-data php /var/www/nextcloud/occ dav:list-calendars saraswathi.admin && sudo -u www-data php /var/www/nextcloud/occ dav:list-addressbooks saraswathi.admin
```

Expected: at least one personal calendar and one address book for `saraswathi.admin`. If a command is unknown, paste the error only.

## 4. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| calendar | 6.5.4 enabled |
| contacts | 8.7.6 enabled (`contactsinteraction` 1.15.0 already present) |
| tasks | 0.18.1 enabled |
| CalDAV `/.well-known/caldav` | HTTP 301 → `https://files.t-saraswathi.in/remote.php/dav/` |
| CardDAV `/.well-known/carddav` | HTTP 301 → `https://files.t-saraswathi.in/remote.php/dav/` |
| Admin calendar | URI `personal`, display **Personal**, owner `saraswathi.admin`, writable |
| Admin address book | URI `contacts`, display **Contacts**, owner `saraswathi.admin`, writable |

## Stop

Calendar, Contacts, Tasks step is complete. Do not create extra users or a firm-wide shared calendar yet. Do not start Talk HPB, Deck, NAT, or EIP.
