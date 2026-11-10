# Project 01 Assessment Evidence Register

This is the evidence index for the graduation submission. Keep screenshots and sanitized text outputs in this folder or a linked evidence location. Never commit Terraform state, plan files, passwords, access keys, secret values, session tokens, or personal/customer data.

## Evidence status

| Evidence ID | Deliverable / test | Status | Evidence file / URL | Date | Notes |
|---|---|---|---|---|---|
| ARCH-01 | Solution architecture diagram | READY - source committed | [draw.io source](../architecture/solution-architecture.drawio) | 2026-11-10 | Editable diagram; architecture also appears in project README |
| DOC-01 | Project documentation / README | READY - draft | [Project README](../README.md) | 2026-11-10 | Review after live deployment for actual outputs |
| CI-01 | GitHub Actions / Terraform validation | PASS - historical run | [Workflow run #45](https://github.com/SherifOracleDBA/Sherif2022/actions/runs/42809046273) | 2026-11-10 | 8 unit tests and Terraform fmt/init/validate passed for commit 8055f5a |
| AWS-01 | Terraform deployment | NOT RUN | — | — | Requires learner AWS account and plan/cost approval |
| APP-01 | ALB target health across AZs | NOT RUN | — | — | Capture target health output |
| DB-01 | RDS Multi-AZ and application DB test | NOT RUN | — | — | Run DB bootstrap and smoke tests |
| SCALE-01 | Target tracking and step scaling | NOT RUN | — | — | Use controlled load and record ASG activity |
| SEC-01 | WAF, SSM, least privilege | NOT RUN | — | — | Capture WAF sample, SSM session, and IAM evidence |
| CDN-01 | CloudFront HTTPS and static caching | NOT RUN | — | — | Capture response headers / cache behavior |
| MON-01 | CloudWatch dashboard and SNS alert | NOT RUN | — | — | Confirm SNS subscription and test alert |
| DR-01 | RDS planned failover | NOT RUN | — | — | Perform only in an approved test window |
| CLEAN-01 | Terraform destroy and cost review | NOT RUN | — | — | Confirm no leftover billable resources |

## Evidence capture checklist
- [ ] Export the draw.io diagram as PNG or SVG and add it to this folder.
- [ ] Terraform plan reviewed; no secret values included in evidence.
- [ ] Deployment outputs recorded with sensitive values removed.
- [ ] Two healthy ALB targets in separate Availability Zones.
- [ ] EC2 instances confirmed in private subnets with no public IP addresses.
- [ ] RDS confirmed private and Multi-AZ.
- [ ] Database health and write smoke tests passed.
- [ ] SSM session opened without SSH.
- [ ] WAF origin verification and managed rule behavior demonstrated.
- [ ] Target tracking, step scaling, and instance replacement demonstrated.
- [ ] CloudFront HTTPS and static caching demonstrated.
- [ ] Route 53 health check verified; custom alias recorded if configured.
- [ ] CloudWatch dashboard and SNS email notification verified.
- [ ] RDS failover completed and application recovered.
- [ ] Terraform destroy completed and residual resources checked.

## Submission rule
The project is ready for final assessment only when all required items in the course rubric are supported by evidence. Optional live URL or demo video should be added only after a successful deployment and security review.
