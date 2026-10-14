# From Home — Next Step: Ubuntu patch only

Instance `i-002509b77963fd5fc` (`saraswathi-nextcloud-app`) is Running. SSM works.
Do this as `logesh.implementer` in Mumbai. Use **Session Manager**, not SSH.

Do **not** install Nextcloud, PHP, Collabora, or Certbot in this step.
Do **not** open port 22.
Do **not** paste the RDS password.

## 1. Open a new SSM session

1. EC2 → Instances → `saraswathi-nextcloud-app`.
2. **Connect** → **Session Manager** → **Connect**.
3. Run:

```bash
whoami
lsb_release -a
uname -r
```

Expected: user is `ssm-user` or `ubuntu`; Ubuntu is **24.04**.

## 2. Patch the OS (this step only)

Run these two commands. Wait for each to finish. If a pink/blue config screen appears, choose **keep the local version currently installed** / default.

```bash
sudo apt update
```

```bash
sudo DEBIAN_FRONTEND=noninteractive apt full-upgrade -y
```

If it asks to restart services, choose **Yes** / default.

## 3. See if a reboot is needed

```bash
test -f /var/run/reboot-required && echo REBOOT_REQUIRED || echo NO_REBOOT
```

Do **not** reboot until you reply with that one line.

## 4. Reboot after REBOOT_REQUIRED (2026-08-25)

`apt full-upgrade` requested a reboot. Do this in the same SSM window:

```bash
sudo reboot
```

The Session Manager tab will disconnect. That is expected.

1. Wait 2–4 minutes.
2. EC2 → Instances → `i-002509b77963fd5fc` until **Running**.
3. **Status checks** should become **2/2** (Initializing is OK first).
4. **Connect** → **Session Manager** → **Connect**.
5. If Connect is grey, wait one more minute and refresh. Do not open port 22.

Then run only:

```bash
lsb_release -a
uname -r
test -f /var/run/reboot-required && echo REBOOT_REQUIRED || echo NO_REBOOT
systemctl --failed --no-legend
```

Do not install nginx, PHP, or Nextcloud until `NO_REBOOT` and failed units are empty or explained.

## 5. After reboot (2026-08-25)

| Item | Value |
|---|---|
| Ubuntu | 24.04.4 LTS |
| Kernel | 7.0.0-1011-aws |
| Reboot file | NO_REBOOT |
| Failed units | none |

Patch step is done. Next: [FROM_HOME_NEXT_STEP_BASE_PACKAGES.md](FROM_HOME_NEXT_STEP_BASE_PACKAGES.md).
