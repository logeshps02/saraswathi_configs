# From Home — Next Step Only: Security Groups

Do this after VPC flow logs are Active. Sign in as `logesh.implementer`. Region: Mumbai.

Do not create EC2, RDS, NAT, or Nextcloud in this step.

Create these four groups in `saraswathi-nextcloud-vpc` only.

| Name | Purpose |
|---|---|
| saraswathi-sg-web | HTTP/HTTPS entry |
| saraswathi-sg-app | App server later |
| saraswathi-sg-db | RDS MySQL later |
| saraswathi-sg-admin | Admin/SSM only; no public SSH |

## 1. Open Security groups

1. Search `VPC` → left: **Security groups**.
2. Ignore the default group on the default VPC.
3. Click **Create security group**.

## 2. Create saraswathi-sg-web

1. Name: `saraswathi-sg-web`
2. Description: `Saraswathi web HTTP HTTPS`
3. VPC: `saraswathi-nextcloud-vpc`
4. Inbound rules → **Add rule** twice:

| Type | Port | Source | Description |
|---|---|---|---|
| HTTP | 80 | Anywhere-IPv4 `0.0.0.0/0` | HTTP to HTTPS and certificate |
| HTTPS | 443 | Anywhere-IPv4 `0.0.0.0/0` | Public Nextcloud later |

5. Outbound: leave default **All traffic** to `0.0.0.0/0`.
6. Tags: `Project=Nextcloud`, `Owner=Saraswathi`, `Environment=Production`
7. **Create security group**.

## 3. Create saraswathi-sg-app

1. **Create security group**.
2. Name: `saraswathi-sg-app`
3. Description: `Saraswathi app from web only`
4. VPC: `saraswathi-nextcloud-vpc`
5. Inbound: **Add rule**
   - Type: **Custom TCP**
   - Port: `80`
   - Source: **Custom** → start typing `saraswathi-sg-web` → pick that security group
   - Description: `From web SG`
6. Do **not** set source to `0.0.0.0/0`.
7. Same tags. Create.

If the first server will also serve HTTPS itself, we add 443 from the web SG later. Do not add it now.

## 4. Create saraswathi-sg-db

1. **Create security group**.
2. Name: `saraswathi-sg-db`
3. Description: `Saraswathi RDS MySQL from app only`
4. VPC: `saraswathi-nextcloud-vpc`
5. Inbound: **Add rule**
   - Type: **MySQL/Aurora**
   - Port: `3306`
   - Source: **Custom** → `saraswathi-sg-app`
   - Description: `From app SG`
6. Same tags. Create.

## 5. Create saraswathi-sg-admin

1. **Create security group**.
2. Name: `saraswathi-sg-admin`
3. Description: `Saraswathi admin no public SSH`
4. VPC: `saraswathi-nextcloud-vpc`
5. Inbound: **add no SSH rule**. Leave inbound empty.
6. Same tags. Create.

We will use Session Manager later. Do not open port 22 to the internet.

## Stop

Reply **security groups done** and paste the four group IDs if shown (`sg-...`).
