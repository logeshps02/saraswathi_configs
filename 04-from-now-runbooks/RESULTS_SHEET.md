# Results sheet — fill as you go (no passwords)

Copy each **Paste / record** block from the runbook files under the matching heading. Date every line.

## T1 batch 5

```
T1 AA slides reopen: pass
T1 AB save-as format: pass
T1 AC details size/date: pass
T1 AD lock: locked and unlocked , icon showing , but able to open file even locked
T1 AE recurring: pass
```

## T2 optional

```
T2 AF print: pass 
T2 AG doc comment: pass 
T2 AH track changes: **no track-changes**.
T2 AI vCard: Pass
T2 AJ task due+priority:pass 
T2 AK TM hours:pass
T2 AL talk extras: pass
T2 AM theme: pass
T2 AN overview warnings:
Keyboard navigation help
Skip to app navigation
Skip to main content
 
Overview
Security & setup warnings
It is important for the security and performance of your instance that everything is configured correctly. To help you with that we are doing some automatic checks. Please see the linked documentation for more information.

There are some errors regarding your setup.

High-performance backend
No High-performance backend configured - Running Nextcloud Talk without the High-performance backend only scales for very small calls (max. 2-3 participants). Please set up the High-performance backend to ensure calls with multiple participants work seamlessly.
Errors in the log
10 errors in the logs since 24 August 2026, 11:58:05
PHP getenv
PHP does not seem to be setup properly to query system environment variables. The test with getenv("PATH") only returns an empty response.
PHP opcache
The PHP OPcache module is not properly configured. The OPcache interned strings buffer is nearly full. To assure that repeating strings can be effectively cached, it is recommended to apply "opcache.interned_strings_buffer" to your PHP configuration with a value higher than "8"..
Client Push
Client Push is not installed. This may lead to delayed Talk notifications.
AppAPI deploy daemon
AppAPI default deploy daemon is not set. Please register a default deploy daemon in the settings to install External Apps (Ex-Apps).
Java
Non-UTF-8 encoding detected: ANSI_X3.4-1968. This may cause issues with accented or special characters
Second factor configuration
Second factor providers are available but two-factor authentication is not enforced.
Email test
You have not set or verified your email server configuration, yet. Please head over to the "Basic settings" in order to set them. Afterwards, use the "Send email" button below the form to verify your settings.
Configuration server ID
Server identifier isn’t configured. It is recommended if your Nextcloud instance is running on several PHP servers. Add a server ID in your configuration.
PHP Imagick module
The PHP module "imagick" in this instance has no SVG support. For better compatibility it is recommended to install it.
Please double check the installation guides ↗, and check for any errors or warnings in the log ↗.

Check the security of your Nextcloud over our security scan ↗.

Version
Nextcloud Hub 26 Spring (34.0.3)

Update
Your version is up to date.
Update channel
Changing the update channel also affects the apps management page. E.g. after switching to the beta channel, beta app updates will be offered to you in the apps management page.
Current update channel:

Stable
You can always update to a newer version, but you can never downgrade to a more stable version.
Note that after a new release the update only shows up after the first minor release or later. We roll out new versions spread out over time and sometimes skip a version when issues are found. Learn more about updates and release channels at https://nextcloud.com/release-channels/

Notify members of the following groups about available updates:
admin
```

## M0

```
M0 path: F:\
M0 size / files / folders: 1,79,790 Files, 41,067 Folders 132 GB (1,42,45,38,08,623 bytes)
PS C:\Users\HP>
PS C:\Users\HP>
>> $root = 'F:\Final'
>> $files = Get-ChildItem $root -Recurse -File -Force -ErrorAction SilentlyContinue
>> $dirs  = Get-ChildItem $root -Recurse -Directory -Force -ErrorAction SilentlyContinue
>> 'files=' + $files.Count
>> 'dirs=' + $dirs.Count
>> 'bytes=' + ($files | Measure-Object Length -Sum).Sum
files=179163
dirs=41028
bytes=142084376166
PS C:\Users\HP>


M0 target NC folder:Firm/Backup_data
M0 option: S
```

## M1A (if S)

```
j

give steps for:
### 0.3 Snapshot before change


M1A HEAD_BUCKET: 0
s s3api head-bucket --bucket saraswathi-nextcloud-files-055855670388 --region ap-south-1 ; echo HEAD_BUCKET:$?
{
    "BucketArn": "arn:aws:s3:::saraswathi-nextcloud-files-055855670388",
    "BucketRegion": "ap-south-1",
    "AccessPointAlias": false
}
HEAD_BUCKET:0
$
$ echo uat-s3-probe | aws s3 cp - s3://saraswathi-nextcloud-files-055855670388/uat-s3-probe.txt --region ap-south-1 ; aws s3 rm s3://saraswathi-nextcloud-files-055855670388/uat-s3-probe.txt --region ap-south-1 ; echo S3_PROBE:$?
delete: s3://saraswathi-nextcloud-files-055855670388/uat-s3-probe.txt
S3_PROBE:0
$
M1A objectstore enabled: 
$
$ sudo -u www-data php /var/www/nextcloud/occ config:list system --private 2>/dev/null | grep -E 'objectstore|datadirectory|instanceid' ; echo OCC_LIST:$?
        "datadirectory": "\/opt\/nextcloud\/data",
        "instanceid": "ocsfrsgd38gw",
OCC_LIST:0
$ ^C
$
M1A _uat-s3.txt:
M1A vault 2026-08-31: saraswathi-backup-vault; 6 EBS recovery points; latest snap-0f2a86657a62ff29d Completed 00:30 IST vol-0063c19bdcb7583bf retain 7d; lock none. Snapshot gate PASS. Do not Restore. Objectstore NOT enabled (existing-instance block).
M1A IAM instance role saraswathi-ec2-ssm: yes (operator 2026-08-31)
M1A inline policy saraswathi-nextcloud-s3 List/Get/Put/Delete this bucket only: yes
M1A objectstore: SKIP on existing install (would hide local files). Grow EBS cancelled. Next = S3 folder Backup_data (files 18–20).
```

## M1B (if E) — cancelled

```
M1B STOP 2026-08-31: do not grow 30 GiB → 200 GiB. Not in quotation. Extra EBS + 7-day snapshots would blow ~$60 / ₹5,000 RI plan. 150 GB stays S3 (~₹320/mo quoted). Objectstore toggle still blocked on existing install. Next = S3 folder (external) for Backup_data, not bigger disk.
M1B volume GiB: leave 30
M1B Avail > 132G: no — by design; bulk data not on EBS
```

## Optional UAT delete

```
UAT deleted from Files: 
Firm seven folders still there:
```

## M1S3-A enable app

```
M1S3-A External storage app:  enableed
M1S3-A Administration External storage page opens: opens
```

## M1S3-B mount

```
M1S3-B first try 2026-08-31: red — “bucket will not be created because the name is not dns compatible” (Nextcloud failed HeadBucket then tried create; do not rename bucket)
M1S3-B second try hostname+region+path-style: still same red (operator)
M1S3-B folder name: Backup_data
M1S3-B hostname: s3.ap-south-1.amazonaws.com
M1S3-B region: ap-south-1
M1S3-B path style: on
M1S3-B auth: None
M1S3-B row icon: red — next = 21 occ mount
M1S3-B Files shows Backup_data: no
M1S3-B2 red row deleted: 
M1S3-B2 HEADWWW: 0
M1S3-B2 list: Mount ID 1 /Backup_data already exists; auth None; hostname s3.ap-south-1.amazonaws.com; use_path_style true
M1S3-B2 create skipped: builtin::builtin not valid; do not create second mount
M1S3-B2 N-literal commands failed as expected (must use 1)
M1S3-B2 region in list had U+200B zero-width spaces around ap-south-1
M1S3-B2 config with extra word set: Too many arguments (NC 34 is config ID KEY VALUE)
M1S3-B2 verify still error: bucket name in message also has U+200B — rewrite bucket+region without set
M1S3-B2 config rewrite (no set): FEBUCKET:0 FEREGION:0 FEHOST:0 FEPATH:0 FEVERIFYOFF:0
M1S3-B2 get bucket: saraswathi-nextcloud-files-055855670388
M1S3-B2 get region: ap-south-1
M1S3-B2 create auth used: None (existing)
M1S3-B2 mount ID: 1
M1S3-B2 files_external:verify: status ok code 0 FEOK:0 (2026-08-31)
M1S3-B2 Files shows Backup_data: yes (operator 2026-08-31)
```

## M1S3-C proof

```
M1S3-C create _s3-proof.txt in Backup_data: yes (operator all working 2026-08-31)
M1S3-C download matches s3-ok: yes (operator)
M1S3-C object visible in S3 console or aws s3 ls: yes S3LS:0; ls showed sample.docx 7965 bytes 2026-08-31
M1S3-C df still ~30G: yes Size 29G Used 7.7G Avail 21G 28% DFDATA:0
```

## M1C

```
M1C php 512M / 3600 / Kolkata: yes sizes 512M and Asia/Kolkata; CLI max_execution_time 0 (unlimited) not 3600 — upload still worked
M1C php8.3-fpm active: yes
M1C nginx client_max_body_size: 512M (line 19)
M1C nginx -t: 0 (wasm duplicate warn only)
M1C small browser upload into Backup_data: yes (operator)
M1C df still ~30G (bulk is S3): yes 29G / 7.7G used / 21G avail DFDATA:0
```

## M2

```
M2 client + structure: pass (operator 2026-09-01)
M2 office + Save-as PDF: DOCX/office open; Save-as PDF option not there; File→Export PDF not working (same known Collabora limit as T1)
M2 search + trash: pass, WebDAV skipped
```

## M3

```
M3 Up to date: pass (operator earlier)
M3 failures count: pass
M3 10 spot-checks: pass
M3 extra sync Backup_data/Data: SAVEPOINT DOCTRINE_2 repeating (2026-09-02). OCC 34.0.3 installed, disk 29G 8.7G used 31%, nginx/php/redis active. Not Too many connections. Pause then resume slower (one folder or upload cap). Do not grow EBS / Apply RDS OS.
M3 rclone (HP F:\f → Backup_data/DATA1) COMPLETE 2026-09-12: leftover copy 2.377 GiB / 8766 files / 19h7m 0 Errors. check --one-way 00:37:47: 0 differences, 167861 matching files, Checks 167861/167861, Listed 409498, 56 hashes unchecked (WebDAV not missing), Transferred 0 B, 9h22m. Explorer 1,67,861. Do not recopy. Laptop may off. Do not desktop full sync. Do not rclone sync.
```

## U1

```
U1 extra user login: pass
U1 user count:pass
```

## U2

```
U2 partner write Templates:  pass
U2 trainee cannot see Partners:pass
```

## U3

```
U3 skipped / password+revoke: pass (operator)
U3 share email: none — SMTP not configured (T2 Email test); U4 next
U3 S3 Backup_data share permissions: missing until Enable sharing on mount 1
U3 expiry stuck on current date: date picker min=today; set default 7 days if still stuck
```

## U4

```
U4 outbound 587 test: 0 (2026-09-02 SSM)
U4 SES identity t-saraswathi.in: Verified (2026-09-02)
U4 provider: SES
U4 SMTP IAM credentials: created then **rotated** (pair was pasted in chat — do not use)
U4 send-test: yes (2026-09-02). Domain ZWSP cleared (DOMLEN 15); mail_smtpsecure tls.
U4 SES Email identity (admin To): Verified (2026-09-02)
U4 system mail: host SES Mumbai, port 587, mode smtp, from local noreply, domain t-saraswathi.in DOMLEN 15 DOMOK. mail_smtpsecure tls.
U4 occ config:app:get core mail_*: all exit 1 (wrong store; system get used).
U4 NC send-test: yes
U4 SES production: requested (case SES: Production Access, ap-south-1, TRANSACTIONAL). Follow-up reply sent 2026-09-02. Waiting AWS (up to 24h; may take longer). Do not log Opened-by mailbox.
U4 share mail to partner: after production Enabled
U4 calendar email reminder:
```

## U5

```
U5 partner selective sync: pass
U5 WebDAV: skip (WinSCP 405; desktop client already pass). Do not change nginx.
U5 Android/iOS: skip unless a phone is on hand
```

## U6

```
U6-A share overview: yes
U6-A @mention: yes
U6-A notification prefs: yes
U6-B co-author: pass
U6-C deck/calendar/talk: pass
U6-D impersonate: pass
U6-E activity: pass
U6-F LibreSign sample: pass (sample only; not production MCA)
Phase U files/UAT: Done 2026-09-02. Wait-only: SES production case. Optional later: share mail after Enabled; Enable sharing on Backup_data if staff must share S3. 
```
