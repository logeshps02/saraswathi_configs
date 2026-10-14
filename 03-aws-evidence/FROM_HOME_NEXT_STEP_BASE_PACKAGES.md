# From Home — Next Step: nginx, redis, fail2ban, ufw

Instance `i-002509b77963fd5fc` is Ubuntu **24.04.4 LTS**, patched, `NO_REBOOT`.
Use Session Manager. Do **not** install PHP, Nextcloud, Collabora, Certbot, or MariaDB server.

Do **not** open port 22 in UFW.

## 1. Install only these packages

```bash
sudo DEBIAN_FRONTEND=noninteractive apt install -y nginx redis-server fail2ban ufw unattended-upgrades
```

Wait until it finishes.

## 2. Enable services

```bash
sudo systemctl enable --now nginx redis-server fail2ban
sudo systemctl is-active nginx redis-server fail2ban
```

Expected: `active` three times.

## 3. Host firewall (no SSH)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
sudo ufw status verbose
```

UFW may warn that SSH is not allowed. That is correct. SSM uses outbound HTTPS, not port 22.

Status must show:
- Default: deny (incoming), allow (outgoing)
- 80/tcp ALLOW
- 443/tcp ALLOW
- no 22/tcp

## 4. Confirm versions only

```bash
lsb_release -ds
nginx -v
redis-server --version
fail2ban-client -V | head -n 1
systemctl --failed --no-legend
```

Do not edit Nginx site files yet. Do not browse the public IP except a later check I will give.

## 5. Confirmed from SSM (2026-08-25)

| Item | Value |
|---|---|
| UFW | active; deny incoming; allow outgoing; 80/tcp and 443/tcp ALLOW; no 22 |
| nginx | 1.24.0 (Ubuntu) |
| redis | 7.0.15 |
| fail2ban | 1.0.2 |
| Note | `systemctl` was mistyped as `systemctl1`; rerun failed-units check |

## 6. Finish this step

Copy exactly. The command is `systemctl` with no `1` at the end. The service is `redis-server`, not `redid-server`.

```bash
systemctl is-active nginx redis-server fail2ban
systemctl --failed --no-legend
```

Local HTTP check already returned `HTTP/1.1 200 OK` from nginx 1.24.0 on 2026-08-24 19:48 GMT.

Do not install PHP or Nextcloud yet.

## 7. Services confirmed (2026-08-25)

| Item | Value |
|---|---|
| nginx | active |
| redis-server | active |
| fail2ban | active |
| failed units | none |
| local HTTP | HTTP/1.1 200 OK |

Base packages step is done. Next: Redis bind check, then PHP version pin. Still no Nextcloud.
