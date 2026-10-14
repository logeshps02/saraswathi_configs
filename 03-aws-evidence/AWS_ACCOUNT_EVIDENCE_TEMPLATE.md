# AWS Account Evidence

Fill this after the client meeting. Never write passwords, access keys, MFA codes, or card numbers.

| Item | Value |
|---|---|
| Date created | |
| Firm legal name | |
| AWS Account ID | |
| Root email | |
| Region confirmed | ap-south-1 |
| Root MFA enabled | Yes / No |
| Root access keys present | Must be None |
| Billing alerts enabled | Yes / No |
| Budget created | Yes / No |
| CloudTrail enabled | Yes — Saraswathi-management-trail, status Logging |
| CloudTrail S3 bucket | aws-cloudtrail-logs-055855670388-1f1c3ed9 |
| CloudTrail home region | ap-south-1, multi-region Yes |
| Implementer access type | IAM user / IAM Identity Center user / assumed role |
| Implementer username | |
| MFA on implementer identity | Yes / No |
| Root password holder | Firm representative name |
| MFA device holder | Firm representative name |
| Screenshot files stored | |
| VPC name | saraswathi-nextcloud-vpc |
| VPC ID | vpc-0a25ed4fa155f526d |
| VPC CIDR | 10.20.0.0/16 |
| DNS resolution / hostnames | Enabled / Enabled |
| saraswathi-public-a | subnet-0032deb58f3f4911d / 10.20.1.0/24 / ap-south-1a |
| saraswathi-public-b | subnet-00f025cdbb7e55063 / 10.20.2.0/24 / ap-south-1b |
| saraswathi-app-a | subnet-046e174df1d34b966 / 10.20.11.0/24 / ap-south-1a |
| saraswathi-app-b | subnet-05bb5715e314ee9a0 / 10.20.12.0/24 / ap-south-1b |
| saraswathi-db-a | subnet-0e11d25441d4a8b85 / 10.20.21.0/24 / ap-south-1a |
| saraswathi-db-b | subnet-0f590566d5279bdb3 / 10.20.22.0/24 / ap-south-1b |
| Public IP auto-assign | Yes on public-a and public-b only |
| Existing unused IGW | igw-063d2617c280aa069 attached to vpc-0c611dba9842d2d2e (not our VPC; leave it) |
| saraswathi-igw | igw-02ac3964b2f226ce1 attached to vpc-0a25ed4fa155f526d |
| saraswathi-rt-public | rtb-0f47bead49020f30c |
| saraswathi-rt-public routes | 10.20.0.0/16 local; 0.0.0.0/0 igw-02ac3964b2f226ce1 Active |
| saraswathi-rt-public associations | saraswathi-public-a, saraswathi-public-b |
| saraswathi-rt-app | rtb-0053cd2e7800f4558; local only; app-a + app-b |
| saraswathi-rt-db | rtb-0d28b44ae54b4b1af; local only; db-a + db-b |
| saraswathi-vpc-flowlogs | fl-0bb98d0c00ed6bd8b Active; CloudWatch /vpc/saraswathi-nextcloud-vpc; role saraswathi-vpc-flowlogs-role |
| saraswathi-sg-web | sg-02f46796f923d880d; 2 inbound (80/443) |
| saraswathi-sg-app | sg-06795a8355e818232; inbound TCP 80 from sg-02f46796f923d880d |
| saraswathi-sg-db | sg-0d232c9611be9dfc2; inbound 3306 from sg-06795a8355e818232 |
| saraswathi-sg-admin | sg-09e08c9be158cbb69; 0 inbound |
| KMS saraswathi-ebs | c7e84359-7794-41ea-bd5c-5f77ccf75875; Enabled; rotation 365 days |
| KMS saraswathi-rds | 81793ce0-4ca7-4805-8098-17a51d3b0f31; Enabled; rotation 365 days |
| S3 files bucket | saraswathi-nextcloud-files-055855670388 |
| S3 public access | Block all public access On; ACLs disabled; 0 objects |
| RDS DB subnet group | saraswathi-db-subnets created |
| RDS instance | saraswathi-nextcloud-db |
| RDS status | Available |
| RDS engine / size | MySQL Community / db.t4g.micro |
| RDS AZ | ap-south-1b |
| RDS VPC | vpc-0a25ed4fa155f526d |
| RDS Multi-AZ | No |
| RDS engine version | MySQL 8.4.9 |
| RDS DB name | nextcloud |
| RDS master username | ncadmin |
| RDS encryption | Enabled / saraswathi-rds |
| RDS storage | gp3 20 GiB, autoscaling max 50 GiB |
| RDS deletion protection | Enabled |
| RDS monitoring | Database Insights Standard; Enhanced Monitoring off |
| RDS endpoint | saraswathi-nextcloud-db.c5giuu4c6ye6.ap-south-1.rds.amazonaws.com:3306 |
| RDS public / internet gateway | Internet access gateway Disabled; inbound only from saraswathi-sg-app |

Screenshot names to capture later (no secrets on screen):

- AWS account ID page
- Region showing Mumbai / ap-south-1
- Root MFA = assigned
- Security credentials showing no root access keys
- Budget and billing alarm
