# From Home — Phase 7 admin-only UAT (one paste)

Phase 6 is **closed**. Extra users, SMTP, Talk HPB, S3 objectstore, and 150 GB stay **later**.

Do **G–K** as `saraswathi.admin` at `https://files.t-saraswathi.in`. One reply at the end. Do **not** create other users. Do **not** share to groups. Do **not** Apply the RDS OS update.

## G. Folder depth (A1)

1. Files → **Firm** → **Templates**.
2. New folder `_uat-depth` → inside it `_uat-sub` → inside that `_uat-sub2`.
3. Confirm three nested folders exist.

## H. Star + comment (A10 / A11)

1. Stay in **Files** (do not open the text editor).
2. Click the **row** of `_restore-drill.txt` once (or the **…** menu on that file).
3. Open the **right sidebar**: **Details** / info **i** icon (top-right of Files).
4. Star: click the **star** on the file or in the sidebar (Favourites).
5. Comment: in the sidebar click **Comments** (speech-bubble). Type `uat-comment`. Press **Enter** or the send arrow.
6. Confirm the comment appears under the file.

If there is no Comments tab: sidebar → **Activity** is not the same thing. Need the **Comments** tab. Do not install a new app this step.

## I. New Office file (B1)

1. **Firm/Templates** → **New** → Document named `_uat-office`.
2. Type `uat-office` → Save / close.
3. Re-open and confirm the text is there.

If New Document fails: paste the error text only. Do not install Docker Collabora.

## J. ZIP download (A5)

1. Select **Firm/Templates** (or `_uat-depth`).
2. **Download**.
3. Confirm a zip downloads.

## K. Grid / list (A18)

1. Toggle Files view between **grid** and **list** once.
2. Confirm both work.

## Paste once

- G nested folders yes/no
- H star + comment yes/no
- I Office new + reopen yes/no (or error)
- J zip downloaded yes/no
- K grid/list yes/no

### Observed (2026-08-26)

| Item | Result |
|---|---|
| G nested folders | **working** |
| I Office new + reopen | **working** |
| J ZIP | **working** |
| K grid/list | **working** |
| H comment | operator asked how — sidebar Comments tab |

### Confirmed H (2026-08-26)

H **yes** — star + Files sidebar comment `uat-comment` on `_restore-drill.txt`. G–K complete.

## Stop

First admin Files/Office batch is complete. Do not create users. Do not share folders. Do not Apply RDS OS. Next batch is `FROM_HOME_NEXT_STEP_PHASE7_ADMIN_UAT2.md`.
