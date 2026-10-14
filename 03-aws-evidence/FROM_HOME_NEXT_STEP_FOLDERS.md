# From Home — Next Step: Firm folder tree (admin only)

Groups exist. Create the runbook folder tree in `saraswathi.admin` files. Do **not** create extra users. Do **not** share folders to groups yet.

Use Session Manager. Paste each numbered block as **one line**.

Do **not** paste `config.php`.
Do **not** put client files here.

## Tree

```text
Firm/
  Partners/
  Administration/
  Clients/
  Statutory/
  Templates/
  Trainee-Workspace/
  Archive/
```

Owner: `saraswathi.admin` → `/opt/nextcloud/data/saraswathi.admin/files/Firm/...`

## 1. Create directories and scan

```sh
sudo -u www-data mkdir -p /opt/nextcloud/data/saraswathi.admin/files/Firm/Partners /opt/nextcloud/data/saraswathi.admin/files/Firm/Administration /opt/nextcloud/data/saraswathi.admin/files/Firm/Clients /opt/nextcloud/data/saraswathi.admin/files/Firm/Statutory /opt/nextcloud/data/saraswathi.admin/files/Firm/Templates /opt/nextcloud/data/saraswathi.admin/files/Firm/Trainee-Workspace /opt/nextcloud/data/saraswathi.admin/files/Firm/Archive && sudo -u www-data php /var/www/nextcloud/occ files:scan --path='/saraswathi.admin/files/Firm' && find /opt/nextcloud/data/saraswathi.admin/files/Firm -type d | sort
```

Expected: scan OK for that path; eight directories listed (`Firm` plus seven children).

## 2. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| files:scan Firm | Folders 8, Files 0, Updated 8, Errors 0 |
| Tree | Firm / Partners, Administration, Clients, Statutory, Templates, Trainee-Workspace, Archive |
| find as ubuntu | Permission denied (expected; data dir is www-data) |
| Shares | none yet |

## Stop

Firm folder tree is complete. Do not upload 150 GB. Do not share to groups until staff users exist.
