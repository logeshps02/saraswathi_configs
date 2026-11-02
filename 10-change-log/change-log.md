# Project Change Log

Record every production or scope change here. Never put passwords, keys, or MFA codes in this file.

| Date | Operator | Area | Change | Reason | Rollback plan | Status |
|---|---|---|---|---|---|---|
| 2026-09-19 | Copilot | 2026-27 HDD | HDD remounted as D:; rebuilt STRUCTURED_COPY_MAP_2026_27.csv from real Uploaded Forms (220 jobs, 220 sources exist); PRINTERS + PALANIAPPA’S MOTORS kept; THIRUKONDA unsorted; resume-safe local copy to C:\\SARASWATHI_2026_27 ok; dest ~6429 files / 5.60 GiB; rclone.exe still missing so DATA1 append not started | Sorted Company\\2026-27 local copy then rclone copy append | Leave HDD originals; do not rclone sync | In progress |
| 2026-09-19 | Copilot | 2026-27 vs F:\\f | CS: 33 names not on F:\\f are separate companies — keep new DATA1 folders. 114 append under existing F:\\f names. THIRUKONDA unsorted. Local C:\\SARASWATHI_2026_27 ready (6431 files / 6.16 GB). rclone.exe not on this PC; copy to DATA1 not started | Append + 33 new company folders | Remove a new folder only if CS later merges it | In progress |
| 2026-09-19 | Copilot | 2026-27 vs F:\\f | Saved 863 F:\\f company names; compared to local 2026-27 dest; remapped SEL JEGAT PRINTER→PRINTERS and PALANIAPPA MOTOR→PALANIAPPA’S MOTORS; 114 dests match F:\\f; 33 not on F:\\f; THIRUKONDA still unsorted; map rebuilt from C:\\SARASWATHI_2026_27 (219 jobs) after CSV truncate; HDD unplugged; rclone not started | Append 2026-27 under existing DATA1/F:\\f names only | Move those two dest trees back; restore map if HDD remounted | In progress |
| 2026-09-18 | Copilot | 2026-27 HDD | Left THIRUKONDA DIR-3 unsorted; remapped ADR/SOUTHFIELD/HOMOEO/STATFIN onto existing company names and moved local dest trees; rclone not on this PC | Append 2026-27 under existing company folders only | Rename dest folders back if staff reject spelling merge | In progress |
| 2026-08-31 | Logesh P S | Storage plan | Quotation path locked: 30 GiB EBS stay; no objectstore; 132 GB via External storage S3 folder Backup_data; UAT disposable; runbooks 16–20 + M1C/M2/M3 updated | Budget $60; quote S3 150 GB not 200 GiB disk | Unmount Backup_data; do not grow volume | In progress |
| 2026-08-24 | Logesh P S | Project setup | Created project control folders 00–10 | Start of delivery | Delete unused empty folders if structure is rejected | Done |
| 2026-08-24 | Logesh P S | Mobilisation | Added client meeting AWS + domain checklist and evidence templates | Contract signed; users deferred; next action is firm-owned IDs | Remove templates if client already has account/domain | Done |
| 2026-08-24 | Logesh P S | AWS foundation | Added from-home CloudTrail click-through | Work after meeting is remote once IAM login is proven | Delete guide if trail already exists | Done |
| 2026-08-24 | Logesh P S | AWS foundation | Added from-home Mumbai VPC click-through | Next remote step after CloudTrail | Delete unused VPC if created in wrong region | Done |
| 2026-08-24 | Logesh P S | Domain | Route 53 register started for t-saraswathi.in | Firm-owned hostname | Cancel register only if wrong name | In progress |
| 2026-08-24 | Logesh P S | Domain | t-saraswathi.in registered; auto-renew on; transfer lock on; email reachability verified | Firm-owned hostname ready | Do not delete domain or transfer out | Done |
| 2026-08-24 | Logesh P S | AWS foundation | Started CloudTrail setup from home in ap-south-1 | Audit before VPC/EC2 | Delete unused trail only if created in wrong account | In progress |
| 2026-08-24 | Logesh P S | AWS foundation | Saraswathi-management-trail is Logging; bucket aws-cloudtrail-logs-055855670388-1f1c3ed9 | Account audit on | Do not delete trail or log bucket | Done |
| 2026-08-24 | Logesh P S | AWS foundation | Created saraswathi-nextcloud-vpc vpc-0a25ed4fa155f526d 10.20.0.0/16 in ap-south-1 | Network foundation | Delete VPC only if unused and empty | Done |
| 2026-08-24 | Logesh P S | AWS foundation | Created 6 Saraswathi subnets in vpc-0a25ed4fa155f526d | Network layout | Delete unused empty subnets only | Done |
| 2026-08-24 | Logesh P S | AWS foundation | Enabled public IPv4 auto-assign on saraswathi-public-a and public-b | Public entry later | Turn auto-assign off if unused | Done |
| 2026-08-24 | Logesh P S | AWS foundation | Attached saraswathi-igw igw-02ac3964b2f226ce1 to saraswathi-nextcloud-vpc | Public internet path | Detach only if unused | Done |
| 2026-08-24 | Logesh P S | AWS foundation | Public RT rtb-0f47bead49020f30c: 0.0.0.0/0 to IGW; associated public-a and public-b | Internet for public subnets only | Disassociate subnets if wrong | Done |
| 2026-08-24 | Logesh P S | AWS foundation | Created saraswathi-rt-app and saraswathi-rt-db; associated private subnets; no internet routes | Isolate app and DB | Move subnets back to main RT if needed | Done |
| 2026-08-24 | Logesh P S | AWS foundation | Enabled VPC flow logs fl-0bb98d0c00ed6bd8b to /vpc/saraswathi-nextcloud-vpc | Network audit | Delete flow log if unused | Done |
| 2026-08-24 | Logesh P S | AWS foundation | Created web/app/db/admin security groups in saraswathi-nextcloud-vpc | Least privilege later | Recreate admin SG to fix name typo | In progress |
| 2026-08-24 | Logesh P S | AWS foundation | Confirmed SG rules and renamed admin to saraswathi-sg-admin sg-09e08c9be158cbb69 | Least privilege | Recreate SGs if sources are wrong | Done |
| 2026-08-24 | Logesh P S | AWS foundation | Created KMS keys alias/saraswathi-ebs and alias/saraswathi-rds with 365-day rotation | Encrypt EBS and RDS later | Disable keys only if unused | Done |
| 2026-08-24 | Logesh P S | AWS foundation | Created private S3 bucket saraswathi-nextcloud-files-055855670388 in ap-south-1 | Nextcloud file store later | Empty bucket can be deleted if unused | Done |
| 2026-08-25 | Logesh P S | AWS foundation | RDS create form corrected to db.t4g.micro gp3 ~USD 17.95 in saraswathi-nextcloud-vpc | Avoid default expensive RDS | Cancel form if public or Multi-AZ | In progress |
| 2026-08-25 | Logesh P S | AWS foundation | Created saraswathi-nextcloud-db Available db.t4g.micro MySQL in ap-south-1b | Nextcloud metadata | Disable deletion protection then delete only if unused | Done |
| 2026-08-25 | Logesh P S | AWS foundation | Confirmed RDS private; endpoint stored without password | Ready for EC2 | Rotate master password if exposed | Done |
| 2026-08-25 | Logesh P S | AWS foundation | EC2 launch form reviewed; AMI summary showed Ubuntu 26.04 mismatch | Prevent wrong AMI | Do not launch until 24.04 LTS confirmed | In progress |
| 2026-08-25 | Logesh P S | AWS foundation | EC2 form reset: still ami-01a00762f46d584a1; Create security group SSH 22 0.0.0.0/0; 8 GiB volume | Prevent open SSH and undersized disk | Do not launch; restore existing SGs and 30 GiB encrypted | In progress |
| 2026-08-25 | Logesh P S | AWS foundation | Confirmed Ubuntu 24.04 LTS AMI ami-006f82a1d5a27da54 noble x86_64 | Correct OS for Nextcloud host | Do not launch until SGs and 30 GiB disk restored | In progress |
| 2026-08-25 | Logesh P S | AWS foundation | Launched i-002509b77963fd5fc saraswathi-nextcloud-app Ubuntu 24.04 t3.medium in public-a | Nextcloud app host | Stop instance if unused; termination protection is on | Done |
| 2026-08-25 | Logesh P S | AWS foundation | Confirmed EC2 SGs web/app/admin, no SSH; vol-0063c19bdcb7583bf 30 GiB encrypted; SSM connected | Ready to patch Ubuntu | Do not open port 22 | Done |
| 2026-08-25 | Logesh P S | AWS foundation | Ubuntu apt full-upgrade on i-002509b77963fd5fc reported REBOOT_REQUIRED | Apply kernel/security patches | Reconnect SSM after reboot; do not open SSH | In progress |
| 2026-08-25 | Logesh P S | AWS foundation | Rebooted i-002509b77963fd5fc; Ubuntu 24.04.4 LTS kernel 7.0.0-1011-aws; no failed units | Finish OS patch | Do not install PHP/Nextcloud yet | Done |
| 2026-08-25 | Logesh P S | AWS foundation | Installed nginx 1.24.0 redis 7.0.15 fail2ban 1.0.2; UFW 80/443 only on i-002509b77963fd5fc | Base web stack | Disable UFW only if lockout; do not open 22 | In progress |
| 2026-08-25 | Logesh P S | AWS foundation | Local curl http://127.0.0.1/ returned HTTP/1.1 200 OK nginx 1.24.0 | Confirm default site | is-active check still pending after systemctl typo | In progress |
| 2026-08-25 | Logesh P S | AWS foundation | nginx redis fail2ban all active; no failed units on i-002509b77963fd5fc | Base stack healthy | Do not install PHP until version is pinned | Done |
| 2026-08-25 | Logesh P S | AWS foundation | Redis 6379 bound to 127.0.0.1 and ::1 only; redis-cli PONG | Local cache only | Bind to 0.0.0.0 would be rollback/fix immediately | Done |
| 2026-08-25 | Logesh P S | AWS foundation | Installed PHP 8.3.6 and php8.3-fpm active on i-002509b77963fd5fc | Nextcloud runtime pin | Remove php8.3 packages only if unused | Done |
| 2026-08-25 | Logesh P S | AWS foundation | Confirmed PHP 8.3 modules including gd imagick redis apcu pdo_mysql intl zip | Nextcloud PHP deps | Reinstall missing php8.3-* only if a module drops | Done |
| 2026-08-25 | Logesh P S | AWS foundation | Set PHP 8.3 limits 512M upload/memory; timezone Asia/Kolkata | Nextcloud uploads | Remove /etc/php/8.3/mods-available/saraswathi-limits.ini | Done |
| 2026-08-25 | Logesh P S | AWS foundation | mysql-client 8.0.46; RDS 10.20.22.41 port open; SELECT VERSION 8.4.9 as ncadmin | Private DB path proven | Do not open RDS publicly; rotate password if ever pasted | Done |
| 2026-08-25 | Logesh P S | App install | Downloaded nextcloud-34.0.3.tar.bz2 269M; official SHA256 OK | Pin current supported Hub 26 Spring | Delete /tmp tarball if unused; do not use 32.x or 35 RC | Done |
| 2026-08-25 | Logesh P S | App install | First tar extract failed: bzip2 missing; /var/www/nextcloud not created | Need bzip2 for .tar.bz2 | Install bzip2 then retry extract; do not re-download | In progress |
| 2026-08-25 | Logesh P S | App install | Installed bzip2 1.0.8; extracted Nextcloud 34.0.3.2 to /var/www/nextcloud; data /opt/nextcloud/data www-data | Official source layout | Remove tree only if unused; do not run wizard yet | Done |
| 2026-08-25 | Logesh P S | App install | HTTP-only nginx site files.t-saraswathi.in; FPM sock OK; nginx -t ok (wasm warn); reload; curl status.php HTTP 200 JSON | Official nginx-root sample, HTTPS off | Confirm status.php body; no occ/wizard/TLS yet | In progress |
| 2026-08-25 | Logesh P S | App install | status.php: installed=false, version 34.0.3.2 | PHP reaches Nextcloud | Next later: occ maintenance:install (RDS + /opt/nextcloud/data); no TLS yet | Done |
| 2026-08-25 | Logesh P S | App install | Started CLI install step: RDS mysql nextcloud/ncadmin, data /opt/nextcloud/data, admin saraswathi.admin | Official occ maintenance:install; passwords via read -s only | Confirm occ status still installed=false | In progress |
| 2026-08-25 | Logesh P S | App install | occ maintenance:install succeeded; admin saraswathi.admin; data /opt/nextcloud/data; RDS mysql | Official CLI install; sh used stty -echo for secrets | Unset session secrets; occ status; trusted_domains | In progress |
| 2026-08-25 | Logesh P S | App install | occ status installed=true 34.0.3.2; trusted_domains 0 = files.t-saraswathi.in | Official hostname only | Recheck status.php; set region/timezone; no TLS/DNS yet | In progress |
| 2026-08-25 | Logesh P S | App install | status.php installed=true 34.0.3.2; datadir /opt/nextcloud/data | HTTP Host files.t-saraswathi.in now trusted | SSM mashed wrap-up sets; re-run region/tz/cli.url | In progress |
| 2026-08-25 | Logesh P S | App install | Set IN phone region, Asia/Kolkata, overwrite.cli.url http://files.t-saraswathi.in | CLI install wrap-up | Next later: DNS A + TLS/Certbot; no browser login required now | Done |
| 2026-08-25 | Logesh P S | DNS / TLS | Started files.t-saraswathi.in A record + Certbot step | HTTPS for official hostname | Do not change NS; rollback = delete only the files A record | In progress |
| 2026-08-25 | Logesh P S | DNS / TLS | Read app public IPv4 3.111.213.217 via IMDSv2 | A record target | Recheck IP if instance is stopped/started | In progress |
| 2026-08-25 | Logesh P S | DNS / TLS | Route 53 change C09702172G2CLD1D4TXOC PENDING for t-saraswathi.in | files A record | Delete only the files A record if wrong; do not touch NS | In progress |
| 2026-08-25 | Logesh P S | DNS / TLS | getent hosts files.t-saraswathi.in -> 3.111.213.217 | A record live from app host | Recheck if public IP changes | In progress |
| 2026-08-25 | Logesh P S | DNS / TLS | Let's Encrypt issued for files.t-saraswathi.in; expires 2026-11-22; nginx plugin deployed | HTTPS | Revoke/replace cert only if wrong name; do not paste private key | In progress |
| 2026-08-25 | Logesh P S | DNS / TLS | HTTPS live; overwriteprotocol=https; status.php 200 installed=true 34.0.3.2 | Official hostname | Recheck if public IP changes; next: Redis+cron | Done |
| 2026-08-25 | Logesh P S | App install | Started Redis APCu cache + locking and system cron | Official memcache + www-data crontab | Remove memcache keys and crontab line if unused | In progress |
| 2026-08-25 | Logesh P S | App install | APCu local + Redis distributed/locking; www-data cron every 5 min | Official cache and background jobs | Remove memcache keys and crontab line if unused | Done |
| 2026-08-25 | Logesh P S | App install | Started occ setupchecks / health pass | Classify warnings before S3 or apps | Do not change config.php by hand | In progress |
| 2026-08-25 | Logesh P S | App install | Health pass: HTTPS/cache/cron/DB green; leftover HSTS, maintenance window, mimetype repair, Talk HPB | Classify only; no product enable yet | Next: small nginx HSTS + maintenance window + mimetype repair | Done |
| 2026-08-25 | Logesh P S | App install | Started HSTS header, maintenance_window_start 18 UTC, expensive mimetype repair | Close leftover health warnings | Revert HSTS add_header if nginx -t fails | In progress |
| 2026-08-25 | Logesh P S | App install | HSTS max-age=15552000; maintenance window 18 UTC; mimetype repair OK; setupchecks headers green | Close leftover health warnings | Next later: S3 primary storage | Done |
| 2026-08-25 | Logesh P S | Storage | Started S3 IAM on saraswathi-ec2-ssm for files bucket; no objectstore yet | Instance already on local data dir | Detach inline policy if unused | In progress |
| 2026-08-25 | Logesh P S | Storage | Bucket and inline policy confirmed; Ubuntu 24.04 apt awscli missing | Need official AWS CLI v2 then probe | Do not create access keys | In progress |
| 2026-08-25 | Logesh P S | Storage | AWS CLI 2.36.30; instance role S3 probe OK on files bucket; no objectstore | IAM-only access proven | Next later: Collabora/Talk or primary S3 migration plan | Done |
| 2026-08-25 | Logesh P S | Apps | Started Nextcloud Office + built-in CODE on same host | Feature B document editing without extra EC2 | Disable richdocumentscode if RAM too low | In progress |
| 2026-08-25 | Logesh P S | Apps | richdocuments 11.1.0 + CODE 26.4.104 enabled; root WOPI 404 | Need proxy.php WOPI URL | Keep allow_local_remote_servers | In progress |
| 2026-08-25 | Logesh P S | Apps | CODE discovery 200 COOLWSD 26.04.1.4; activate-config path-style 400 | Clear custom wopi_url for built-in CODE | Keep wopi_allowlist | In progress |
| 2026-08-25 | Logesh P S | Apps | Built-in CODE live; custom WOPI URLs cleared; discovery 200 | Nextcloud Office on same host | Update wopi_allowlist if public IP changes | Done |
| 2026-08-25 | Logesh P S | Apps | Started Calendar, Contacts, Tasks enable | Feature E groupware | Disable apps if unused | In progress |
| 2026-08-25 | Logesh P S | Apps | calendar 6.5.4 contacts 8.7.6 tasks 0.18.1; CalDAV/CardDAV 301; admin Personal + Contacts | Feature E groupware | Shared firm calendar after users exist | Done |
| 2026-08-26 | Logesh P S | Apps | Started Deck app enable | Feature F boards | Disable deck if unused | In progress |
| 2026-08-26 | Logesh P S | Apps | deck 1.18.3 enabled; /apps/deck/ 401 unauthenticated; no board-list occ | Feature F | First board in browser later | Done |
| 2026-08-26 | Logesh P S | Identity | Started empty Nextcloud groups from runbook; no extra users | Groups before users | occ group:delete if unused | In progress |
| 2026-08-26 | Logesh P S | Identity | Six Firm-* groups; saraswathi.admin in Firm-Admins + admin; others empty | Groups before users | Next: admin folder tree | Done |
| 2026-08-26 | Logesh P S | Files | Started Firm/ folder tree under saraswathi.admin | Runbook 6.3 structure | Delete empty folders if unused | In progress |
| 2026-08-26 | Logesh P S | Files | Firm/ plus 7 children scanned; 8 folders 0 errors | Runbook 6.3 | Share after users exist | Done |
| 2026-08-26 | Logesh P S | Apps | Started LibreSign enable | Feature B13 PDF signing | Disable libresign if unused | In progress |
| 2026-08-26 | Logesh P S | Apps | libresign 14.1.0 enabled; /apps/libresign/ 401 unauthenticated | Feature B13 | Need configure:check before install | In progress |
| 2026-08-26 | Logesh P S | Apps | LibreSign check: java/jsignpdf/pdftk/openssl missing; imagick OK | Need occ install + openssl configure | Uninstall binaries if unused | In progress |
| 2026-08-26 | Logesh P S | Apps | LibreSign tools all success: Java 21, JSignPdf 2.3.0, PDFtk 3.3.3, poppler, openssl CA | Feature B13 runtime | Uninstall via libresign:uninstall if unused | Done |
| 2026-08-26 | Logesh P S | Apps | Started Time Manager enable | Quotation groupware extra | Disable timemanager if unused | In progress |
| 2026-08-26 | Logesh P S | Apps | timemanager 0.3.25 enabled; anonymous HEAD /apps/timemanager/ HTTP 500 | Need exception class from nextcloud.log | Disable only if logged-in use also 500 | In progress |
| 2026-08-26 | Logesh P S | Apps | Time Manager guest 500 = null userId in PageController.php:135; app kept | Quotation extra enable complete | Disable if logged-in use also 500 | Done |
| 2026-08-26 | Logesh P S | Apps | Started Talk (`spreed`) confirm; no HPB | Quotation Talk chat/video | Do not install signaling server | In progress |
| 2026-08-26 | Logesh P S | Apps | spreed 24.0.4; /apps/spreed/ 303; signaling_servers unset | Quotation Talk without HPB | Do not install signaling server | Done |
| 2026-08-26 | Logesh P S | Backup | Started RDS backup + EBS snapshot confirm | Phase 6 resilience; no AWS Backup vault yet | Delete unused manual snapshot only | In progress |
| 2026-08-26 | Logesh P S | Backup | RDS automated backups Enabled 7 days; two automated snapshots Available | Metadata restore path | Do not disable backups or deletion protection | Done |
| 2026-08-26 | Logesh P S | Backup | Created EBS snap-0a1d21b760e5e6bf6 from vol-0063c19bdcb7583bf | App disk + Nextcloud data | Delete unused manual snapshot only | In progress |
| 2026-08-26 | Logesh P S | Backup | EBS snap-0a1d21b760e5e6bf6 Completed 100% encrypted saraswathi-ebs | App disk + Nextcloud data | Delete unused manual snapshot only | Done |
| 2026-08-26 | Logesh P S | Billing | Saraswathi-Monthly-AWS-Budget $40; duplicate Budget_2 $50 created | Cost alert | Delete Budget_2; keep one | In progress |
| 2026-08-26 | Logesh P S | Billing | Deleted Budget_2; remaining Saraswathi-Monthly-AWS-Budget $60 Healthy $9.44 MTD | Single monthly cost ceiling | Edit amount only; do not create a third | Done |
| 2026-08-26 | Logesh P S | Monitoring | Started CloudWatch default-metric alarms (no agent) | Phase 6 ops after budget | Delete unused alarms/topic | In progress |
| 2026-08-26 | Logesh P S | Monitoring | SNS saraswathi-ops-alerts EMAIL subscription Confirmed | Alarm destination | Unsubscribe if unused | Done |
| 2026-08-26 | Logesh P S | Monitoring | Created alarm saraswathi-ec2-status-check-failed (>=1, 2 of 2) | EC2 instance health | Delete unused alarm | In progress |
| 2026-08-26 | Logesh P S | Monitoring | Created alarm saraswathi-ec2-cpu-high (>85, 3 of 3); status-check now OK | EC2 CPU | Delete unused alarm | In progress |
| 2026-08-26 | Logesh P S | Monitoring | Created alarm saraswathi-rds-free-storage-low; three default-metric alarms exist | Phase 6 default metrics | Delete unused alarms | Done |
| 2026-08-26 | Logesh P S | Monitoring | Started CloudWatch agent mem/disk (no NAT) | Guest metrics after default alarms | Remove agent + detach CW policy | In progress |
| 2026-08-26 | Logesh P S | Monitoring | amazon-cloudwatch-agent 1.300071 running configured on i-002509b77963fd5fc | mem_used_percent + disk / | Stop service; dpkg -r if unused | In progress |
| 2026-08-26 | Logesh P S | IAM | Attached CloudWatchAgentServerPolicy to saraswathi-ec2-ssm | Agent PutMetricData | Detach policy if unused | Done |
| 2026-08-26 | Logesh P S | Monitoring | Created saraswathi-ec2-mem-high OK and saraswathi-ec2-disk-high; five alarms exist | Guest mem/disk | Delete unused alarms | Done |
| 2026-08-26 | Logesh P S | Backup | Started AWS Backup vault + daily EBS plan | Phase 6 scheduled EBS | Delete unused plan/vault if empty | In progress |
| 2026-08-26 | Logesh P S | Backup | Created vault saraswathi-backup-vault KMS alias/saraswathi-ebs | Scheduled EBS target | Delete vault if unused and empty | In progress |
| 2026-08-26 | Logesh P S | Backup | Plan saraswathi-ebs-daily daily-ebs-7d; assigned vol-0063c19bdcb7583bf | Scheduled EBS 7d | Delete plan if unused | Done |
| 2026-08-26 | Logesh P S | Backup | Started on-demand EBS backup into saraswathi-backup-vault | Prove recovery point before 12:30 | Cancel job if wrong volume | In progress |
| 2026-08-26 | Logesh P S | Backup | On-demand job Completed into Default vault (vol-0063c19bdcb7583bf snap-07664ef633cc92904) | Wrong vault | Leave Default copy; redo into firm vault | In progress |
| 2026-08-26 | Logesh P S | Backup | On-demand Completed into saraswathi-backup-vault snap-0877c1316d9702f73 | Firm vault recovery point | Do not restore; do not FSR | Done |
| 2026-08-26 | Logesh P S | App | Started versions + trashbin confirm | Phase 6 Nextcloud safety nets | Disable apps only if unused | In progress |
| 2026-08-26 | Logesh P S | App | files_versions and files_trashbin not in enabled list; retention unset | Need occ app:enable | Disable if unused | In progress |
| 2026-08-26 | Logesh P S | App | Enabled files_versions 1.27.0 and files_trashbin 1.24.0 | Phase 6 user restore path | occ app:disable if unused | Done |
| 2026-08-26 | Logesh P S | Storage | Started S3 versioning confirm (no upload) | Phase 6 object safety net | Do not fill 150 GB | In progress |
| 2026-08-26 | Logesh P S | Storage | Confirmed files bucket versioning Enabled SSE-S3 | Object version safety | Do not fill 150 GB | Done |
| 2026-08-26 | Logesh P S | App | Started Activity app confirm | Phase 6 audit events | Disable activity if unused | In progress |
| 2026-08-26 | Logesh P S | App | Confirmed activity 7.0.0 already enabled | File/share events in UI | occ app:disable if unused | Done |
| 2026-08-26 | Logesh P S | App | Started admin_audit enable | Phase 6 admin audit log | Disable admin_audit if unused | In progress |
| 2026-08-26 | Logesh P S | App | Enabled admin_audit 1.24.0; logfile unset (default) | Admin/file audit in NC log | occ app:disable if unused | Done |
| 2026-08-26 | Logesh P S | Audit | Started CloudTrail S3 data events on files bucket | Phase 6 object API audit | Remove data-event selector if unused | In progress |
| 2026-08-26 | Logesh P S | Audit | Data events S3 (2): files bucket + all current/future buckets | Extra cost | Remove all-buckets row | In progress |
| 2026-08-26 | Logesh P S | Audit | Files-bucket data events Enabled; all-buckets unchecked (UI row remains) | Object API audit one bucket | Edit selectors if all-buckets becomes Enabled | Done |
| 2026-08-26 | Logesh P S | Audit | Started CloudTrail log file validation | Integrity of trail logs | Turn validation off if unused | In progress |
| 2026-08-26 | Logesh P S | Audit | Enabled log file validation on Saraswathi-management-trail | Trail integrity | Turn validation off if unused | Done |
| 2026-08-26 | Logesh P S | Audit | Started CloudTrail tags | Cost allocation consistency | Remove tags if unused | In progress |
| 2026-08-26 | Logesh P S | Audit | Tagged Saraswathi-management-trail Project/Owner/Environment | Cost allocation consistency | Remove tags if unused | Done |
| 2026-08-26 | Logesh P S | Backup | Started backup vault tags | Vault had 0 tags | Remove tags if unused | In progress |
| 2026-08-26 | Logesh P S | Backup | Vault tags Project + Environment; Owner missing | Partial cost tags | Add Owner=Saraswathi | In progress |
| 2026-08-26 | Logesh P S | Backup | Tagged saraswathi-backup-vault Project/Owner/Environment | Cost allocation consistency | Remove tags if unused | Done |
| 2026-08-26 | Logesh P S | Monitoring | Started five-alarm state confirm | Disk was Insufficient data | Do not delete alarms | In progress |
| 2026-08-26 | Logesh P S | Monitoring | Five alarms all OK (disk no longer Insufficient data) | Phase 6 monitoring live | Delete unused alarms | Done |
| 2026-08-26 | Logesh P S | Audit | Started CloudTrail digest confirm | First validation was `-` | Do not Stop logging | In progress |
| 2026-08-26 | Logesh P S | Audit | Validation digest delivered 2026-08-26 20:22 IST | Trail integrity live | Turn validation off if unused | Done |
| 2026-08-26 | Logesh P S | Audit | Trail tags Project + Environment; Owner missing | Console showed Tags (2) | Add Owner=Saraswathi | In progress |
| 2026-08-26 | Logesh P S | Audit | Stopped tag follow-up (not required) | Operator: do not mention tags | Leave existing tags as-is | Done |
| 2026-08-26 | Logesh P S | App | Started occ status + setupchecks refresh | Confirm stack after Phase 6 apps | Do not paste config.php | In progress |
| 2026-08-26 | Logesh P S | App | setupchecks refresh: 34.0.3.2 healthy; Talk HPB/email expected | Post Phase 6 health | Do not enable HPB/SMTP | Done |
| 2026-08-26 | Logesh P S | App | Started redacted Nextcloud log error classify | 8 errors since 2026-08-19 | Do not dump secrets | In progress |
| 2026-08-26 | Logesh P S | App | Classified 8 errors by app/class (need 80-char msgs) | DB/Office/LibreSign/TypeError | Do not dump stacks | In progress |
| 2026-08-26 | Logesh P S | App | 8 errors leftover/known (Office URL, TM guest, empty LibreSign) | No live outage | Do not vendor-patch | Done |
| 2026-08-26 | Logesh P S | App | Started LibreSign background-job list | Empty SignFileJob in log | Do not delete jobs yet | In progress |
| 2026-08-26 | Logesh P S | App | LibreSign Reminder + CRL cache jobs present (list truncated) | Normal scheduled jobs | Do not delete | In progress |
| 2026-08-26 | Logesh P S | App | SIGN_JOBS:0 — no LibreSign SignFile jobs queued | Empty-arg errors leftover | Do not delete Reminder/CRL | Done |
| 2026-08-26 | Logesh P S | App | Started admin-only trash restore drill | Phase 6 user restore path | Restore/delete only the drill file | In progress |
| 2026-08-26 | Logesh P S | App | Restored _restore-drill.txt from Deleted files | Phase 6 trash path proven | Delete only the drill file | Done |
| 2026-08-26 | Logesh P S | App | Started versions restore on _restore-drill.txt | Phase 6 version sidebar | Restore only the drill file | In progress |
| 2026-08-26 | Logesh P S | App | Versions restore working on _restore-drill.txt | Phase 6 version path proven | Delete only the drill file | Done |
| 2026-08-26 | Logesh P S | App | Started Phase 6 batch (Activity + admin_audit + leave drill file) | Token-saving multi-step | Do not create users/SMTP | In progress |
| 2026-08-26 | Logesh P S | App | Activity working; four restore/audit apps enabled; logfile unset | Phase 6 UI/audit | Do not dump audit.log | Done |
| 2026-08-26 | Logesh P S | Docs | Added DR runbook (no prod restore) | Phase 6 exit | Edit if restore policy changes | Done |
| 2026-08-26 | Logesh P S | Ops | Started read-only budget + backup + RDS confirm | Phase 6 close-out | Do not create resources | In progress |
| 2026-08-26 | Logesh P S | Ops | Budget $60 Healthy $9.44 MTD; daily-ebs-7d 12:30 IST 7d | Close-out D+E | Do not create budget/plan | Done |
| 2026-08-26 | Logesh P S | Ops | RDS paste was service dashboard not instance backup | Need F on saraswathi-nextcloud-db | Do not restore | In progress |
| 2026-08-26 | Logesh P S | Ops | RDS automated backups Enabled 7d; 2 automated snaps Available | Phase 6 close-out F | Do not restore; do not Apply OS | Done |
| 2026-08-26 | Logesh P S | Project | Phase 6 AWS/app safety nets closed (no extra users/SMTP) | Exit: drills + monitoring + DR note | Reopen only if asked | Done |
| 2026-08-26 | Logesh P S | UAT | Started Phase 7 admin-only Files/Office batch | Extra users still deferred | Delete only _uat* objects | In progress |
| 2026-08-26 | Logesh P S | UAT | Admin UAT G/I/J/K working; H comment path pending | Folder/Office/ZIP/view | Comment via Files sidebar | In progress |
| 2026-08-26 | Logesh P S | UAT | H comment yes; Phase 7 G–K complete | Admin Files/Office UAT | Leave _uat* / drill file | Done |
| 2026-08-26 | Logesh P S | UAT | Started Phase 7 batch 2 (copy/move, preview, PDF, calendar, Deck) | Extra users deferred | Delete only _uat* | In progress |
| 2026-08-26 | Logesh P S | UAT | L–O working; Deck board clicks pending | Copy/preview/LibreSign/calendar | Leave _uat* | In progress |
| 2026-08-26 | Logesh P S | UAT | P Deck yes; Phase 7 L–P complete | Board/stack/card | Leave _uat-board | Done |
| 2026-08-26 | Logesh P S | UAT | Started Phase 7 batch 3 (contacts, tasks, Talk, tags, search) | Extra users deferred | Leave _uat* | In progress |
| 2026-08-26 | Logesh P S | UAT | Phase 7 Q–U complete (contact/task/Talk/tag/search) | Admin groupware + files | Leave _uat* | Done |
| 2026-08-26 | Logesh P S | UAT | Started Phase 7 batch 4 (xlsx, PDF export, Deck extras, TM, sort/activity) | Extra users deferred | Leave _uat* | In progress |
| 2026-08-26 | Logesh P S | UAT | Phase 7 V–Z complete; B8 Save-as-PDF yes, File-Export-PDF no | Collabora export known fail | Leave _uat* | Done |
| 2026-08-26 | Logesh P S | UAT | Started Phase 7 batch 5 (pptx, metadata, lock, recurring, save-as ODT) | Extra users deferred | Leave _uat* | In progress |
| 2026-08-30 | Logesh P S | Plan | From-now-to-end plan: 132 GB waits on S3/disk cutover; UAT before bulk | Quotation still 150 GB | Do not upload 132 GB | Done |
| 2026-08-30 | Logesh P S | Plan | Click-by-click runbooks T1–U6 in 04-from-now-runbooks | Through Phase U | Ask only on failure | Done |
| 2026-09-03 | Logesh P S | Migration | rclone source proven F:\f ~167860 files / 123.5 GiB; remote Backup_data/DATA1 (not DATA!) | Desktop client too slow / SAVEPOINT; S3 folder path | Do not recopy E:/F:; do not rclone sync | Done |
| 2026-09-09 | Logesh P S | Migration | HP reboot LastBootUpTime 03:40:48 IST (Windows Update); rclone window died — not finished | Resume same copy to DATA1 | Do not treat reboot as complete | Done |
| 2026-09-12 | Logesh P S | Migration | rclone copy F:\f → nextcloud:Backup_data/DATA1 leftover 2.377 GiB / 8766 files / 19h7m 0 Errors | Finish ingest | Do not recopy; laptop may off | Done |
| 2026-09-12 | Logesh P S | Migration | rclone check --one-way 00:37:47: 0 differences, 167861 matching files, 56 hashes unchecked (WebDAV) | Prove complete vs Explorer 1,67,861 | Do not recopy | Done |
| 2026-09-12 | Logesh P S | Billing | Sep 1–10 MTD ~$85.10; S3 ~$47 + CloudTrail ~$14 from ingest APIs + data events; t3.medium ~$9.78; no NAT | Cost after rclone | Do not stop EC2; pay ₹900.39 past due | In progress |
| 2026-09-12 | Logesh P S | Audit | CloudTrail S3 data events off; trail Saraswathi-management-trail still Logging; management events All; validation Enabled | Stop data-event cost after ingest | Do not Delete/Stop logging; do not Save empty Data-events Edit (re-enables) | Done |
| 2026-09-12 | Logesh P S | Identity | Instructed 8 staff (6 Firm-Seniors / 2 Firm-Juniors) quota 5 GB not admin; unique passwords | Demo users | Shared password in chat burned; do not log secrets | In progress |
| 2026-09-12 | Logesh P S | Apps | Deck board Firm_Work exists; lists empty — To do / Waiting client / Doing / Partner review / Done + share groups | Training | Do not create second board unless asked | In progress |
| 2026-11-02 | Logesh P S | Billing | Oct 2026 bill $82.77 ($70.14 + 18% GST); Sep credits $120.39 exhausted; read-only review: EC2 CPU avg 2.6%, mem peak 60%, RDS CPU 4.5% | Bill above $60 budget | n/a (read-only) | Done |
| 2026-11-02 | Logesh P S | Backup | Pre-change EBS snapshot snap-006094f30c8419f2a + /root/config.php.before-t3a-202611021254 | Safety before resize | Restore snapshot to new volume | Done |
| 2026-11-02 | Logesh P S | Network | Elastic IP 13.234.211.7 (eipalloc-0cb0b191a0994190f) associated to i-002509b77963fd5fc; old auto IP 3.111.213.217 released | Fixed IP across stop/start | Disassociate EIP (IP will change) | Done |
| 2026-11-02 | Logesh P S | DNS / TLS | Route 53 files.t-saraswathi.in A → 13.234.211.7 (C10319213ESNLUUVEI11Q INSYNC) | Follow EIP | UPSERT A to new IP | Done |
| 2026-11-02 | Logesh P S | Apps | Office wopi_allowlist = 127.0.0.1,::1,10.20.1.144,13.234.211.7 | New public IP | Re-add old IP only if EIP removed | Done |
| 2026-11-02 | Logesh P S | Backup | Deleted manual EBS snap-0a1d21b760e5e6bf6 (Aug); daily AWS Backup 7d kept | Cost cleanup | Not recoverable; daily backups remain | Done |
| 2026-11-02 | Logesh P S | Compute | EC2 t3.medium → t3a.medium (stop/modify/start ~47 s 18:34 IST); all services, DB, S3 mount, Office, cron verified | ~45% cheaper, same 2 vCPU / 4 GiB | Stop → t3.medium → start | Done |
| 2026-11-02 | Logesh P S | Billing | 1-yr EC2 Instance Savings Plan t3a ap-south-1 No Upfront $0.0155/hr (358b5613-3e8e-4db9-b9b5-92acf54ea648) to 2027-11-02 | Commit 24×7 compute | Non-cancellable after 7 days | Done |
| 2026-11-02 | Logesh P S | Billing | 1-yr RDS RI db.t4g.micro MySQL Single-AZ No Upfront $0.017/hr (saraswathi-nextcloud-db-ri-1yr) | Commit 24×7 DB | Non-cancellable | In progress (payment-pending → active) |
| 2026-11-02 | Logesh P S | Docs | Updated docs to EIP 13.234.211.7 / t3a.medium; detail in SESSION_2026-11-02_COST_OPTIMISATION.md | Keep records current | git revert | Done |
| 2026-11-02 | Logesh P S | Billing | RDS RI saraswathi-nextcloud-db-ri-1yr status **payment-failed** (23:29 IST); not charged; RDS stays on-demand. Savings Plan 358b5613 still active | AISPL payment issue (past-due/unpaid invoices or card) | Pay invoices + valid default card, then re-buy RI with new ID | Blocked (payment) |
