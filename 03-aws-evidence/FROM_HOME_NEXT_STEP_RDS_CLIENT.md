# From Home — Next Step: MySQL client to private RDS

PHP limits are set. Test that the app host can reach `saraswathi-nextcloud-db`.
Use Session Manager. Paste one command at a time with Ctrl+V.

Do **not** type the database password in this file or in chat.
Do **not** put the password on the command line (no `-pPASSWORD`).
Do **not** install Nextcloud in this step.

## 1. Install the client only

```bash
sudo DEBIAN_FRONTEND=noninteractive apt install -y mysql-client
```

## 2. Confirm timezone was not cut off

```bash
php -r 'echo ini_get("date.timezone"), "\n";'
```

Expected: `Asia/Kolkata`

## 3. Test TCP to RDS (no password)

```bash
getent hosts saraswathi-nextcloud-db.c5giuu4c6ye6.ap-south-1.rds.amazonaws.com
```

```bash
timeout 8 bash -c 'echo >/dev/tcp/saraswathi-nextcloud-db.c5giuu4c6ye6.ap-south-1.rds.amazonaws.com/3306' && echo RDS_PORT_OPEN || echo RDS_PORT_FAIL
```

Expected: a private IP (10.20.21.x or 10.20.22.x) and `RDS_PORT_OPEN`.

## 4. Login test (password prompt only)

When this asks `Enter password:`, type the password from the password manager. It will not show on screen. Then press Enter.

```bash
mysql --host=saraswathi-nextcloud-db.c5giuu4c6ye6.ap-south-1.rds.amazonaws.com --port=3306 --user=ncadmin --password --database=nextcloud -e 'SELECT VERSION();'
```

Expected: a MySQL 8.4.x version number. If it fails, copy the error text only, never the password.

## Result (2026-08-25)

| Check | Value |
|---|---|
| date.timezone | Asia/Kolkata |
| mysql-client | 8.0.46-0ubuntu0.24.04.3 |
| RDS private IP | 10.20.22.41 (db-b) |
| TCP 3306 | RDS_PORT_OPEN |
| MySQL VERSION() | 8.4.9 |
| Password in paste | No |

Private RDS from `saraswathi-nextcloud-app` is proven. Do not open RDS publicly.
