# Project Delivery Status

Status is evidence-based: committed code is not treated as validated until checks pass, and deployment is not verified until it has been run in an AWS account.

| Project | Infrastructure code | Application code | Automated tests | CI / Terraform validation | Live AWS deployment |
|---|---|---|---|---|---|
| 01 — Scalable web app | Starter committed | Demo app committed | 4/4 unit tests passed in GitHub Actions | **Passed** | Not deployed |
| 02 — Image processing | Pending | Pending | Pending | Pending | Not deployed |
| 03 — Cognito REST API | Pending | Pending | Pending | Pending | Not deployed |
| 04 — Hybrid connectivity | Pending | Pending | Pending | Pending | Not deployed |
| 05 — Multi-region DR | Pending | Pending | Pending | Pending | Not deployed |
| 06 — ECS microservices | Pending | Pending | Pending | Pending | Not deployed |
| 07 — Serverless data lake | Pending | Pending | Pending | Pending | Not deployed |

## Latest Project 01 CI evidence

- Workflow: [Project 01 CI](https://github.com/SherifOracleDBA/Sherif2022/actions/workflows/project-01-ci.yml)
- Successful run: [Run #16 — 41435861425](https://github.com/SherifOracleDBA/Sherif2022/actions/runs/41435861425)
- Python unit tests: passed.
- Terraform format check: passed.
- Terraform init with no backend: passed.
- Terraform validate: passed.

Earlier runs on earlier commits remain visible as failed historical records. The successful run above validates the current CI workflow and the commit it checked.

## Project 01 scope committed

- Terraform starter: VPC, public/private subnets, Internet Gateway, NAT Gateway, security groups, ALB, launch template, ASG, CPU target tracking, private RDS PostgreSQL, WAF, CloudFront, optional Route 53 alias, CloudWatch dashboard/alarms, and SNS.
- Application: dependency-free Python web app with health, home, and cacheable static CSS routes.
- Tests: four Python unit tests and a deployed endpoint smoke test.
- Automation: GitHub Actions workflow for Python tests and Terraform formatting/validation.

## Project 01 limitations still to close

- AWS deployment has not been performed.
- The RDS instance is provisioned, but the demo web app is not yet connected using a dedicated least-privilege database user.
- CloudFront-to-ALB origin traffic currently uses HTTP. Enable origin TLS before production use.
- The starter uses one NAT Gateway and defaults RDS Multi-AZ off to reduce lab costs. Use one NAT per AZ and enable Multi-AZ for the high-availability exercise.
- The deployed endpoint smoke test, scale-out, instance replacement, WAF behavior, SSM access, and teardown still need live AWS evidence.

## Completion gates

1. Infrastructure code committed with pinned provider/tool versions.
2. Application code committed.
3. Unit, integration, and smoke tests pass.
4. Terraform format/init/validate/plan pass.
5. AWS deployment succeeds in a named test account.
6. Functional, security, availability, and failure tests pass.
7. Teardown is completed and remaining billable resources are reviewed.

## Recommended implementation order

Complete Project 01 end-to-end before moving to Projects 02–07. Reuse its repository layout, test approach, and CI workflow for subsequent projects.

**No production readiness, HA, security compliance, or DR claim is made until the corresponding tests and deployment evidence exist.**
