# Optional — delete UAT test objects only

**Who:** `saraswathi.admin` at https://files.t-saraswathi.in  
**When:** Before S3 mount, or skip.  
**Do not:** delete `Firm` or its seven children. Do not empty trash until you confirm names. Do not delete production data (there is none yet except tests).

## 1. Files to remove (tests)

In **home** and **Firm/Templates** (and Deck/Calendar/Talk if you want):

**Files / folders**

- `_restore-drill.txt`
- `_uat-office` and any `.odt` / `.pdf` save-as copies
- `_uat-sheet`
- `_uat-slides`
- `_uat-s3.txt` if present
- `_uat-up-small.bin` if present
- `Firm/Templates/_uat-depth` (and nested `_uat-sub`)
- `Firm/Templates/_pilot` if you already made it
- copies like `_partner-write.txt` if any

**Apps (optional)**

- Calendar: `_uat-event` / `_uat-recur`
- Contacts: `_uat-contact`
- Tasks: `_uat-task`
- Deck: board `_uat-board`
- Talk: room `_uat-room`
- Time Manager: `_uat-client`

## 2. How to delete a file

1. Files → find the row.
2. **⋯** → **Delete**.
3. Repeat. Do not **Delete permanently** yet.

## 3. Empty trash (optional)

1. Left: **Deleted files**.
2. Confirm only `_uat-*` / drill names.
3. **Empty trash** / delete selected.

## 4. Verify

1. Files home: no `_restore-drill.txt`.
2. Firm/Templates: no `_uat-*`.
3. Firm still has Partners, Administration, Clients, Statutory, Templates, Trainee-Workspace, Archive.

## Paste / record

```
UAT deleted from Files: yes/skip
Firm seven folders still there: yes/no
```

Next: [18_M1S3_ENABLE_EXTERNAL.md](18_M1S3_ENABLE_EXTERNAL.md)
