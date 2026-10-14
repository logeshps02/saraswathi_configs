# From Home — Next Step: Time Manager

LibreSign configure:check is all success. Enable **Time Manager** (quotation app list).

Use Session Manager. Paste each numbered block as **one line**.

Do **not** paste `config.php`.
Do **not** create extra users.

## 1. Enable Time Manager

App id is usually `timemanager`.

```sh
sudo -u www-data php /var/www/nextcloud/occ app:enable timemanager && sudo -u www-data php /var/www/nextcloud/occ app:list --enabled | grep -Ei 'time'
```

If `timemanager` is not found, paste the error only. Do not guess another id.

## 2. Confirm HTTPS surface

```sh
curl -sI https://files.t-saraswathi.in/apps/timemanager/ | head -n 6
```

Expected: not nginx 404 (401/302/200 OK). Do not paste Set-Cookie values.

**Observed 2026-08-25:** `timemanager 0.3.25 enabled`. Anonymous `HEAD /apps/timemanager/` → **HTTP 500** (not 401 like Deck). Cookie headers were pasted once — **do not paste Set-Cookie again**. Treat that session as exposed; log in again from the browser later. Do not store cookies in evidence.

Time Manager 0.3.25 is listed for Nextcloud 34. The page controller constructs with a user id and then reads locale; anonymous HEAD can 500 before a login redirect. Confirm with logs before disabling.

## 3. Exception class only (no cookies, no full log JSON)

```sh
sudo python3 -c "import json; p='/opt/nextcloud/data/nextcloud.log';
lines=open(p,encoding='utf-8',errors='replace').read().splitlines();
n=0
for line in reversed(lines):
    try: o=json.loads(line)
    except Exception: continue
    msg=str(o.get('message','')); ex=o.get('exception') or {}
    blob=(msg+' '+str(ex.get('class',''))+' '+str(ex.get('File',''))).lower()
    if 'timemanager' in blob or 'punic' in blob or 'getuservalue' in blob or 'getdateformat' in blob:
        print(o.get('level'), o.get('time'), ex.get('class') or o.get('app'), (ex.get('message') or msg)[:240]); print(ex.get('File'), ex.get('Line')); n+=1
        if n>=3: break
print('MATCHES', n)"
```

If MATCHES 0, run this (still no cookies):

```sh
sudo python3 -c "import json; p='/opt/nextcloud/data/nextcloud.log';
lines=open(p,encoding='utf-8',errors='replace').read().splitlines()[-80:];
n=0
for line in lines:
    try: o=json.loads(line)
    except Exception: continue
    if int(o.get('level',0) or 0)<3: continue
    ex=o.get('exception') or {}
    print(o.get('time'), ex.get('class') or o.get('app'), (ex.get('message') or o.get('message',''))[:240]); print(ex.get('File'), ex.get('Line')); n+=1
print('ERRS', n)"
```

## 4. Migrations still OK

```sh
sudo -u www-data php /var/www/nextcloud/occ migrations:status timemanager | head -n 20
```

## 5. Core still healthy

```sh
curl -sI https://files.t-saraswathi.in/status.php | head -n 5
```

Do not paste Set-Cookie. Do not dump `config.php` or the whole log file.

## 6. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| App | `timemanager` **0.3.25** enabled (NC 34 listed) |
| Anonymous HEAD `/apps/timemanager/` | HTTP 500 |
| Log | `AppConfig::getUserValue()` Argument #1 `$userId` must be string, **null** given |
| File | `/var/www/nextcloud/apps/timemanager/lib/Controller/PageController.php` line 135 |
| Decision | **Keep enabled.** Guest probe only. Open in browser after login as `saraswathi.admin`. Do not patch vendor PHP. |

## Stop

Do not create client time entries yet. Do not disable `timemanager`. Do not paste cookies.
