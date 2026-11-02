# Project 05 — Multi-Region Disaster Recovery with Route 53 Failover

**Architecture:** Warm standby  
**Primary Region:** us-east-1 (configurable)  
**Secondary Region:** eu-west-1 (configurable)

**Goal:** Run a reduced-capacity stack in a secondary Region, replicate required data, and demonstrate controlled recovery.

## DR strategy comparison

| Strategy | Recovery posture | Cost profile | Recovery speed |
|---|---|---|---|
| Backup and restore | Backups only | Lowest | Slowest |
| Pilot light | Core data/services ready; compute started during recovery | Low–medium | Medium |
| Warm standby | Reduced but running secondary stack | Medium–high | Faster |
| Multi-site active-active | Both Regions serve traffic | Highest | Fastest when correctly designed |

Actual RTO/RPO depends on the application, replication lag, automation, testing, and operational decisions. Do not publish guaranteed recovery objectives until measured.

## Target architecture

~~~mermaid
flowchart TD
    U[Users] --> DNS[Route 53 failover records]
    DNS --> P[Primary Region]
    DNS -. failover .-> S[Secondary Region]
    P --> PAPP[ALB + EC2 ASG]
    S --> SAPP[ALB + minimum ASG]
    PAPP --> PA[(Primary database)]
    PA == async replication ==> SA[(Secondary database)]
    PS3[S3 primary] == CRR ==> SS3[S3 secondary]
    P --> CW[CloudWatch / EventBridge]
    S --> CW
~~~

## Phase 1 — Prepare the application

1. Start from a working application deployment such as Project 01.
2. Externalize configuration and secrets from instance-local files.
3. Separate stateful data from EC2 storage.
4. Define RTO and RPO targets to measure, not assumptions.
5. Identify dependencies required in both Regions: certificates, IAM roles, networking, logs, keys, DNS, and artifacts.
6. Choose a database cross-region option that matches consistency and failover requirements.

## Phase 2 — Deploy both Regions

1. Parameterize Region, CIDR, environment, and resource names.
2. Deploy the complete primary stack.
3. Deploy reduced-capacity secondary resources using the same versioned infrastructure code.
4. Use CloudFormation StackSets or another repeatable IaC approach for multi-account/Region consistency.
5. Keep separate state/configuration per Region.
6. Validate that secondary application can start without primary Region resources.

## Phase 3 — Replicate data

1. Configure the chosen database replication solution. For Aurora Global Database, create the primary cluster and secondary Region cluster using supported engine versions.
2. Monitor replication lag and test managed switchover/failover procedures.
3. Enable S3 versioning and configure Cross-Region Replication with its required IAM role.
4. Use DynamoDB Global Tables only when the data model supports multi-Region writes and conflict handling.
5. Test restore and consistency, not just replica existence.
6. Document replicated data, backup-only data, and possible data loss during recovery.

## Phase 4 — Health checks and DNS

1. Create primary and secondary Route 53 failover records.
2. Check a meaningful application endpoint, not merely a TCP port.
3. Set TTL based on recovery targets and DNS caching behavior.
4. Test a health-check failure in a controlled window.
5. Confirm the secondary application is ready before directing traffic.
6. Document manual approval and rollback steps. DNS failover is not a substitute for database promotion or application recovery.

## Phase 5 — Automation and backups

1. Configure AWS Backup plans for supported resources.
2. Use EventBridge for alarms/events that should trigger a runbook.
3. Use Lambda or Systems Manager Automation for safe, repeatable tasks.
4. Require approval for destructive or data-promotion operations.
5. Make automation idempotent and log every action.
6. Test the runbook while the primary Region is healthy.

## Phase 6 — DR exercise

1. Record initial health and replication lag.
2. Simulate the agreed primary failure.
3. Follow the runbook: decide, promote/activate secondary data services, scale secondary compute, validate the app, then shift DNS.
4. Measure time to restore service and data loss.
5. Restore primary service in a controlled manner.
6. Define and separately test the failback sequence.
7. Update measured RTO/RPO and remediate gaps.

## Validation checklist

- Both Regions deploy from version-controlled configuration.
- Secondary application can serve requests.
- Database replication lag is recorded.
- S3 replica objects arrive as expected.
- Route 53 health check and TTL behavior are understood.
- Recovery and failback runbooks are tested.
- Actual RTO/RPO is measured and reported.

## Cost and cleanup

Two Regions, two application stacks, cross-region database, replication, and backups can be expensive. Use minimal capacity and short test windows. Remove health checks/records, database clusters, replication, S3 versions/replicas, EC2/ASG/ALBs, and backup recovery points as appropriate.

## Definition of done

Warm standby is demonstrably capable of recovery, the runbook covers data promotion and traffic shifting, and measured recovery results are documented. DNS failover alone is insufficient.
