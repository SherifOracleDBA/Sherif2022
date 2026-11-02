# Project Delivery Status

Status is evidence-based: committed code is not treated as validated until the checks have passed, and deployment is not treated as verified until it has been run in an AWS account.

| Project | Infrastructure code | Application code | Automated tests | CI validation | Live AWS deployment |
|---|---|---|---|---|---|
| 01 — Scalable web app | <strong>Starter committed</strong> | <strong>Demo app committed</strong> | <strong>Unit + smoke tests committed</strong> | Pending run/result | Not deployed |
| 02 — Image processing | Pending | Pending | Pending | Pending | Not deployed |
| 03 — Cognito REST API | Pending | Pending | Pending | Pending | Not deployed |
| 04 — Hybrid connectivity | Pending | Pending | Pending | Pending | Not deployed |
| 05 — Multi-region DR | Pending | Pending | Pending | Pending | Not deployed |
| 06 — ECS microservices | Pending | Pending | Pending | Pending | Not deployed |
| 07 — Serverless data lake | Pending | Pending | Pending | Pending | Not deployed |

## Project 01 scope now committed

- Terraform starter: VPC, public/private subnets, IGW, NAT, security groups, ALB, launch template, ASG, CPU target tracking, private RDS PostgreSQL, WAF, CloudFront, optional Route 53 alias, CloudWatch dashboard/alarms, SNS.
- Application: dependency-free Python web application with health, home, and cacheable static CSS routes.
- Tests: Python unit tests and a deployed endpoint smoke test.
- Automation: GitHub Actions workflow for Python tests and Terraform format/validation.

## Project 01 limitations still to close

- The workflow result has not yet been inspected, so Terraform validation and CI are not marked passed.
- No AWS account deployment has been performed.
- RDS is provisioned but the demo application is not yet connected to it with a least-privilege database user.
- The initial CloudFront-to-ALB origin uses HTTP; enable origin TLS before production use.
- The starter uses one NAT Gateway and defaults RDS Multi-AZ off to reduce learning-lab costs. Use one NAT per AZ and Multi-AZ database for the high-availability exercise.

## Completion gates

1. Infrastructure code committed with pinned provider/tool versions.
2. Application code committed.
3. Unit, integration, and smoke tests pass.
4. Terraform format/init/validate/plan pass.
5. AWS deployment succeeds in a named test account.
6. Functional, security, availability, and failure tests pass.
7. Teardown is completed and remaining billable resources are reviewed.

## Recommended implementation order

Complete Project 01 end-to-end before moving to Projects 02–07. Use its repository conventions and CI workflow as the template for the remaining projects.

**No production readiness, HA, security compliance, or DR claim is made until the corresponding tests and deployment evidence exist.**
