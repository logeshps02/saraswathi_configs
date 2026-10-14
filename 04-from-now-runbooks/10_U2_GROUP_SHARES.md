# U2 — Share Firm tree with groups (C1 / C2 / K9)

**Who:** `saraswathi.admin` then one Partner and one Trainee in **private windows**
**When:** After U1 at least `partner1` and `trainee1` exist.
**Do not:** public links (U3). Do not share the entire 132 GB to Trainees unless CS says so. Do not paste share URLs with tokens into git.

Recommended matrix (change if CS wrote another):

| Folder                 | Firm-Partners | Firm-Seniors | Firm-Juniors | Firm-Trainees | Firm-Admins |
| ---------------------- | ------------- | ------------ | ------------ | ------------- | ----------- |
| Firm/Partners          | Edit          | View         | None         | None          | Edit        |
| Firm/Administration    | Edit          | View         | None         | None          | Edit        |
| Firm/Clients           | Edit          | Edit         | Edit         | View or None  | Edit        |
| Firm/Statutory         | Edit          | Edit         | View         | None          | Edit        |
| Firm/Templates         | Edit          | Edit         | Edit         | Edit          | Edit        |
| Firm/Trainee-Workspace | View          | View         | View         | Edit          | Edit        |
| Firm/Archive           | View          | View         | None         | None          | Edit        |

**View** = can download/preview, not delete. **Edit** = upload/edit. **None** = folder hidden.

If the UI only has “Allow editing” on/off: **on** = Edit, **off** = View.

---

## 1. Share one folder (example: Templates)

1. Login admin. Files → **Firm**.
2. **⋯** on **Templates** → **Share**.
3. Right sidebar **Sharing**.
4. Search box: type `Firm-Partners` (group, not a person).
5. Select the **group**.
6. Permissions: **Allow editing** **on** for Templates.
7. Repeat add: Firm-Seniors, Firm-Juniors, Firm-Trainees — editing on.
8. Do **not** tick “Share with link” here.
9. Confirm the four groups listed.

---

## 2. Repeat for other Firm children

Same clicks. Apply the matrix. Archive: Partners **edit off** (View). Trainee-Workspace: Trainees **edit on**; Partners **edit off** if they should only view.

**Clients:** if 132 GB landed under Clients, sharing **Clients** shares that tree. Confirm CS before Edit for Juniors.

---

## 3. Verify as Partner (C1/C2)

1. Private window. Login `partner1`.
2. Files: **Firm** or **Shared** / **Shares** in the left bar.
3. Open **Templates**. See `_uat-*` / `_pilot` (admin files).
4. **+** → New text file `_partner-write.txt` with `ok`.
5. Confirm it appears.
6. Try **Archive**: if View-only, upload should fail or **+** missing.
7. **Administration settings** must be absent.
8. Log out.

---

## 4. Verify as Trainee (negative test)

1. Private window. Login `trainee1`.
2. Must see **Trainee-Workspace** and **Templates** (if shared).
3. Must **not** see **Partners** / **Administration** if None.
4. In Trainee-Workspace: create `_trainee-write.txt`.
5. In Templates: if Edit, they can upload — CS may later switch Trainees to View.
6. Log out.

---

## 5. Instant revoke (C10) — on a **test** share only

1. Admin: share **Templates** also to a **user** `trainee1` extra if needed, or use a dummy folder `_uat-share-revoke`.
2. Create folder Firm/Templates/`_uat-share-revoke`. Share to `trainee1` Edit.
3. Trainee sees it.
4. Admin: Sharing → **X** on that share.
5. Trainee refresh: folder gone. 404/empty is pass.

Leave production group shares in place.

---

## 6. S3 / Backup_data — Share permissions missing

External storage **does not** use the same share ACL as `Firm/` until **Enable sharing** is on for that mount.

**Browser**

1. Administration settings → **External storage**.
2. Green row **Backup_data** (do not trash it).
3. Tick **Enable sharing** if present → **Save** / tick until green.
4. **Available for:** add **Firm-Partners** (etc.) if those groups must see the mount at all. Users not in Available for will not see Backup_data even if you “share” a file.
5. Files → Backup_data → **⋯ → Share** on a **subfolder** (prefer `_pilot` / a dummy, not the whole 132 GB). Allow editing on/off should appear.

**SSM (if the checkbox is missing)** — one line:

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:option 1 enable_sharing true ; echo FESHARE:$?
```

Then:

```sh
sudo -u www-data php /var/www/nextcloud/occ files_external:list ; echo FELIST:$?
```

Expect mount **1** still `/Backup_data`. Do not `create` a second mount. Do not type `N`.

**Limits (normal):** some S3 mounts still cannot set per-file **Can edit / Can share / Create** the way local `Firm/` can. Then: share **Firm** folders for office work; keep Backup_data as an archive visible via **Available for**. Do not copy 132 GB onto the 30 GB disk to “fix” sharing.

---

## 6. Notifications (N1, C9 in-app)

1. Partner: bell icon (top-right).
2. After admin shared Templates, an in-app notice **may** appear. If not, record **no bell** (SMTP not done). In-app is enough for this step.

---

## Paste / record

```
U2 matrix applied to 7 folders: yes
U2 partner sees Templates and can write: yes
U2 partner Archive view-only: yes 
U2 trainee cannot see Partners: yes
U2 trainee write Trainee-Workspace: yes
U2 revoke test: yes
U2 in-app share notice: no
```

Next: [11_U3_PUBLIC_LINKS.md](11_U3_PUBLIC_LINKS.md) only if CS allows public links. Else skip to [12_U4_SMTP.md](12_U4_SMTP.md) or [13_U5_DESKTOP_MOBILE_WEBDAV.md](13_U5_DESKTOP_MOBILE_WEBDAV.md).
