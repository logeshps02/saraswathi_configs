# From Home — Next Step: Nextcloud Activity

S3 files bucket versioning is **Enabled**. SSE-S3 on. Object Lock / MFA delete / website stay **off**. Do **not** upload 150 GB. Do **not** set objectstore.

Next: confirm the **Activity** app (file/share/login events in Nextcloud). Do **not** create extra users. Do **not** paste cookies or `config.php`.

Use Session Manager. One line.

## 1. Confirm enabled

```sh
sudo -u www-data php /var/www/nextcloud/occ app:list --enabled | grep -Ei 'activity'
```

If `activity` is not listed:

```sh
sudo -u www-data php /var/www/nextcloud/occ app:enable activity && sudo -u www-data php /var/www/nextcloud/occ app:list --enabled | grep -Ei 'activity'
```

Need a line with `activity` and a version. Email notifications can stay off (no SMTP yet).

### Confirmed (2026-08-26)

| Item | Value |
|---|---|
| activity | **7.0.0** already enabled |

## Stop

Do not configure SMTP. Do not create users. `admin_audit` is the next guide.
