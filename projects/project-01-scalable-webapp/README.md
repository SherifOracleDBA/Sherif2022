# Project 01 — Scalable Web Application with ALB and Auto Scaling

**Architecture:** EC2-based, multi-AZ application with private compute  
**Implementation:** Terraform + Python standard-library web app  
**Current stage:** Starter infrastructure and app code committed; validation and AWS deployment still required.

## Architecture

~~~mermaid
flowchart TD
    U[Users] --> R53[Optional Route 53 alias]
    R53 --> CF[CloudFront HTTPS]
    CF --> WAF[AWS WAF on regional ALB]
    WAF --> ALB[Public ALB]
    ALB --> EC2A[EC2 / ASG - private AZ A]
    ALB --> EC2B[EC2 / ASG - private AZ B]
    EC2A --> RDS[(Private RDS PostgreSQL)]
    EC2B --> RDS
    EC2A --> SSM[Systems Manager]
    EC2B --> SSM
    ASG[Auto Scaling] --> CW[CloudWatch dashboard and alarms]
    CW --> SNS[SNS notifications]
~~~

The ALB security group accepts traffic only from the AWS-managed CloudFront origin-facing prefix list. CloudFront adds a secret origin header, and AWS WAF blocks requests that do not contain the configured value. The managed common rule group starts in **count mode** so you can review false positives; a rate-based rule blocks excessive requests.

## Repository layout

~~~text
project-01-scalable-webapp/
├── README.md
├── application/web/app.py
├── infrastructure/terraform/
│   ├── versions.tf
│   ├── variables.tf
│   ├── main.tf
│   ├── dashboard.tf
│   ├── outputs.tf
│   ├── user_data.sh.tftpl
│   └── terraform.tfvars.example
└── tests/
    ├── test_app.py
    └── smoke_test.py
~~~

## What the initial Terraform stack creates

- VPC with two public, two private application, and two private database subnets across two AZs.
- Internet Gateway and one NAT Gateway for the learning environment.
- Security groups that restrict ALB → application → database traffic.
- Public ALB, target group, and health check on `/health`.
- EC2 launch template, encrypted EBS volume, IMDSv2 requirement, IAM instance profile, and Systems Manager access.
- EC2 Auto Scaling group across two private AZs with CPU target tracking.
- Private PostgreSQL RDS instance with encryption, backups, and an RDS-managed master password stored in Secrets Manager.
- Regional AWS WAF on the ALB with origin-header validation, managed common rules in count mode, and rate limiting.
- CloudFront distribution with HTTPS for viewers, disabled caching for dynamic responses, and managed caching for `/static/*`.
- Optional Route 53 alias record for a custom domain.
- CloudWatch dashboard, CPU/unhealthy-target alarms, and SNS topic with optional email subscription.

## Important starter limitations

This is a learning baseline, **not yet a production-ready deployment**:

1. NAT is deployed in one AZ to reduce lab cost. A resilient design should use one NAT Gateway per AZ or suitable VPC endpoints and routing.
2. The RDS instance is created and its master credential is managed by RDS/Secrets Manager, but the demo web application does not yet connect to the database. Add a separate least-privilege application DB user and schema migration before app-level database testing. Do not give the app the RDS master password.
3. CloudFront viewer traffic is HTTPS, but the initial CloudFront-to-ALB origin connection uses HTTP. For production, add an ALB HTTPS listener with a valid origin certificate and change CloudFront to HTTPS-only origin communication.
4. RDS Multi-AZ defaults to false to keep initial lab costs lower. Set `db_multi_az = true` for the HA exercise.
5. A custom hostname requires a Route 53 hosted zone and an ACM certificate in **us-east-1** for CloudFront.
6. CloudFront, ALB, NAT Gateway, RDS, and data transfer incur costs. Destroy the lab when finished.

## Prerequisites

- AWS CLI v2, Terraform 1.9+, Git, and Python 3.12+.
- An AWS account with billing alerts enabled.
- A named AWS CLI profile using IAM Identity Center/SSO or another short-lived credential source.
- Permission to create VPC, EC2, Auto Scaling, ELB, RDS, IAM, WAF, CloudFront, Route 53 (optional), CloudWatch, and SNS resources.

Check the AWS Provider release and pin range in `versions.tf`; this project currently uses the 6.71 provider line.

## Step 1 — Configure AWS credentials

Example with IAM Identity Center:

~~~bash
aws configure sso --profile aws-lab
aws sso login --profile aws-lab
aws sts get-caller-identity --profile aws-lab
~~~

Use the profile in subsequent commands:

~~~bash
export AWS_PROFILE=aws-lab
export AWS_REGION=us-east-1
~~~

Do not create or commit access keys for this project.

## Step 2 — Configure Terraform

~~~bash
cd projects/project-01-scalable-webapp/infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
~~~

Generate a unique origin-header value:

~~~bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
~~~

Paste the generated value into the local `terraform.tfvars` file as `origin_verify_header`. Do not commit that file. The root `.gitignore` excludes `*.tfvars`.

For the optional custom hostname, fill in all three values:
- `domain_name`: hostname to publish.
- `hosted_zone_id`: existing Route 53 public hosted zone ID.
- `cloudfront_certificate_arn`: ACM certificate ARN from us-east-1 that covers the hostname.

Keep the custom domain values empty to use the CloudFront-generated hostname.

To enable the database HA exercise, set:

~~~hcl
db_multi_az = true
~~~

This will increase the hourly database cost.

## Step 3 — Format, initialize, and review

~~~bash
terraform fmt -recursive
terraform init
terraform validate
terraform plan -out=tfplan
terraform show tfplan
~~~

Review the plan carefully. Check Region, subnet CIDRs, instance/database sizes, domain/certificate settings, and estimated cost before applying.

## Step 4 — Deploy

~~~bash
terraform apply tfplan
terraform output
~~~

The `application_url` output is the CloudFront URL (or configured custom hostname). CloudFront creation and propagation can take time. The SNS email subscription, when configured, requires confirmation from the recipient.

## Step 5 — Validate the app and infrastructure

From the repository root, run the unit tests:

~~~bash
python -m unittest discover -s projects/project-01-scalable-webapp/tests -p "test_*.py" -v
~~~

Run the deployed smoke test using the Terraform `application_url` output:

~~~bash
python projects/project-01-scalable-webapp/tests/smoke_test.py --url https://YOUR_CLOUDFRONT_DOMAIN
~~~

Also verify in the AWS Console/CLI:
- ALB target group reports two healthy instances in separate AZs.
- EC2 instances have no public IPs and are in private application subnets.
- Session Manager can connect without SSH.
- RDS is not publicly accessible and its security group allows only the application security group.
- WAF blocks requests without the origin header; inspect managed-rule count metrics before switching the managed group to block mode.
- `/static/style.css` is cacheable; `/health` and the dynamic home page are not cached.
- CloudWatch dashboard and alarms exist; SNS email is confirmed when used.
- Terminating one test instance results in ASG replacement.

## Step 6 — Enable managed-rule blocking only after review

After checking WAF sampled requests and metrics for false positives, change the managed common rule group's override action from:

~~~hcl
override_action {
  count {}
}
~~~

to:

~~~hcl
override_action {
  none {}
}
~~~

Then run `terraform plan` and apply the reviewed change.

## Step 7 — Destroy the lab

~~~bash
terraform destroy
~~~

Confirm that the CloudFront distribution, ALB, NAT Gateway/EIP, RDS instance, subnets, and VPC are removed. Review snapshots, CloudWatch logs, and other retained resources separately. Do not remove snapshots needed for recovery or evidence.

## CI and tests

The workflow at `.github/workflows/project-01-ci.yml` runs Python unit tests and Terraform formatting/validation on relevant pushes and pull requests. A green GitHub Actions run is required before marking code validation complete. The smoke test requires a deployed URL and is run separately.

## Definition of done

- [ ] Terraform format and validation pass in CI.
- [ ] Python unit tests pass in CI.
- [ ] Infrastructure deploys from a clean checkout.
- [ ] Two targets are healthy across AZs.
- [ ] Instance replacement and target-tracking behavior are demonstrated.
- [ ] WAF origin protection and managed rules are reviewed.
- [ ] SSM access works without SSH.
- [ ] Database connectivity is tested with a least-privilege app user (not the master account).
- [ ] Origin TLS is enabled before any production use.
- [ ] Smoke tests and teardown are recorded.
