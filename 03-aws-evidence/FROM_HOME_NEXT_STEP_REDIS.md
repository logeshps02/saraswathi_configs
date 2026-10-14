# From Home — Next Step: Redis local-only check

nginx, redis, and fail2ban are **active**. Local HTTP is 200.
Use Session Manager. Paste one command at a time with Ctrl+V.
Do **not** install PHP or Nextcloud in this step.

## 1. Confirm Redis listens only on localhost

```bash
ss -ltnp | grep 6379
```

Expected: `127.0.0.1:6379` and/or `[::1]:6379`.
Not `0.0.0.0:6379`.

## 2. Confirm Redis answers locally

```bash
redis-cli ping
```

Expected: `PONG`

## 3. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| Listen | 127.0.0.1:6379 and [::1]:6379 only |
| Public 0.0.0.0:6379 | no |
| redis-cli | PONG |

Redis step is done. Next: [FROM_HOME_NEXT_STEP_PHP.md](FROM_HOME_NEXT_STEP_PHP.md).
