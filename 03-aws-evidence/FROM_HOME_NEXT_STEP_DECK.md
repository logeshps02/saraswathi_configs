# From Home — Next Step: Deck

Calendar, Contacts, and Tasks are enabled. Enable **Deck** on the same host.

Use Session Manager. Paste each numbered block as **one line**.

Do **not** paste `config.php`.
Do **not** create extra users.
Do **not** install Docker, NAT, EIP, Talk HPB, or LibreSign in this step.

## Values

| Item | Value |
|---|---|
| App | `deck` |
| Sample board | after the app is enabled; admin-only for now |
| Sharing by group | later, when users exist |

## 1. Enable Deck

App-store download. Wait for `$`.

```sh
sudo -u www-data php /var/www/nextcloud/occ app:enable deck && sudo -u www-data php /var/www/nextcloud/occ app:list --enabled | grep -Ei '^  - deck:'
```

Expected: `deck` enabled with a version.

## 2. Confirm Deck API / occ surface (no extra users)

```sh
sudo -u www-data php /var/www/nextcloud/occ list 2>/dev/null | grep -Ei '^ *deck' || echo NO_DECK_OCC; curl -sI https://files.t-saraswathi.in/apps/deck/ | head -n 8
```

Expected: some `deck:` occ commands **or** `NO_DECK_OCC` (either is OK). HTTPS to `/apps/deck/` should not be nginx 404 (login redirect 302/303 or 200 is OK).

## 3. Optional: list boards for admin (if occ exists)

If step 2 showed `deck:` commands, run:

```sh
sudo -u www-data php /var/www/nextcloud/occ deck:board:list saraswathi.admin 2>/dev/null || sudo -u www-data php /var/www/nextcloud/occ deck:list-boards 2>/dev/null || echo DECK_LIST_SKIP
```

Empty boards is OK. Do not create staff users. A first board can wait for browser login as `saraswathi.admin`.

## 4. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| deck | 1.18.3 enabled |
| occ | `deck:calendar-toggle`, `deck:export`, `deck:import`, `deck:transfer-ownership` (no board-list command) |
| HTTPS `/apps/deck/` | 401 JSON without login (app is present; not nginx 404) |
| Boards | none yet (`DECK_LIST_SKIP`) |

Do not paste `Set-Cookie` values from curl.

## Stop

Deck app enable is complete. First board later in the browser as `saraswathi.admin`. Do not create extra users yet.
