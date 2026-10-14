# From Home — Next Step: Nextcloud versions + trash

AWS Backup on-demand is **Completed** in `saraswathi-backup-vault` (`snap-0877c1316d9702f73`). Daily plan remains 12:30 AM IST. Do **not** Restore. Do **not** enable Fast Snapshot Restore.

Next: confirm Nextcloud **file versions** and **trash** apps (Phase 6 user restore path). Do **not** create extra users. Do **not** delete production files.

Use Session Manager. Paste each block as **one line**.

Do **not** paste `config.php`. Do **not** paste cookies.

## 1. Apps enabled

```sh
sudo -u www-data php /var/www/nextcloud/occ app:list --enabled | grep -Ei 'files_versions|files_trashbin'
```

Need both `files_versions` and `files_trashbin`. If one is missing:

### Observed (2026-08-26)

| Check | Result |
|---|---|
| `app:list --enabled` grep | **empty** — neither app listed |
| `versions_retention_obligation` | unset `VR_EXIT:1` (default `auto`) |
| `trashbin_retention_obligation` | unset `TR_EXIT:1` (default `auto`) |

Do not set retention. Enable both apps next.

```sh
sudo -u www-data php /var/www/nextcloud/occ app:enable files_versions && sudo -u www-data php /var/www/nextcloud/occ app:enable files_trashbin && sudo -u www-data php /var/www/nextcloud/occ app:list --enabled | grep -Ei 'files_versions|files_trashbin'
```

## 2. Retention knobs (read only)

```sh
sudo -u www-data php /var/www/nextcloud/occ config:system:get versions_retention_obligation; echo VR_EXIT:$?; sudo -u www-data php /var/www/nextcloud/occ config:system:get trashbin_retention_obligation; echo TR_EXIT:$?
```

Empty / `VR_EXIT:1` / `TR_EXIT:1` means Nextcloud defaults (`auto`). Do **not** set new values this step.

### Enabled (2026-08-26)

| App | Version |
|---|---|
| `files_versions` | **1.27.0** enabled |
| `files_trashbin` | **1.24.0** enabled |
| Retention keys | still unset (`auto`) |

## Stop

Do not delete files to test trash. Do not Restore AWS snapshots. Do not create users. Do not set retention keys. S3 versioning confirm is the next guide.
