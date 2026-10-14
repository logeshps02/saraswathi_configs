# From Home — Next Step: PHP memory and upload limits

PHP 8.3.6 FPM is active and required modules are present.
Use Session Manager. Paste one command at a time with Ctrl+V.
Do **not** download Nextcloud yet.

## 1. Write a drop-in config

```bash
printf '%s\n' 'memory_limit = 512M' 'upload_max_filesize = 512M' 'post_max_size = 512M' 'output_buffering = Off' 'max_execution_time = 3600' 'max_input_time = 3600' 'date.timezone = Asia/Kolkata' | sudo tee /etc/php/8.3/mods-available/saraswathi-limits.ini
```

You should see those seven lines printed back.

## 2. Enable for FPM and CLI, then restart FPM

```bash
sudo phpenmod -v 8.3 -s ALL saraswathi-limits
```

```bash
sudo systemctl restart php8.3-fpm
```

```bash
systemctl is-active php8.3-fpm
```

## 3. Confirm values

```bash
php -i | grep -E '^memory_limit|^upload_max_filesize|^post_max_size|^date.timezone'
```

Expected:
- memory_limit => 512M
- upload_max_filesize => 512M
- post_max_size => 512M
- date.timezone => Asia/Kolkata

## 4. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| php8.3-fpm | active after restart |
| memory_limit | 512M |
| post_max_size | 512M |
| upload_max_filesize | 512M |
| date.timezone | Asia/Kolkata (terminal may wrap the name) |

PHP limits step is done. Next: [FROM_HOME_NEXT_STEP_RDS_CLIENT.md](FROM_HOME_NEXT_STEP_RDS_CLIENT.md).
