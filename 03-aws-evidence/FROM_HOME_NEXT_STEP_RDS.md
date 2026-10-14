# From Home — Next Step: Private RDS MySQL

This starts monthly AWS cost. Create it only when you are ready to continue the project.

Sign in as `logesh.implementer`. Region: **Asia Pacific (Mumbai) / ap-south-1**.
Never put the master password in this file or in chat.

## Values

| Item | Value |
|---|---|
| DB subnet group | saraswathi-db-subnets |
| Subnets | saraswathi-db-a, saraswathi-db-b only |
| Identifier | saraswathi-nextcloud-db |
| Engine | MySQL 8.0 (choose the default 8.0.x AWS offers) |
| Instance | db.t4g.micro (if missing, db.t3.micro) |
| Storage | gp3, 20 GiB, autoscaling max 50 GiB |
| Multi-AZ | No |
| Public access | No |
| VPC | saraswathi-nextcloud-vpc |
| Security group | saraswathi-sg-db |
| Master username | ncadmin |
| Database name | nextcloud |
| Encryption key | alias/saraswathi-rds |
| Backup | 7 days |
| Deletion protection | Yes |

## 1. Create the DB subnet group

1. Search `RDS` → open **RDS**.
2. Confirm region is **Mumbai**.
3. Left: **Subnet groups** → **Create DB subnet group**.
4. Name: `saraswathi-db-subnets`
5. Description: `Saraswathi private DB subnets`
6. VPC: `saraswathi-nextcloud-vpc`
7. Availability Zones: add `ap-south-1a` and `ap-south-1b`.
8. Subnets: add only
   - `subnet-0e11d25441d4a8b85` (`saraswathi-db-a`)
   - `subnet-0f590566d5279bdb3` (`saraswathi-db-b`)
9. Do **not** add public or app subnets.
10. Tags: `Project=Nextcloud`, `Owner=Saraswathi`, `Environment=Production`
11. **Create**.

## 2. Create the database

1. Left: **Databases** → **Create database**.
2. Creation method: **Standard create**.
3. Engine: **MySQL**.
4. Engine version: latest **MySQL 8.0** in the list. Not 5.7.
5. Templates: **Dev/Test** is OK for cost. Settings below still harden it.
6. Availability: **Single-AZ DB instance**.
7. DB instance identifier: `saraswathi-nextcloud-db`
8. Master username: `ncadmin`
9. Credentials: **Self managed**.
10. Master password: partner/you create a long password in a password manager. Type it twice.
11. Instance configuration: **Burstable classes** → `db.t4g.micro`. If t4g is not listed, `db.t3.micro`.
12. Storage type: **gp3**.
13. Allocated storage: `20`.
14. Enable storage autoscaling. Maximum: `50`.
15. Connectivity:
    - Compute resource: **Don't connect to an EC2 compute resource**
    - VPC: `saraswathi-nextcloud-vpc`
    - DB subnet group: `saraswathi-db-subnets`
    - Public access: **No**
    - VPC security group: **Choose existing** → `saraswathi-sg-db` only
    - Remove **default** if AWS added it
    - Availability Zone: **No preference**
    - RDS Proxy: Off
    - Certificate authority: leave default
16. Database authentication: **Password authentication**
17. Monitoring: uncheck **Performance Insights** and extra Enhanced Monitoring for now to save cost.
18. Additional configuration:
    - Initial database name: `nextcloud`
    - DB parameter group: default
    - Backup: enable automatic backups, retention **7 days**
    - Encryption: **Enable encryption** → AWS KMS key → `saraswathi-rds` / `81793ce0-4ca7-4805-8098-17a51d3b0f31`
    - Log exports: optional. Leave off for now.
    - Maintenance: enable auto minor version upgrade
    - Deletion protection: **Enable**
19. Tags: `Project=Nextcloud`, `Owner=Saraswathi`, `Environment=Production`
20. Review estimated cost, then **Create database**.

Status will be **Creating** for 5–15 minutes. Do not create a second database.

## 3. When status is Available

1. Open `saraswathi-nextcloud-db`.
2. Confirm:
   - Publicly accessible = **No**
   - VPC = saraswathi-nextcloud-vpc
   - Security group = saraswathi-sg-db
   - Multi-AZ = No
   - Encryption = Enabled with saraswathi-rds
3. Copy the **Endpoint** (looks like `saraswathi-nextcloud-db.xxxx.ap-south-1.rds.amazonaws.com`).
4. Store endpoint + username `ncadmin` + password in the password manager. Not in chat.

## Stop

Do not create EC2 until RDS is **Available**.
Reply **RDS available** and paste only the endpoint hostname, never the password.
