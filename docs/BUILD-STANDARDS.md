# Build Standards and AWS Safety Rules

These standards apply to all projects in this repository.

## 1. Standard lifecycle

1. Plan: confirm use case, architecture, Region, CIDRs, prerequisites, and expected cost.
2. Design: create an architecture diagram and record key decisions.
3. Build: implement infrastructure in small layers; review every change.
4. Deploy: use a named AWS CLI profile and an explicit Region.
5. Validate: test happy path, failure path, permissions, logging, scaling, or recovery behavior.
6. Document: record sanitized outputs, test results, limitations, and teardown evidence.
7. Destroy: remove resources in dependency order and verify that no lab resources remain.

## 2. Suggested toolchain

- AWS CLI v2
- Terraform for infrastructure-as-code labs
- AWS CDK or CloudFormation where appropriate
- Git and GitHub
- Python or Node.js for Lambda and helper code
- Docker for the ECS project
- Mermaid diagrams in Markdown
- Shell scripts for repeatable validation and cleanup

Pin tool and provider versions in each implementation. Avoid unbounded latest dependencies.

## 3. Credentials and IAM

- Never place access keys, passwords, JWTs, database strings, or private keys in source code.
- Prefer IAM Identity Center/SSO or short-lived credentials for human access.
- Use a dedicated deployment role with only the permissions needed by the current project.
- Use instance profiles, Lambda execution roles, and ECS task roles for workloads. Do not pass long-lived AWS keys into user data, Lambda environment variables, or containers.
- Separate ECS task execution roles from application task roles.
- Store application secrets in Secrets Manager or encrypted SSM Parameter Store, not Git.
- Add secret scanning to the GitHub workflow.

## 4. Terraform and configuration

- Use remote state with encryption, access control, and locking for shared/team use.
- For a solo lab, local state may be used temporarily but must never be committed.
- Ignore Terraform state, .terraform directories, tfvars, plan files, and generated artifacts.
- Commit example variable files with placeholders only.
- Review terraform plan before terraform apply.
- Tag resources with Project, Environment, Owner, and ManagedBy.
- Never output passwords or secret values. Terraform state can contain sensitive values even when variables are marked sensitive.

## 5. Network and security defaults

- Use private subnets for application and data tiers wherever possible.
- Limit database security groups to the exact application security group.
- Prefer Systems Manager Session Manager over public SSH.
- Enable encryption at rest and in transit where supported.
- Enable CloudTrail and relevant service logs; redact tokens, passwords, PII, and unnecessary request bodies.
- Do not expose administrative ports to the world.
- Validate public entry points with security groups, WAF, and origin protection where relevant.

## 6. Cost guardrails

Before deployment, set a budget and billing alert; choose one Region unless the project requires more; use small sizes and short test windows; estimate always-on costs; identify hourly resources such as NAT Gateways, ALBs, RDS, Transit Gateway, VPN, ElastiCache, and interface endpoints; and add a destroy checklist.

After testing, inspect billing and resource inventory. DNS records and S3 objects can remain after compute resources are deleted.

## 7. Testing evidence

Each project should include unit tests, infrastructure validation, smoke tests, at least one negative test, and a failure/recovery test where relevant. Record expected result, actual result, and evidence location.

Never claim HA, failover, DR, or security compliance merely because resources were created.

## 8. GitHub workflow

- main: reviewed baseline.
- feature/project-xx-* branches: project changes.
- Use pull requests for meaningful infrastructure changes.
- Include plan and test results in PR descriptions.
- Never upload state files, credentials, customer data, or screenshots containing secrets.

Recommended checks: Markdown lint, Terraform format/validate, unit tests, secret scanning, infrastructure security scanning, and manual approval before AWS deployment. Do not allow unrestricted deployment or destruction from every pull request.
