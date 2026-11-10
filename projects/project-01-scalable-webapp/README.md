# Project 01 — Scalable Web Application with ALB and Auto Scaling

**Architecture:** EC2-based, multi-AZ application with private compute and database tiers  
**Infrastructure:** Terraform  
**Application:** Python + PostgreSQL  
**Current stage:** Assessment-focused infrastructure and database integration implemented in code. Live AWS deployment, failover, scaling, and security evidence remain to be collected.

## 1. Solution architecture

~~~mermaid
flowchart TB
    Users[Users] --> DNS[Route 53 - optional CloudFront alias]
    DNS --> CF[CloudFront - HTTPS viewer]
    CF --> WAF[AWS WAF on ALB]
    HC[Route 53 health checker] -->|HTTP /health| ALB[Public ALB]
    WAF --> ALB
    ALB --> AppA[EC2 / ASG - private app subnet AZ A]
    ALB --> AppB[EC2 / ASG - private app subnet AZ B]
    AppA --> DB[(Private PostgreSQL RDS - Multi-AZ)]
    AppB --> DB
    AppA --> SSM[Systems Manager]
    AppB --> SSM
    AppA --> Secrets[Secrets Manager - app-only DB secret]
    AppB --> Secrets
    AppA --> NATa[NAT Gateway AZ A]
    AppB --> NATb[NAT Gateway AZ B]
    AppA --> CW[CloudWatch metrics / alarms]
    AppB --> CW
    ASG[Target tracking + step scaling] --> CW
    CW --> SNS[SNS notifications]
~~~

The VPC is split across two Availability Zones. Each AZ contains a public subnet, private application subnet, and private database subnet. Application instances have no public IP addresses. The public ALB is the only application ingress point.

CloudFront is the normal public application entry point. The ALB WAF requires a secret `X-Origin-Verify` header for application routes. The `/health` endpoint is the only path allowed without that header so Route 53 health checkers can reach it. Direct requests to other ALB paths without the CloudFront header are blocked by WAF.

## 2. Assessment requirements mapped to implementation

| Requirement | Implementation |
|---|---|
| VPC, public/private subnets, route tables | Two AZs; public, app-private, and DB-private tiers |
| NAT Gateway | One NAT Gateway per AZ by default; optional one-NAT cost mode |
| Security Groups and NACLs | ALB, app, and DB security groups plus separate public/app/DB network ACLs |
| EC2 and Auto Scaling | Launch Template, private ASG, ELB health checks |
| Target tracking | ASG average CPU target of 50% |
| Step scaling | Adds one instance after average ASG CPU is at least 75% for two 60-second periods |
| ALB and health checks | ALB forwards to port 8080; target health path is `/health` |
| WAF | CloudFront origin-header protection, AWS managed common rule set in blocking mode, and IP rate limiting |
| CloudFront | HTTPS for viewers; `/static/*` is cached; dynamic responses are not cached |
| RDS Multi-AZ | PostgreSQL Multi-AZ is enabled by default |
| Route 53 | ALB `/health` health check is created; optional A-alias to ALB requires an owned public hosted zone and `alb_domain_name` |
| Systems Manager | EC2 instance profile uses `AmazonSSMManagedInstanceCore`; no SSH/bastion is required |
| CloudWatch and SNS | Dashboard, CPU and unhealthy-target alarms, step-scaling alarm, and SNS notification topic |

## 3. Repository layout

~~~text
project-01-scalable-webapp/
├── README.md
├── application/
│   ├── requirements.txt
│   └── web/app.py
├── infrastructure/terraform/
│   ├── versions.tf
│   ├── variables.tf
│   ├── main.tf
│   ├── dashboard.tf
│   ├── outputs.tf
│   ├── user_data.sh.tftpl
│   └── terraform.tfvars.example
├── scripts/
│   ├── bootstrap-db-user.sh
│   └── bootstrap-db-user.sql
└── tests/
    ├── test_app.py
    └── smoke_test.py
~~~

## 4. Security and database design

- EC2 instances use IMDSv2, encrypted EBS, a dedicated instance profile, and Systems Manager.
- The application role can retrieve only the application database secret. It does not have permission to retrieve the RDS master secret.
- RDS manages the master password in Secrets Manager.
- Terraform generates a separate random application password and stores it in a separate Secrets Manager secret. The secret value is never exposed as a Terraform output.
- The application retrieves its secret at runtime using its instance role and connects to PostgreSQL with TLS required.
- A one-time SQL bootstrap creates the `portfolio_app` database role and the `app.visits` table. Run it from an operator workstation through an SSM remote-host port forward. Do not grant the application the master DB credentials.
- NACLs are stateless. The rules explicitly allow ALB-to-app traffic, app-to-database traffic, return ephemeral ports, and outbound web access through NAT. Security Groups provide the narrower stateful workload boundaries.

The web application provides:
- `GET /` — demonstration page.
- `GET /health` — process/ALB health endpoint; does not depend on the database.
- `GET /database` — verifies PostgreSQL connectivity.
- `POST /visits` — inserts a non-personal demonstration visit into `app.visits`.
- `GET /static/style.css` — cacheable static asset.

## 5. Cost and configuration notes

The assessment-oriented defaults enable **two NAT Gateways** and **RDS Multi-AZ**. These improve Availability Zone resilience but increase hourly charges. ALB, WAF, CloudFront, Route 53 health checks, data transfer, RDS, NAT Gateways, and EC2 can all incur costs.

For a temporary low-cost code-only plan, you may set:
~~~hcl
nat_gateway_per_az = false
db_multi_az        = false
~~~
That configuration is a cost-saving mode and must not be presented as the Multi-AZ/high-availability assessment deployment.

## 6. Prerequisites

- AWS CLI v2 and a named profile using IAM Identity Center/SSO or another short-lived credential source.
- Terraform 1.9+.
- Python 3.12+ for local tests.
- Git.
- For the database bootstrap: Session Manager plugin, `psql`, and `jq` on the operator workstation.
- An AWS account with billing alerts enabled and permissions to create VPC, EC2, Auto Scaling, ELB, RDS, IAM, Secrets Manager, WAF, CloudFront, Route 53, CloudWatch, SNS, and SSM resources.
- An owned Route 53 public hosted zone and valid certificate ARNs only if using custom DNS names.

## 7. Configure AWS credentials

Example with IAM Identity Center:

~~~bash
aws configure sso --profile aws-lab
aws sso login --profile aws-lab
aws sts get-caller-identity --profile aws-lab
export AWS_PROFILE=aws-lab
export AWS_REGION=us-east-1
~~~

Do not create or commit long-lived access keys.

## 8. Configure Terraform

From the Terraform directory:

~~~bash
cd projects/project-01-scalable-webapp/infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
~~~

Generate a unique origin-header secret:

~~~bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
~~~

Paste it into local `terraform.tfvars` as `origin_verify_header`. Do not commit `terraform.tfvars`; the repository `.gitignore` excludes it.

Assessment defaults are:
~~~hcl
db_multi_az        = true
nat_gateway_per_az = true
~~~

### Optional DNS and TLS settings

- `domain_name`: CloudFront custom hostname. Requires `hosted_zone_id` and an issued ACM certificate in **us-east-1** in `cloudfront_certificate_arn`.
- `alb_domain_name`: optional Route 53 A-alias to the ALB for the assessment's ALB DNS/health-check requirement. Requires `hosted_zone_id`.
- `alb_certificate_arn`: optional issued ACM certificate in the **ALB Region**, covering `alb_domain_name`. When supplied, CloudFront connects to the ALB using HTTPS-only origin communication. Without it, the CloudFront-to-ALB origin connection uses HTTP.
- `alarm_email`: optional SNS email recipient. Confirm the subscription email after deployment.

The Route 53 ALB health check is created against the ALB DNS name and `/health` even when no custom domain is configured. The Route 53 ALB alias record is created only when you own a hosted zone and set `alb_domain_name`.

## 9. Format, initialize, validate, and review

~~~bash
terraform fmt -recursive
terraform init
terraform validate
terraform plan -out=tfplan
terraform show tfplan
~~~

Review the plan before applying. Confirm the Region, two AZs, six subnets, two NAT Gateways, Multi-AZ RDS, NACLs, WAF, step-scaling alarm, Secrets Manager resources, and expected monthly/hourly cost.

## 10. Deploy

~~~bash
terraform apply tfplan
terraform output
~~~

CloudFront deployment and DNS propagation can take time. Confirm any SNS email subscription. Save the Terraform outputs for the verification steps below; do not publish secret values or state files.

## 11. Bootstrap the least-privilege application database account

Terraform creates the RDS-managed master secret and a separate application secret. The database role/table are created once by the operator, not by EC2 user data.

First, get one in-service EC2 instance and start an SSM port forward to the private RDS endpoint. Run this from the Terraform directory:

~~~bash
ASG_NAME=$(terraform output -raw autoscaling_group_name)
INSTANCE_ID=$(aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names "$ASG_NAME" \
  --query 'AutoScalingGroups[0].Instances[?LifecycleState==`InService`].InstanceId | [0]' \
  --output text)
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)

aws ssm start-session \
  --target "$INSTANCE_ID" \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters "{\"host\":[\"$RDS_ENDPOINT\"],\"portNumber\":[\"5432\"],\"localPortNumber\":[\"15432\"]}"
~~~

Keep that session running. In a second terminal from the repository root, run:

~~~bash
export AWS_REGION=us-east-1
export MASTER_SECRET_ARN="$(cd projects/project-01-scalable-webapp/infrastructure/terraform && terraform output -raw rds_master_secret_arn)"
export APP_SECRET_ARN="$(cd projects/project-01-scalable-webapp/infrastructure/terraform && terraform output -raw rds_app_secret_arn)"
bash projects/project-01-scalable-webapp/scripts/bootstrap-db-user.sh
~~~

The script retrieves both secret payloads without printing them, connects to the local forwarded port as the RDS master user, and runs the idempotent SQL bootstrap. Only the application secret ARN is available to the EC2 role.

## 12. Validate application and infrastructure

Run local unit tests from the repository root:

~~~bash
python -m pip install -r projects/project-01-scalable-webapp/application/requirements.txt
PYTHONPATH=projects/project-01-scalable-webapp/application \
  python -m unittest discover -s projects/project-01-scalable-webapp/tests -p "test_*.py" -v
~~~

Run deployed application and database smoke tests after the DB bootstrap:

~~~bash
APP_URL=$(cd projects/project-01-scalable-webapp/infrastructure/terraform && terraform output -raw application_url)
python projects/project-01-scalable-webapp/tests/smoke_test.py \
  --url "$APP_URL" --check-database --create-visit
~~~

Also verify and save sanitized evidence for:

1. ALB target group has at least two healthy targets in separate AZs.
2. EC2 instances have no public IPs and are in private app subnets.
3. SSM Session Manager works without SSH.
4. RDS is not publicly accessible, is Multi-AZ, and accepts PostgreSQL only from the app security group.
5. `/database` succeeds and `POST /visits` inserts a row.
6. WAF blocks a direct ALB request to `/` without the origin header but allows `/health`; CloudFront application requests succeed.
7. Route 53 health check reports healthy. When configured, the ALB A-alias uses the health check.
8. `/static/style.css` is cacheable; dynamic pages and database endpoints are not cached.
9. CloudWatch dashboard and alarms exist; SNS email is confirmed.
10. ASG replaces a terminated instance and target tracking and step scaling can be demonstrated under controlled load.
11. RDS failover behavior is tested and documented during an approved test window.

## 13. WAF operating mode

The managed AWS common rule group is configured in blocking mode for the assessment. Review WAF sampled requests and metrics after deployment. If the demo workload triggers false positives, temporarily change the managed rule group's `override_action` from `none {}` to `count {}`, review the result, then restore blocking mode and capture the evidence.

The custom origin-header protection remains active in either mode. Only `/health` is exempted so Route 53 can evaluate the ALB endpoint.

## 14. Destroy and verify cleanup

After collecting assessment evidence:

~~~bash
terraform destroy
~~~

Confirm CloudFront, ALB, NAT Gateways/EIPs, EC2/ASG, RDS, Secrets Manager secrets, subnets, NACLs, security groups, and VPC resources are removed. Review retained snapshots and any other billable resources separately. Preserve only the sanitized assessment evidence you need.

## 15. CI and definition of done

GitHub Actions at `.github/workflows/project-01-ci.yml` installs the application dependencies, runs Python unit tests, and runs Terraform format, init, and validate checks. The deployed smoke test and AWS acceptance tests require a live deployment.

- [ ] Architecture diagram and complete README are in the public GitHub repository.
- [ ] Terraform format, init, and validate pass in CI.
- [ ] Python unit and database-route tests pass in CI.
- [ ] Terraform plan is reviewed and approved.
- [ ] AWS deployment succeeds from a clean checkout.
- [ ] Two healthy ALB targets run in separate AZs.
- [ ] Multi-AZ RDS is enabled and failover is tested.
- [ ] NACLs, Security Groups, and WAF are verified.
- [ ] Target tracking and step scaling are demonstrated.
- [ ] App uses the least-privilege database user and app-only secret.
- [ ] Route 53 ALB health check is healthy; ALB alias is configured when a hosted zone/domain is available.
- [ ] SSM, CloudWatch, SNS, CloudFront caching, and smoke tests are verified.
- [ ] Teardown and post-destroy cost review are recorded.

**Do not claim production readiness or successful live HA until the AWS deployment and corresponding test evidence exist.**


## 16. Graduation submission pack

The project now includes an editable architecture source and a structured evidence pack:

- **Solution Architecture Diagram:** [Editable draw.io diagram](architecture/solution-architecture.drawio), [Mermaid source](architecture/solution-architecture.mmd), and [architecture notes](architecture/README.md).
- **GitHub documentation:** this README documents the solution, AWS services, deployment, security, validation, and cleanup.
- **Deployment procedure:** [Deployment Runbook](docs/DEPLOYMENT-RUNBOOK.md).
- **Assessment test cases:** [Validation and Acceptance Matrix](docs/VALIDATION-MATRIX.md).
- **Evidence tracking:** [Assessment Evidence Register](docs/ASSESSMENT-EVIDENCE.md).
- **Cost and teardown:** [Cost and Cleanup Controls](docs/COST-AND-CLEANUP.md).

### Current submission status

| Deliverable | Status |
|---|---|
| Architecture diagram source | Committed; export PNG/SVG for final upload |
| README and technical documentation | Committed; update with actual deployment outputs after testing |
| Terraform and application code | Committed; CI validation previously passed |
| Live AWS deployment | Not yet performed |
| Runtime acceptance evidence | Not yet collected |
| Optional live URL / demo recording | Pending successful deployment |

The architecture and documentation describe the intended solution. They must not be presented as proof of live AWS deployment. Complete the evidence register only after each test has actually passed.
