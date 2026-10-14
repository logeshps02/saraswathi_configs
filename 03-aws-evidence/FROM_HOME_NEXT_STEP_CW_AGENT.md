# From Home — Next Step: CloudWatch agent (memory + disk)

Default-metric alarms exist:

| Name | State (2026-08-26) |
|---|---|
| `saraswathi-ec2-status-check-failed` | OK |
| `saraswathi-ec2-cpu-high` | OK |
| `saraswathi-rds-free-storage-low` | Insufficient data (wait for next RDS sample) |

Memory and disk are **not** published until the **CloudWatch agent** runs on the instance. Do **not** create NAT. Do **not** open port 22. Do **not** create extra users. Do **not** create another budget.

Sign in as `logesh.implementer`. Region: **Asia Pacific (Mumbai) / ap-south-1**.

## Values

| Item | Value |
|---|---|
| Instance | `i-002509b77963fd5fc` `saraswathi-nextcloud-app` |
| IAM role | `saraswathi-ec2-ssm` |
| Managed policy to attach | `CloudWatchAgentServerPolicy` |
| Alarm 4 | `saraswathi-ec2-mem-high` |
| Alarm 5 | `saraswathi-ec2-disk-high` |
| Notify | `saraswathi-ops-alerts` |

## 1. IAM (console first)

1. **IAM** → **Roles** → `saraswathi-ec2-ssm`.
2. **Add permissions** → **Attach policies**.
3. Find AWS managed **CloudWatchAgentServerPolicy**. Attach.
4. Paste: role name + that `CloudWatchAgentServerPolicy` is listed. No ARNs required.

Do not create access keys. Do not attach AdministratorAccess.

## 2. Install agent (Session Manager)

Paste as **one line**.

```sh
curl -fsSL -o /tmp/amazon-cloudwatch-agent.deb https://s3.ap-south-1.amazonaws.com/amazoncloudwatch-agent-ap-south-1/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb && sudo dpkg -i /tmp/amazon-cloudwatch-agent.deb && /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -a status
```

Need: package installed; status JSON or `running`/`stopped` (stopped is OK before config).

## 3. Config + start (Session Manager)

One line:

```sh
sudo tee /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json >/dev/null <<'EOF'
{"metrics":{"namespace":"CWAgent","aggregation_dimensions":[["InstanceId"],["InstanceId","path"]],"append_dimensions":{"InstanceId":"${aws:InstanceId}"},"metrics_collected":{"mem":{"measurement":["mem_used_percent"],"metrics_collection_interval":60},"disk":{"measurement":["used_percent"],"metrics_collection_interval":60,"resources":["/"]}}}}
EOF
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json && /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -a status
```

Need: `status` **running**. Paste status only. Do not paste the JSON file later.

### Observed (2026-08-26)

| Item | Value |
|---|---|
| Package | amazon-cloudwatch-agent **1.300071.0b1720-1** |
| After dpkg | status **stopped**, configstatus not configured |
| After fetch-config | validation succeeded |
| After start | **running**, configured, starttime 2026-08-25T19:58:13Z |
| IAM `CloudWatchAgentServerPolicy` | **attached** on `saraswathi-ec2-ssm` (with AmazonSSMManagedInstanceCore + inline S3) |

Do not install a second agent. Do not paste the JSON file again.

## 4. Two guest-metric alarms (console, after agent running ~2 min)

CloudWatch → Alarms → Create alarm → **Browse** → **CWAgent** (not EC2).

**Memory**

| Field | Value |
|---|---|
| Metric | `mem_used_percent` for `i-002509b77963fd5fc` |
| Statistic / period | Average / 5 minutes |
| Whenever | **Greater > 85** |
| Datapoints | 3 out of 3 |
| Name | `saraswathi-ec2-mem-high` |
| Notify | In alarm → `saraswathi-ops-alerts` |

**Disk /**

| Field | Value |
|---|---|
| Metric | `disk_used_percent` (or `used_percent`) path `/` instance `i-002509b77963fd5fc` |
| Statistic / period | Average / 5 minutes |
| Whenever | **Greater > 80** |
| Datapoints | 2 out of 2 |
| Name | `saraswathi-ec2-disk-high` |
| Notify | In alarm → `saraswathi-ops-alerts` |

If **CWAgent** is missing: wait 2 minutes, confirm agent **running**, region Mumbai. Do not install a second agent.

### Created (2026-08-26)

| Name | State | Condition |
|---|---|---|
| `saraswathi-ec2-disk-high` | **Insufficient data** (OK for a few minutes) | disk_used_percent > 80 for 2 datapoints within 10 minutes |
| `saraswathi-ec2-mem-high` | **OK** | mem_used_percent > 85 for 3 datapoints within 15 minutes |
| `saraswathi-rds-free-storage-low` | **OK** | FreeStorageSpace < 2 GiB for 2 datapoints within 10 minutes |
| `saraswathi-ec2-cpu-high` | **OK** | CPUUtilization > 85 for 3 datapoints within 15 minutes |
| `saraswathi-ec2-status-check-failed` | **OK** | StatusCheckFailed >= 1 for 2 datapoints within 2 minutes |

Five alarms exist. Do not create a sixth this step. Do not create a composite alarm.

## 5. Paste back

- IAM policy attached yes/no
- Agent status running/stopped
- Two new alarm **names** + **states**

## Stop

Agent + five alarms are complete. Do not create NAT or EIP. Do not open 22. Do not paste emails. Do not create a composite alarm. AWS Backup vault is the next guide.
