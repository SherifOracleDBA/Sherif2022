# Project 01 Validation and Acceptance Matrix

Use this matrix as the graduation-project test plan. A code check is not a substitute for a deployed AWS acceptance test.

| ID | Requirement | Verification | Expected result | Evidence |
|---|---|---|---|---|
| NET-01 | VPC spans two AZs | aws ec2 describe-subnets | Public, app-private, and DB-private subnets exist in two AZs | Sanitized CLI |
| NET-02 | Private application tier | Inspect EC2 instances and subnet routes | App EC2 has no public IP and uses private subnet route via NAT | CLI output |
| NET-03 | Private DB tier | aws rds describe-db-instances | RDS is not publicly accessible and uses private DB subnet group | CLI output |
| NET-04 | NACL and SG boundaries | Inspect inbound/outbound rules | ALB-to-app and app-to-DB paths only; ephemeral return traffic allowed where required | Rule screenshots |
| APP-01 | ALB health checks | aws elbv2 describe-target-health | At least two healthy targets in separate AZs | CLI output |
| APP-02 | Application health | Run smoke test | GET /health returns HTTP 200 and status ok | Test log |
| APP-03 | Database connectivity | Smoke test --check-database | GET /database returns HTTP 200 | Test log |
| APP-04 | Database write | Smoke test --create-visit | POST /visits returns HTTP 201 and generated demo ID | Test log |
| SCALE-01 | Target tracking | Inspect ASG policies and run controlled load | Target tracking policy exists and ASG scales in response to sustained CPU load | ASG activity + CloudWatch |
| SCALE-02 | Step scaling | Generate controlled load above configured alarm threshold | Step policy adds capacity; record alarm transition and ASG activity | Alarm history |
| SCALE-03 | Instance replacement | Terminate one test instance during approved window | ASG launches replacement and target returns healthy | ASG activity |
| DB-01 | RDS Multi-AZ | aws rds describe-db-instances | MultiAZ=true; DB is private | CLI output |
| DB-02 | RDS failover | Planned failover during approved window | Failover completes and application reconnects successfully | RDS events + smoke test |
| SEC-01 | WAF origin verification | Request ALB application path without origin header; compare CloudFront request | Direct ALB application request is blocked; CloudFront application request succeeds | HTTP status + WAF sample |
| SEC-02 | WAF managed rules | Use safe, non-destructive test request and inspect WAF metrics | Managed rule behavior is observed and documented | WAF metrics |
| SEC-03 | SSM access | Start Session Manager session to private EC2 | Session opens without SSH or bastion host | Session screenshot |
| SEC-04 | Secrets Manager least privilege | Inspect EC2 role policy and test app behavior | Instance role can read app DB secret only, not master secret | IAM policy |
| CDN-01 | CloudFront HTTPS | Open output application URL | Viewer redirects/uses HTTPS | Browser screenshot |
| CDN-02 | Static caching | Inspect response headers / CloudFront cache metrics | /static/* is cacheable; dynamic/database routes are not cached | Header capture |
| DNS-01 | Route 53 health check | Inspect health check status | Health check reports healthy for ALB /health | Console screenshot |
| DNS-02 | Route 53 alias | Inspect record when custom hosted zone is configured | ALB alias exists and references health check | Record screenshot |
| MON-01 | CloudWatch dashboard | Open dashboard | Dashboard shows application/ALB/ASG metrics | Screenshot |
| MON-02 | CloudWatch alarms | Inspect alarm states | CPU, unhealthy-host, and step-scaling alarms exist | Alarm screenshot |
| MON-03 | SNS notifications | Confirm subscription and trigger approved test alarm | Email notification received | Redacted email |
| CI-01 | Automated code checks | GitHub Actions | Python tests, Terraform fmt, init, validate pass | Workflow URL |
| CLEAN-01 | Cleanup | Run destroy and inspect resources | No unintended billable project resources remain | Destroy log |

## Pass criteria
- Mark a row PASS only when its verification has been run and evidence has been saved.
- Mark it BLOCKED when it requires a domain, certificate, permission, or approved test window that is not available.
- Mark it NOT RUN when no test has been performed.
- Do not infer a runtime pass from Terraform configuration, a successful plan, or GitHub CI.
