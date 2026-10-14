# From Home — Next Step Only: Create the Mumbai VPC

Do this after CloudTrail is logging. Sign in as `logesh.implementer`. Never use root.

Do not create EC2, RDS, Nextcloud, or a NAT Gateway in this step.
A NAT Gateway costs money every hour. We add it only when the private app server needs outbound internet.

## Values to type exactly

| Item | Value |
|---|---|
| Region | Asia Pacific (Mumbai) / ap-south-1 |
| VPC name | saraswathi-nextcloud-vpc |
| VPC CIDR | 10.20.0.0/16 |
| Public subnet AZ-a | saraswathi-public-a / 10.20.1.0/24 / ap-south-1a |
| Public subnet AZ-b | saraswathi-public-b / 10.20.2.0/24 / ap-south-1b |
| Private app subnet AZ-a | saraswathi-app-a / 10.20.11.0/24 / ap-south-1a |
| Private app subnet AZ-b | saraswathi-app-b / 10.20.12.0/24 / ap-south-1b |
| Private DB subnet AZ-a | saraswathi-db-a / 10.20.21.0/24 / ap-south-1a |
| Private DB subnet AZ-b | saraswathi-db-b / 10.20.22.0/24 / ap-south-1b |
| Internet Gateway | saraswathi-igw |
| Public route table | saraswathi-rt-public |
| Private app route table | saraswathi-rt-app |
| Private DB route table | saraswathi-rt-db |

## 1. Sign in and lock the region

1. Open the IAM console sign-in URL.
2. Sign in as `logesh.implementer` + your MFA.
3. Top-right: set region to **Asia Pacific (Mumbai) / ap-south-1**.
4. If it is not Mumbai, stop and change it before creating anything.

## 2. Create the VPC only

1. Top search bar: type `VPC`.
2. Click **VPC**.
3. Left menu: **Your VPCs**.
4. Do **not** click **Create VPC** on the big “VPC and more” wizard if you want full control.
   Use the simple path below.
5. Click **Create VPC**.
6. Resources to create: **VPC only**.
7. Name tag: `saraswathi-nextcloud-vpc`
8. IPv4 CIDR: `10.20.0.0/16`
9. IPv6: **No IPv6 CIDR**
10. Tenancy: **Default**
11. Tags: add
    - `Project` = `Nextcloud`
    - `Owner` = `Saraswathi`
    - `Environment` = `Production`
12. Click **Create VPC**.
13. Open the new VPC.
14. Copy the **VPC ID** (starts with `vpc-`) into `AWS_ACCOUNT_EVIDENCE_TEMPLATE.md` or a note in this folder.
15. Actions → **Edit VPC settings**:
    - Enable **DNS resolution**
    - Enable **DNS hostnames**
    - Save

## 3. Create six subnets

1. Left menu: **Subnets** → **Create subnet**.
2. VPC: `saraswathi-nextcloud-vpc`.
3. Create the first subnet, then use **Add new subnet** until all six exist.

| Subnet name | AZ | IPv4 CIDR |
|---|---|---|
| saraswathi-public-a | ap-south-1a | 10.20.1.0/24 |
| saraswathi-public-b | ap-south-1b | 10.20.2.0/24 |
| saraswathi-app-a | ap-south-1a | 10.20.11.0/24 |
| saraswathi-app-b | ap-south-1b | 10.20.12.0/24 |
| saraswathi-db-a | ap-south-1a | 10.20.21.0/24 |
| saraswathi-db-b | ap-south-1b | 10.20.22.0/24 |

4. Click **Create subnet**.
5. You must see **6** subnets in this VPC.

### Auto-assign public IP only on public subnets

6. Tick `saraswathi-public-a` → Actions → **Edit subnet settings**.
7. Enable **Auto-assign public IPv4 address** → Save.
8. Repeat for `saraswathi-public-b` only.
9. Leave `saraswathi-app-*` and `saraswathi-db-*` **off**. Those stay private.

## 4. Create and attach the Internet Gateway

1. Left menu: **Internet gateways** → **Create internet gateway**.
2. Name: `saraswathi-igw`
3. Same three tags as the VPC.
4. Create internet gateway.
5. Select `saraswathi-igw` → Actions → **Attach to VPC**.
6. VPC: `saraswathi-nextcloud-vpc` → Attach.
7. State must become **Attached**.

## 5. Create three route tables

The main/default route table will exist automatically. Do not use it for everything. Create named tables.

### Public table

1. Left menu: **Route tables** → **Create route table**.
2. Name: `saraswathi-rt-public`
3. VPC: `saraswathi-nextcloud-vpc`
4. Create.
5. Select it → **Routes** tab → **Edit routes** → **Add route**:
   - Destination: `0.0.0.0/0`
   - Target: **Internet Gateway** → `saraswathi-igw`
6. Save changes.
7. **Subnet associations** tab → **Edit subnet associations**.
8. Tick only `saraswathi-public-a` and `saraswathi-public-b`.
9. Save.

### App private table

10. Create route table `saraswathi-rt-app` in the same VPC.
11. Do **not** add `0.0.0.0/0` yet. No NAT in this step.
12. Associate only `saraswathi-app-a` and `saraswathi-app-b`.

### DB private table

13. Create route table `saraswathi-rt-db` in the same VPC.
14. Do **not** add internet routes.
15. Associate only `saraswathi-db-a` and `saraswathi-db-b`.

## 6. Turn on VPC Flow Logs

1. Left menu: **Your VPCs** → select `saraswathi-nextcloud-vpc`.
2. **Flow logs** tab → **Create flow log**.
3. Name: `saraswathi-vpc-flowlogs`
4. Filter: **All**
5. Maximum aggregation interval: **10 minutes**
6. Destination: **Send to CloudWatch Logs**
   - If this asks for a new log group, create `/vpc/saraswathi-nextcloud-vpc`
   - If it asks for an IAM role, choose **Create a new role** / allow the console to create it
7. If CloudWatch role creation fails, use destination **Send to an Amazon S3 bucket** and pick the CloudTrail bucket only if you understand the prefix. Prefer CloudWatch if the role creates cleanly.
8. Create flow log.
9. Status should become **Active**.

## 7. Evidence to save

Put these in `03-aws-evidence`. No secrets on screen.

- VPC details showing `10.20.0.0/16` and DNS enabled  
  `YYYY-MM-DD_aws_vpc_v1.png`
- Subnets list showing all 6 names and CIDRs  
  `YYYY-MM-DD_aws_subnets_v1.png`
- Internet gateway = Attached  
  `YYYY-MM-DD_aws_igw_v1.png`
- Public route table with `0.0.0.0/0` → igw  
  `YYYY-MM-DD_aws_rt-public_v1.png`
- Flow log Active  
  `YYYY-MM-DD_aws_vpc-flowlogs_v1.png`

Fill this table:

| Item | ID / value |
|---|---|
| VPC ID | vpc- |
| IGW ID | igw- |
| Public subnet a | subnet- |
| Public subnet b | subnet- |
| App subnet a | subnet- |
| App subnet b | subnet- |
| DB subnet a | subnet- |
| DB subnet b | subnet- |

## Stop

Do not create:

- NAT Gateway
- EC2
- RDS
- extra S3 buckets
- security groups yet

Reply **VPC done** when the six subnets and IGW exist.
