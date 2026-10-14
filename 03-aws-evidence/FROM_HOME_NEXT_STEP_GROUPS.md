# From Home — Next Step: Nextcloud groups (no extra users)

Deck 1.18.3 is enabled. Create the approved **groups only**. Do **not** create staff users in this step.

Use Session Manager. Paste each numbered block as **one line**.

Do **not** paste `config.php`.
Do **not** paste cookies.
Do **not** set passwords here.

## Values

| Group | Purpose |
|---|---|
| Firm-Admins | Firm administrators |
| Firm-Partners | Partners |
| Firm-Seniors | Seniors |
| Firm-Juniors | Juniors |
| Firm-Trainees | Trainees |
| Firm-Departed | Disabled/departed (empty) |

`saraswathi.admin` is added only to `Firm-Admins`. No other users.

## 1. Create the six groups

```sh
sudo -u www-data php /var/www/nextcloud/occ group:add Firm-Admins && sudo -u www-data php /var/www/nextcloud/occ group:add Firm-Partners && sudo -u www-data php /var/www/nextcloud/occ group:add Firm-Seniors && sudo -u www-data php /var/www/nextcloud/occ group:add Firm-Juniors && sudo -u www-data php /var/www/nextcloud/occ group:add Firm-Trainees && sudo -u www-data php /var/www/nextcloud/occ group:add Firm-Departed && sudo -u www-data php /var/www/nextcloud/occ group:list
```

Expected: all six names listed. If a group already exists, paste the error and continue listing.

## 2. Put the existing admin in Firm-Admins only

```sh
sudo -u www-data php /var/www/nextcloud/occ group:adduser Firm-Admins saraswathi.admin && sudo -u www-data php /var/www/nextcloud/occ group:list-members Firm-Admins && sudo -u www-data php /var/www/nextcloud/occ user:info saraswathi.admin
```

Expected: `saraswathi.admin` in `Firm-Admins`. Other groups stay empty. Do not create new users.

Result (2026-08-25): all six groups created. Built-in `admin` already contains `saraswathi.admin`. `group:adduser Firm-Admins saraswathi.admin` succeeded. `group:list-members` is **not** a command on 34.0.3; use `group:info` / `group:list`.

## 3. Confirm membership (SSM)

```sh
sudo -u www-data php /var/www/nextcloud/occ group:list && sudo -u www-data php /var/www/nextcloud/occ group:info Firm-Admins && sudo -u www-data php /var/www/nextcloud/occ user:info saraswathi.admin
```

Expected: Firm-Admins lists `saraswathi.admin`; other Firm-* groups empty; user info shows groups `admin` and `Firm-Admins`.

## 4. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| Groups | Firm-Admins, Firm-Partners, Firm-Seniors, Firm-Juniors, Firm-Trainees, Firm-Departed |
| Firm-Admins members | saraswathi.admin |
| Other Firm-* | empty |
| Built-in admin group | saraswathi.admin |
| user enabled | true |
| cloud_id | saraswathi.admin@files.t-saraswathi.in |
| user_directory | /opt/nextcloud/data/saraswathi.admin |
| Extra users | none |

## Stop

Groups step is complete. Do not create staff accounts yet.
