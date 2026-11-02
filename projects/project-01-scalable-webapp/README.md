# Project 01 — Scalable Web Application with ALB and Auto Scaling

**Architecture:** EC2-based, multi-AZ, three-tier application  
**Goal:** Deploy a web application with compute only in private subnets and traffic distributed across two Availability Zones.

## Target architecture

~~~mermaid
flowchart TD
    U[Users] --> R53[Route 53]
    R53 --> CF[CloudFront]
    CF --> WAF[AWS WAF]
    WAF --> ALB[Public ALB]
    ALB --> EC2A[EC2 App - Private AZ A]
    ALB --> EC2B[EC2 App - Private AZ B]
    EC2A --> DB[(RDS Multi-AZ)]
    EC2B --> DB
    EC2A --> CW[CloudWatch]
    EC2B --> CW
    SSM[Systems Manager] -. secure administration .-> EC2A
    SSM -. secure administration .-> EC2B
~~~

**Design clarification:** The baseline ALB is internet-facing in public subnets; EC2 instances and RDS are private. CloudFront is the public distribution and the ALB is its origin. Protect the origin with a custom origin header and WAF controls, and restrict the ALB security group to CloudFront origin-facing traffic where applicable. Do not put EC2 instances in public subnets to make the ALB work.

## Implementation layout

~~~text
infrastructure/terraform/
  modules/vpc/
  modules/alb/
  modules/asg/
  modules/rds/
  envs/dev/
application/web/
tests/smoke/
scripts/
docs/
~~~

## Phase 1 — Plan and prepare

1. Select one Region and two Availability Zones.
2. Allocate a non-overlapping VPC CIDR, for example 10.20.0.0/16.
3. Plan two public subnets for ALB/NAT, two private application subnets, and private database subnets.
4. Choose MySQL or PostgreSQL.
5. Install AWS CLI v2 and Terraform. Configure a named profile with short-lived credentials.
6. Set a budget alert before deploying NAT, ALB, or RDS.

## Phase 2 — Build the network

1. Create the VPC and enable DNS support and DNS hostnames.
2. Create public, private application, and private database subnets across two AZs.
3. Attach an Internet Gateway.
4. Add public routes to the Internet Gateway.
5. Add private application outbound routes through NAT. A NAT Gateway per AZ is more resilient; a single NAT is a lower-cost lab trade-off.
6. Create security groups: ALB accepts HTTPS; application accepts only from ALB; database accepts only its port from the application security group.
7. Add NACL rules only when needed; use security groups as the primary stateful control.

**Checkpoint:** Private instances have no public IP and the database has no direct internet route.

## Phase 3 — Deploy compute

1. Build a small web application with a /health endpoint.
2. Create an EC2 launch template using a supported Amazon Linux image.
3. Attach an instance profile with least-privilege permissions and Systems Manager access.
4. Use user data to install and start the app. Do not embed credentials in user data.
5. Create an Auto Scaling group across both private application subnets.
6. Start with two instances for the two-AZ exercise.
7. Add target tracking based on CPU or ALB requests per target.

**Checkpoint:** Access an instance with Systems Manager Session Manager without opening SSH.

## Phase 4 — Add ALB, WAF, and CloudFront

1. Create an ALB in public subnets and a target group with the application's health check path.
2. Add an HTTPS listener using an ACM certificate; redirect HTTP to HTTPS.
3. Attach the Auto Scaling group to the target group.
4. Create CloudFront with the ALB as origin.
5. Cache static assets; do not cache dynamic application responses unless demonstrably safe.
6. Protect the origin with a custom header and security-group/WAF restrictions.
7. Create a Route 53 alias record to CloudFront.

**Checkpoint:** Verify healthy targets, HTTPS, static cache behavior, and origin protection.

## Phase 5 — Database

1. Create an RDS DB subnet group in private database subnets.
2. Enable Multi-AZ for the HA exercise.
3. Store credentials in Secrets Manager.
4. Give the application role permission to retrieve only its required secret.
5. Configure the app to read connection details securely.
6. Create a least-privilege database user and schema.
7. Test read/write operations and confirm RDS is not publicly accessible.

## Phase 6 — Monitoring, scaling, and protection

1. Associate AWS WAF with CloudFront or the selected protected entry point.
2. Start managed rules in count mode; inspect false positives before blocking.
3. Add rate-based protection.
4. Create CloudWatch dashboards for ALB requests/latency/healthy hosts, EC2 CPU, ASG capacity, and RDS metrics.
5. Add alarms and SNS notifications.
6. Generate controlled load and observe scale-out and scale-in.

## Phase 7 — Validate

- Two healthy targets across two AZs.
- Application remains available after terminating one test instance.
- ASG launches a replacement.
- ALB stops routing to an unhealthy target.
- RDS accepts traffic only from the application tier.
- SSM works without public SSH.
- WAF blocks a controlled test request after rules are enabled.
- CloudWatch alarm delivers an SNS notification.

Record expected result, actual result, and sanitized evidence in docs/test-results/.

## Cleanup

Delete CloudFront and wait for distribution removal; delete Route 53 records and WAF associations; remove ASG, launch template, ALB, and target groups; delete RDS when snapshots are no longer needed; delete NAT Gateways and Elastic IPs; then remove subnets, route tables, security groups, and VPC. Verify billing after cleanup.

## Definition of done

Infrastructure is reproducible from code; the app is reachable through the intended hostname; multi-AZ behavior and scaling are demonstrated; security/monitoring checks pass; and teardown is documented.
