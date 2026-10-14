# From Home — Next Step: Download Nextcloud 34.0.3

Private RDS works. Pin and verify the official tarball only.
Use Session Manager. Paste one command at a time with Ctrl+V.

Do **not** extract, chown, run occ, or open the install wizard in this step.
Do **not** install Apache, MariaDB server, snap, or Certbot.
Do **not** put the database password in chat.

Pinned from official sources on 2026-08-25:

| Item | Value |
|---|---|
| Version | 34.0.3 (Hub 26 Spring; supported until 2027-06) |
| Why not 32 | 32.0.x EOL is 2026-09 |
| Why not 35 | 35 is still RC, not stable |
| Tarball | https://download.nextcloud.com/server/releases/nextcloud-34.0.3.tar.bz2 |
| SHA256 file | https://download.nextcloud.com/server/releases/nextcloud-34.0.3.tar.bz2.sha256 |

## 1. Download tarball and official checksum

```bash
cd /tmp
```

```bash
curl -fLO https://download.nextcloud.com/server/releases/nextcloud-34.0.3.tar.bz2
```

Wait until the prompt returns. The file is about 268M.

```bash
curl -fLO https://download.nextcloud.com/server/releases/nextcloud-34.0.3.tar.bz2.sha256
```

## 2. Verify SHA256

```bash
sha256sum -c nextcloud-34.0.3.tar.bz2.sha256
```

Expected: `nextcloud-34.0.3.tar.bz2: OK`

If it is not `OK`, stop. Do not extract. Reply with the exact line.

## 3. Confirm the file is present (do not unpack)

```bash
ls -lh /tmp/nextcloud-34.0.3.tar.bz2 /tmp/nextcloud-34.0.3.tar.bz2.sha256
```

Expected: tarball around 268M and a small `.sha256` file.

## Result (2026-08-25)

| Check | Value |
|---|---|
| Tarball | /tmp/nextcloud-34.0.3.tar.bz2 269M |
| SHA256 of tarball | nextcloud-34.0.3.tar.bz2: OK |
| nextcloud-34.0.3.metadata | Not downloaded; official .sha256 lists it too — ignore that FAILED line |

The tarball itself is verified. Do not re-download.
