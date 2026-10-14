#!/bin/bash
# ============================================================
# Saraswathi Nextcloud Office Fix Script
# 
# Context: files.t-saraswathi.in on EC2 i-002509b77963fd5fc
#   Nextcloud 34.0.4 at /var/www/nextcloud
#   Data at /opt/nextcloud/data
#   Built-in CODE (richdocumentscode) — no Docker
#   nginx site: /etc/nginx/sites-enabled/files.t-saraswathi.in
#   Access: AWS SSM Session Manager (no SSH)
#
# Run on the server as:
#   sudo bash /tmp/fix_office.sh
#
# What this script does:
#   1. Removes the broken standalone nextcloud.conf
#   2. Restores wopi_url to EMPTY (built-in CODE autodetect, 
#      which is how it originally worked per the project docs)
#   3. Restores the correct wopi_allowlist
#   4. Restarts Collabora CODE
#   5. Tests and restarts nginx + PHP-FPM
#   6. Verifies everything
# ============================================================
set -e

echo ""
echo "=========================================="
echo " Saraswathi Nextcloud Office Fix"
echo " files.t-saraswathi.in"
echo "=========================================="

# ----------------------------------------------------------
# Step 1: Remove the broken standalone nextcloud.conf
# This file had a bare "location" block outside any server{}
# which caused: "location" directive is not allowed here
# The ONLY nginx site file should be files.t-saraswathi.in
# ----------------------------------------------------------
echo ""
echo "[Step 1/6] Removing broken /etc/nginx/sites-enabled/nextcloud.conf ..."
if [ -f /etc/nginx/sites-enabled/nextcloud.conf ]; then
    rm -f /etc/nginx/sites-enabled/nextcloud.conf
    echo "  ✔ Removed."
else
    echo "  ✔ Already gone."
fi

# ----------------------------------------------------------
# Step 2: Restore wopi_url to EMPTY (delete it)
#
# Per the project technical snapshot (02-architecture/
# TECHNICAL_SNAPSHOT_AND_FLOW.md line 208):
#   "Custom wopi_url is EMPTY. Built-in CODE is reached 
#    only through proxy.php?req=..."
#
# The original working setup had NO custom wopi_url.
# Built-in richdocumentscode autodetects via proxy.php.
# All the wopi_url values you tried were WRONG for built-in CODE.
# ----------------------------------------------------------
echo ""
echo "[Step 2/6] Restoring wopi_url to empty (built-in CODE autodetect) ..."
cd /var/www/nextcloud

# Delete ALL custom WOPI URLs — built-in CODE doesn't need them
sudo -u www-data php occ config:app:delete richdocuments wopi_url 2>/dev/null && \
    echo "  ✔ Deleted wopi_url" || echo "  ✔ wopi_url already empty"

sudo -u www-data php occ config:app:delete richdocuments public_wopi_url 2>/dev/null && \
    echo "  ✔ Deleted public_wopi_url" || echo "  ✔ public_wopi_url already empty"

# Remove certificate verification override (proper LE cert exists)
sudo -u www-data php occ config:app:delete richdocuments disable_certificate_verification 2>/dev/null && \
    echo "  ✔ Deleted disable_certificate_verification" || echo "  ✔ Already clean"

# ----------------------------------------------------------
# Step 3: Restore correct wopi_allowlist + settings
#
# Per the project docs:
#   wopi_allowlist: 127.0.0.1, ::1, 10.20.1.144, 3.111.213.217
#   allow_local_remote_servers: true
# ----------------------------------------------------------
echo ""
echo "[Step 3/6] Restoring wopi_allowlist and allow_local_remote_servers ..."

sudo -u www-data php occ config:app:set richdocuments wopi_allowlist \
    --value="127.0.0.1,::1,10.20.1.144,3.111.213.217"
echo "  ✔ wopi_allowlist set"

sudo -u www-data php occ config:system:set allow_local_remote_servers --value=true --type=boolean
echo "  ✔ allow_local_remote_servers = true"

# ----------------------------------------------------------
# Step 4: Restart Collabora CODE (richdocumentscode)
# This kills the old coolwsd and starts a fresh one
# ----------------------------------------------------------
echo ""
echo "[Step 4/6] Restarting Collabora CODE ..."

# Kill any stale coolwsd processes
pkill -f coolwsd 2>/dev/null || true
pkill -f coolforkit 2>/dev/null || true
pkill -f Collabora_Online 2>/dev/null || true
sleep 2

# Clean up stale temp files
rm -rf /tmp/coolwsd* /tmp/appimage_extracted_* 2>/dev/null || true

# Disable and re-enable to force fresh start
sudo -u www-data php occ app:disable richdocumentscode
sleep 3
sudo -u www-data php occ app:enable richdocumentscode
echo "  ✔ richdocumentscode restarted"
echo "  Waiting 15 seconds for coolwsd to start..."
sleep 15

# Also cycle richdocuments (the frontend app)
sudo -u www-data php occ app:disable richdocuments
sleep 2
sudo -u www-data php occ app:enable richdocuments
echo "  ✔ richdocuments restarted"

# Update mimetypes
sudo -u www-data php occ maintenance:mimetype:update-js
echo "  ✔ Mimetypes updated"

# ----------------------------------------------------------
# Step 5: Test and restart nginx + PHP-FPM
# ----------------------------------------------------------
echo ""
echo "[Step 5/6] Testing and restarting nginx + php8.3-fpm ..."

nginx -t
if [ $? -eq 0 ]; then
    systemctl restart nginx php8.3-fpm
    echo "  ✔ nginx and php8.3-fpm restarted"
else
    echo "  ✘ nginx config test FAILED. Check the output above."
    echo "  Nginx was NOT restarted."
    exit 1
fi

# ----------------------------------------------------------
# Step 6: Verify everything
# ----------------------------------------------------------
echo ""
echo "=========================================="
echo " Verification"
echo "=========================================="

echo ""
echo "--- Service Status ---"
systemctl is-active nginx && echo "  ✔ nginx: running" || echo "  ✘ nginx: NOT running"
systemctl is-active php8.3-fpm && echo "  ✔ php8.3-fpm: running" || echo "  ✘ php8.3-fpm: NOT running"

echo ""
echo "--- coolwsd Process ---"
if ps aux | grep -q "[c]oolwsd"; then
    echo "  ✔ coolwsd is running"
    ps aux | grep "[c]oolwsd" | grep -v "grep" | head -2
else
    echo "  ✘ coolwsd is NOT running — CODE may need more time to start"
    echo "  Check again in 30 seconds: ps aux | grep coolwsd"
fi

echo ""
echo "--- Ports 80/443 ---"
ss -tulpn | grep -E '(:80|:443)' | head -4
echo ""

echo ""
echo "--- richdocuments Config ---"
echo -n "  wopi_url: "
sudo -u www-data php occ config:app:get richdocuments wopi_url 2>/dev/null || echo "(empty — correct for built-in CODE)"
echo -n "  wopi_allowlist: "
sudo -u www-data php occ config:app:get richdocuments wopi_allowlist 2>/dev/null || echo "(not set)"

echo ""
echo "--- WOPI Discovery Test ---"
# For built-in CODE, discovery is at proxy.php?req=/hosting/discovery
DISCOVERY=$(curl -s -k --max-time 15 "https://files.t-saraswathi.in/apps/richdocumentscode/proxy.php?req=/hosting/discovery" | head -5)
if echo "$DISCOVERY" | grep -qi "wopi"; then
    echo "  ✔ WOPI discovery responding!"
    echo "$DISCOVERY" | head -3
else
    echo "  ⚠ WOPI discovery not responding yet. Output:"
    echo "$DISCOVERY"
    echo ""
    echo "  If empty, wait 30 seconds and run:"
    echo "  curl -s https://files.t-saraswathi.in/apps/richdocumentscode/proxy.php?req=/hosting/discovery | head -5"
fi

echo ""
echo "--- Nextcloud status.php ---"
curl -s -k https://files.t-saraswathi.in/status.php
echo ""

echo ""
echo "--- Disk Space ---"
df -h /

echo ""
echo "--- nginx site files (should be ONLY files.t-saraswathi.in) ---"
ls -la /etc/nginx/sites-enabled/

echo ""
echo "=========================================="
echo " DONE!"
echo ""
echo " Open https://files.t-saraswathi.in"
echo " Login as saraswathi.admin"
echo " Try opening a .docx or .xlsx file"
echo ""
echo " If Office still fails, run:"
echo "   sudo tail -50 /var/www/nextcloud/data/nextcloud.log | grep -i 'richdocuments\|wopi\|cool'"
echo "   sudo tail -50 /tmp/coolwsd.*/coolwsd.log"
echo "=========================================="
