# Parallel sync (no recopy)

Unsorted dest is done. Copy stays on the laptop (`F:\f`). This step only **uploads** that tree.

The Nextcloud desktop client is mostly **one file at a time**. That is why a ~100k-file tree takes days. You can go faster with **a few disjoint jobs**, not with 20 parallel uploads.

## Hard stops

- Do **not** recopy from E:/F:.
- Do **not** grow EBS. Do **not** delete S3. Do **not** enable `objectstore`.
- Do **not** Remove the old Nextcloud pair. Pause it.
- Do **not** sync onto `/` home or `Firm/`.
- Remote = **new** folder `/Backup_data/Final_v2` (or whatever empty folder you already created).
- If CloudWatch disk ALARM or `SAVEPOINT DOCTRINE_2`: **Pause extra jobs**. Leave **one** running. Do not Apply RDS OS.

RDS is `db.t4g.micro`. More than ~4–8 file-creates at once often throws SAVEPOINT. Parallel here means **4 jobs × 4 transfers**, not unlimited.

## Fastest safe setup (rclone WebDAV)

1. Pause the desktop client pair (do not Remove).
2. Install rclone on the copy laptop if missing: https://rclone.org/downloads/
3. `rclone config` → New remote name `nextcloud`
   - Type: **WebDAV**
   - URL: `https://files.t-saraswathi.in/remote.php/dav/files/saraswathi.admin/`
   - Vendor: Nextcloud
   - User: `saraswathi.admin`
   - Pass: **app password** (Nextcloud security settings). Do not paste it in chat.
4. On that laptop:

```bat
python split_sync_batches.py --dest F:\f --jobs 4 --write-rclone
```

Use `D:\f` if that is the dest.

5. Confirm `05-migration\sync_batches\SYNC_BATCHES.txt` lists company folders only.
6. Browser: `/Backup_data/Final_v2` exists and is the intended target.
7. Upload (4 jobs, 4 file transfers each):

```bat
python run_parallel_rclone.py --dest F:\f --jobs 4
```

Dry-run first if you want:

```bat
python run_parallel_rclone.py --dest F:\f --jobs 4 --dry-run
```

Each job writes `F:\f\_SYNC_JOB_01.log` … `_04.log`.

One process instead of four (simpler, still parallel files):

```bat
rclone copy F:\f nextcloud:Backup_data/Final_v2 --transfers 8 --checkers 16 --fast-list --create-empty-src-dirs --exclude "~$*" --exclude "Thumbs.db" --exclude "desktop.ini" --exclude "*.tmp" --exclude "_COPY_*.csv" --exclude "_UNSORTED_REORG_LOG.csv" --exclude "_SYNC_JOB_*.log" --log-file F:\f\_SYNC_RCLONE.log --log-level INFO
```

Start with `--transfers 8`. If SAVEPOINT appears, drop to `--transfers 4` or use the 4-job bat and stop 3 of them.

`--dry-run` once if you want a count before real upload.

## Nextcloud client (if you stay on the desktop app)

Desktop **Network → parallel / multi-connection: 1–2**. Turning that up on one huge pair usually hits RDS, not speed.

Better: **4 folder pairs**, each a slice of companies, all under the same remote parent:

1. Run `split_sync_batches.py --dest F:\f --jobs 4` (no rclone needed).
2. For each `batch_0N.txt`, make a small parent folder of **directory junctions** *or* add pairs only for the largest company folders first.
3. Practical shortcut without junctions: keep **one** pair on `F:\f` → `/Backup_data/Final_v2`, and add **at most 3 extra pairs** for the biggest company folders listed in the batches. Exclude those same folders from the main pair if the client lets you, so they are not double-uploaded.

If the client cannot exclude subfolders, **do not** add extra pairs on the same files. Use rclone instead.

## What “faster” will and will not do

| Change | Effect |
|---|---|
| 4 rclone jobs, 4 transfers each | Usually 3–8× vs default desktop client |
| `--transfers 32` or 10 desktop pairs | RDS SAVEPOINT; often **slower** after retries |
| `aws s3 sync` / S3 console | Files **do not** show in Nextcloud. Forbidden |
| Browser drag | Too slow / timeouts. Forbidden |
| Recopy F:\f | Not needed |

Office broadband and tiny-file count still dominate. Overnight + leave PC on power.

## After it finishes

- rclone logs: no `ERROR` on real files (ignore excluded junk).
- Browser: open 5 companies that were in different batches.
- Keep old pair paused until staff sign off `Final_v2`.
