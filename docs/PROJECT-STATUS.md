# Project Delivery Status

Status is evidence-based: infrastructure code and automated tests are marked complete only when committed and CI-verified. Live deployment, high availability, security, and failover are not considered verified until evidence is collected from an AWS account.

| Project | Infrastructure code | Application code | Automated tests | CI / Terraform validation | Live AWS deployment |
|---|---|---|---|---|---|
| 01 — Scalable web app | Assessment-focused Terraform committed | Python app with PostgreSQL integration code committed | 8/8 unit tests passed; deployed DB smoke tests prepared | **Passed** | Not deployed |
| 02 — Image processing | Pending | Pending | Pending | Pending | Not deployed |
| 03 — Cognito REST API | Pending | Pending | Pending | Pending | Not deployed |
| 04 — Hybrid connectivity | Pending | Pending | Pending | Pending | Not deployed |
| 05 — Multi-region DR | Pending | Pending | Pending | Pending | Not deployed |
| 06 — ECS microservices | Pending | Pending | Pending | Pending | Not deployed |
| 07 — Serverless data lake | Pending | Pending | Pending | Pending | Not deployed |

## Latest Project 01 CI evidence

- Workflow: [Project 01 CI](https://github.com/SherifOracleDBA/Sherif2022/actions/workflows/project-01-ci.yml)
- Latest successful run: [Run #45 — 42809046273](https://github.com/SherifOracleDBA/Sherif2022/actions/runs/42809046273).
- Commit checked: `8055f5a26f8d8a078e6b79820a44fa4cf79eb0ca` on `graduation/project-01-submission`.
- Python unit tests: passed (8 tests).
- Terraform format check: passed.
- Terraform init with no backend: passed.
- Terraform validate: passed.
- CI installs the application runtime dependencies before running tests.
- The workflow keeps `terraform fmt -check -recursive` non-mutating.

Earlier failed workflow runs are historical records from intermediate commits. They do not represent the current branch's result; Run #36 validates the current `main` commit.

## Project 01 assessment implementation committed

- VPC with public, private application, and private database subnets across two AZs.
- Dedicated public, application, and database Network ACLs, in addition to Security Groups.
- One NAT Gateway per AZ by default, with a cost-saving single-NAT option.
- ALB, health-checked target group, EC2 Launch Template, and private Auto Scaling group.
- CPU target tracking plus a CloudWatch-alarm-driven step scale-out policy.
- RDS PostgreSQL with Multi-AZ enabled by default and a Secrets Manager-managed master password.
- Separate random application DB credential stored in Secrets Manager. The EC2 role can read only the application secret, not the master secret.
- Python routes for application health, database health, and a sample database write.
- One-time PostgreSQL application-role/table bootstrap script using an SSM port-forward; the application never uses the RDS master account.
- AWS WAF origin-header protection, managed common rules in blocking mode, and rate limiting. Only `/health` is exempted from the CloudFront origin-header requirement for Route 53 health checks.
- CloudFront distribution with HTTPS viewer access and static-asset caching. HTTPS from CloudFront to the ALB is enabled when a matching regional ALB certificate is supplied.
- Route 53 ALB HTTP health check is created by default. The ALB A-alias record is conditional on a user-owned public hosted zone and `alb_domain_name`.
- CloudWatch dashboard, alarms, SNS notifications, README architecture diagram, deployment steps, test plan, and cleanup instructions.

## Remaining Project 01 acceptance gates

The following are not honestly markable as complete until deployment and evidence exist:

1. Deploy the stack into the user's AWS account and review the real Terraform plan/cost before applying.
2. Run the SSM database bootstrap once; then pass `/database` and `POST /visits` smoke tests.
3. Verify two healthy targets in separate AZs, private EC2 placement, and Session Manager access.
4. Demonstrate target tracking, step scale-out, and ASG instance replacement under controlled load.
5. Verify the Route 53 health check reports healthy. Configure `alb_domain_name` and `hosted_zone_id` to create the assessment's ALB alias; these require an owned public hosted zone.
6. Verify RDS Multi-AZ configuration and perform a planned failover test during an approved window.
7. Review WAF sampled requests, verify blocking, confirm SNS delivery, CloudFront caching, and any optional ALB origin TLS certificate configuration.
8. Destroy the stack after evidence capture and verify no unintended billable resources remain.

## Cost and security notes

- The assessment defaults create two NAT Gateways and a Multi-AZ RDS instance. These incur higher charges than a single-NAT/single-AZ lab.
- Terraform state contains sensitive generated database credential material. Do not commit state or plan files. Use encrypted, access-controlled remote state for shared or long-running environments.
- The sample application DB password is generated by Terraform and stored in Secrets Manager. Do not grant the application role access to the RDS master secret.
- CloudFront viewer HTTPS is enabled by default. CloudFront-to-ALB origin TLS requires an issued ACM certificate in the ALB Region and a matching `alb_domain_name`.
- No production-readiness, high-availability, security-compliance, or DR claim is made before the corresponding AWS tests pass.

## Recommended implementation order

Follow the requested build sequence exactly: Project 01, Projects 02 and 03, Project 04, Project 05, Project 06, then Project 07. Complete Project 01's live acceptance gates before beginning Project 02.
