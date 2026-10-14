# From Home — Next Step: EC2 Ubuntu for Nextcloud

RDS is Available and private. This EC2 starts hourly cost. Sign in as `logesh.implementer`. Region: Mumbai.

Do not open SSH to `0.0.0.0/0`. Use SSM. Do not paste the RDS password anywhere in AWS tags.

## Values

| Item | Value |
|---|---|
| Name | saraswathi-nextcloud-app |
| AMI | Ubuntu Server 24.04 LTS (64-bit x86) `ami-006f82a1d5a27da54` (noble; not 26.04) |
| Instance type | t3.medium |
| Subnet | saraswathi-public-a |
| Auto-assign public IP | Enable |
| Security groups | saraswathi-sg-web + saraswathi-sg-app + saraswathi-sg-admin |
| Disk | 30 GiB gp3, encrypted with saraswathi-ebs |
| IAM role | saraswathi-ec2-ssm |
| IMDSv2 | Required |
| Key pair | Proceed without a key pair (SSM only) |

## Launched instance (2026-08-25)

| Item | Value |
|---|---|
| Instance ID | i-002509b77963fd5fc |
| Name | saraswathi-nextcloud-app |
| State | Running |
| AMI | ami-006f82a1d5a27da54 ubuntu-noble-24.04-amd64-server-20260610 |
| Type | t3.medium |
| VPC | vpc-0a25ed4fa155f526d saraswathi-nextcloud-vpc |
| Subnet | subnet-0032deb58f3f4911d saraswathi-public-a |
| Private IP | 10.20.1.144 |
| Public IPv4 | 3.111.213.217 (auto-assigned 2026-08-25; not an Elastic IP) |
| IAM role | saraswathi-ec2-ssm |
| IMDSv2 | Required |
| Termination protection | Enabled |
| Credit specification | standard |
| Key pair | none |
| Security groups | sg-02f46796f923d880d web; sg-06795a8355e818232 app; sg-09e08c9be158cbb69 admin |
| Inbound | TCP 80 and 443 from 0.0.0.0/0 on web; TCP 80 from web SG on app; admin none. No SSH 22 |
| Root volume | vol-0063c19bdcb7583bf /dev/sda1 30 GiB In-use Encrypted Yes KMS c7e84359-7794-41ea-bd5c-5f77ccf75875 (saraswathi-ebs) |
| SSM | Connected 2026-08-25 |

## 1. Create the SSM role first

1. Search `IAM` → **Roles** → **Create role**.
2. Trusted entity: **AWS service**.
3. Use case: **EC2**.
4. Next.
5. Search and tick **AmazonSSMManagedInstanceCore**.
6. Next.
7. Role name: `saraswathi-ec2-ssm`
8. Tags: `Project=Nextcloud`, `Owner=Saraswathi`, `Environment=Production`
9. **Create role**.

## 2. Launch the instance

1. Search `EC2` → **Instances** → **Launch instance**.
2. Name: `saraswathi-nextcloud-app`
3. Application and OS: **Ubuntu**.
4. Do **not** trust the Quick Start card if it shows Ubuntu 26.04 (`ami-01a00762f46d584a1`).
   Click **Browse more AMIs** → search `24.04` → pick Canonical **Ubuntu Server 24.04 LTS**, 64-bit (x86).
   If AWS warns that volumes and security groups will be overridden, click **Confirm changes**, then set the 30 GiB encrypted volume and the three Saraswathi security groups again.
   After an AMI change, AWS often switches Firewall back to **Create security group** with SSH 22 from `0.0.0.0/0` and resets the root volume to **8 GiB**. That is not acceptable. Switch to **Select existing security group**, tick the three Saraswathi groups, and set **30 GiB gp3 encrypted with saraswathi-ebs** before launch.
   Do not launch until Summary says 24.04, is not `ami-01a00762f46d584a1`, Firewall is the three existing groups (not a new SSH group), and storage is 30 GiB.
5. Instance type: **t3.medium**.
6. Key pair: **Proceed without a key pair**.
7. Network:
   - VPC: `saraswathi-nextcloud-vpc`
   - Subnet: `saraswathi-public-a`
   - Auto-assign public IP: **Enable**
   - Firewall: **Select existing security groups**
   - Tick all three: `saraswathi-sg-web`, `saraswathi-sg-app`, `saraswathi-sg-admin`
   - Do **not** use the default security group
8. Configure storage:
   - Size: `30` GiB
   - Volume type: **gp3**
   - Encryption: **Enabled**
   - KMS key: `saraswathi-ebs` / `c7e84359-7794-41ea-bd5c-5f77ccf75875`
9. Advanced details:
   - IAM instance profile: `saraswathi-ec2-ssm`
   - Metadata version: **V2 only (token required)**
   - Metadata response hop limit: `2` is OK
   - Termination protection: Enable if shown
10. Tags: `Project=Nextcloud`, `Owner=Saraswathi`, `Environment=Production`, `Name=saraswathi-nextcloud-app`
11. Check the summary. Estimated cost should be tens of USD per month, not hundreds.
12. **Launch instance**.

## 3. Confirm

1. Wait until Instance state = **Running** and Status checks = **2/2** or **Initializing** then 2/2.
2. Copy Instance ID (`i-...`) and public IPv4.
3. Select the instance → **Connect** → **Session Manager**.
4. If **Connect** is enabled, SSM works. Do not install Nextcloud yet.

## 4. After launch — Security, Storage, then Session Manager

1. Open instance `i-002509b77963fd5fc`.
2. Tab **Security**: security groups must be only `saraswathi-sg-web`, `saraswathi-sg-app`, `saraswathi-sg-admin`. Inbound must not include SSH 22 from `0.0.0.0/0`.
3. Tab **Storage**: root volume 30 GiB, gp3, Encrypted Yes, KMS `saraswathi-ebs`.
4. Tab **Tags**: `Name`, `Project=Nextcloud`, `Owner=Saraswathi`, `Environment=Production`.
5. Select the instance → **Connect** → **Session Manager** → **Connect**.
6. If a shell opens, type `whoami` then `exit`. Do not install packages yet.

If Session Manager says it cannot connect, wait 2–5 minutes for status checks **2/2**, then try again. Do not open port 22.

## Stop

Security, storage, and SSM are confirmed. Next file: [FROM_HOME_NEXT_STEP_UBUNTU_PATCH.md](FROM_HOME_NEXT_STEP_UBUNTU_PATCH.md). Do not install Nextcloud or PHP yet.
