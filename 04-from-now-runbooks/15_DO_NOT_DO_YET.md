# Do not do yet (out of T–U path)

If you hit these, **stop** and ask. They are not required to finish testing through Phase U.

| Item                                                       | Why later                                                    |
| ---------------------------------------------------------- | ------------------------------------------------------------ |
| File → Export → PDF                                      | Known Collabora fail; use Save as PDF near filename          |
| Talk HPB / video / screen share                            | Extra server/CPU; CODE already reports insufficient hardware |
| Full-text search A8                                        | Needs indexer app + jobs; CPU                                |
| ClamAV H11                                                 | Extra packages/RAM on t3a.medium                             |
| E2E encrypted folders H3                                   | Breaks Office/search; policy decision                        |
| NAT Gateway                                                | Cost; not needed for current HTTPS                           |
| Elastic IP                                                 | **Done 2026-11-02** — `13.234.211.7`. Do not release it      |
| Apply RDS OS update                                        | Maintenance window; not “now”                              |
| Fast Snapshot Restore                                      | Cost; do not                                                 |
| Object Lock / MFA delete / S3 website                      | Not in current design                                        |
| CloudTrail data events on**all** buckets             | Noise/cost. **S3 data events off** 2026-09-12; do not turn back on without a written change |
| Stop logging / Delete `Saraswathi-management-trail` | Management audit must stay |
| `rclone sync` (vs copy) | Can delete remote files |
| Nextcloud desktop full sync of Backup_data / DATA1 | Two-way; can change `F:\f`; fills 30 GB disk |
| Recopy `F:\f` or `E:\` | check passed 2026-09-12: 167861 files, 0 differences |
| Stop EC2 to save money | Kills files.t-saraswathi.in |
| PHP 8.5                                                    | Not this OS/app pin                                          |
| Port 22 / root from home                                   | Forbidden                                                    |
| Dump 132 GB in S3 console                                  | Nextcloud will not show it                                   |
| Browser upload of 132 GB                                   | Use desktop client after M1                                  |
| Second RDS / FSR / restore over prod                       | Forbidden                                                    |
| Vendor-patch Time Manager PHP                              | Forbidden                                                    |
| Passwords,`config.php`, cookies, SES secrets in chat/git | Forbidden                                                    |
| Domain NS / delete / transfer                              | Forbidden                                                    |
| Third AWS budget                                           | Forbidden                                                    |
| Glacier 5–10 year (I9)                                    | Separate cost/lifecycle design                               |
| Branding M1–M3                                            | After go-live look-and-feel                                  |
| Federated share C11                                        | No second Nextcloud                                          |
| Creating 10 users who sync all 132 GB on 30 GB disk        | Fills disk                                                   |
| Grow EBS 30 → 200 GiB                                     | Not in quotation; snapshots blow $60 budget                  |
| Primary objectstore in config.php                          | Hides existing Files tree on this install                    |
| Access keys for S3                                         | Use instance role None/builtin auth                          |
| Dump 132 GB in S3 console                                  | Nextcloud will not show pretty folders                       |

**Ask Copilot if:** External storage has **only** Access key (no None), mount row is red, SMTP 587 fails, disk alarm during M3 (should not fill), public IP changed, impersonation missing, CODE crash on two-user edit.
