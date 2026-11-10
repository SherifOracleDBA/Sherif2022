# Project 01 Deployment Runbook

## Purpose
Repeatable deployment and validation procedure for the Scalable Web Application graduation project.

## Safety gates before deployment
1. Confirm the AWS account and Region with `aws sts get-caller-identity` and `aws configure get region`.
2. Enable an AWS Budget or billing alert before creating resources.
3. Use IAM Identity Center/SSO or another short-lived credential mechanism. Never create or commit long-lived access keys.
4. Confirm the selected Region has at least two available AZs and supports the selected EC2/RDS instance types.
5. Review current Terraform variables and cost drivers. Assessment defaults create two NAT Gateways and Multi-AZ RDS.
6. Do not run `terraform apply` until the plan and expected cost have been reviewed.

## 1. Authenticate
```bash
aws configure sso --profile aws-lab
aws sso login --profile aws-lab
aws sts get-caller-identity --profile aws-lab
export AWS_PROFILE=aws-lab
export AWS_REGION=us-east-1
```

## 2. Configure Terraform
```bash
cd projects/project-01-scalable-webapp/infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
```

Generate a unique origin verification value and set it in the local, ignored `terraform.tfvars` file:
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Keep assessment settings enabled for final high-availability evidence:
```hcl
db_multi_az        = true
nat_gateway_per_az = true
```

Optional custom DNS requires an owned Route 53 public hosted zone. CloudFront custom hostnames require an ACM certificate in us-east-1; HTTPS from CloudFront to the ALB requires an ALB-region ACM certificate and matching ALB hostname.

## 3. Initialize and inspect the plan
```bash
terraform fmt -recursive
terraform init
terraform validate
terraform plan -out=tfplan
terraform show tfplan
```

Review every resource, Region, subnet, security boundary, IAM policy, WAF rule, RDS setting, NAT Gateway, and expected cost. Store plan files locally only; do not commit them.

## 4. Apply only after approval
```bash
terraform apply tfplan
terraform output
```

Wait for CloudFront deployment. Confirm any SNS email subscription. Save sanitized resource identifiers and outputs; never publish secret values or Terraform state.

## 5. Bootstrap the application database role
Follow the complete SSM remote-host port-forward and database bootstrap instructions in the [Project 01 README](../README.md#11-bootstrap-the-least-privilege-application-database-account). This is a one-time operator task. Do not put master credentials in EC2 user data or the application role.

## 6. Run smoke tests
```bash
APP_URL=$(terraform output -raw application_url)
cd ../../../..
python -m pip install -r projects/project-01-scalable-webapp/application/requirements.txt
PYTHONPATH=projects/project-01-scalable-webapp/application \
  python -m unittest discover -s projects/project-01-scalable-webapp/tests -p "test_*.py" -v
python projects/project-01-scalable-webapp/tests/smoke_test.py \
  --url "$APP_URL" --check-database --create-visit
```

## 7. Capture evidence
Use the [validation matrix](VALIDATION-MATRIX.md) and [evidence register](ASSESSMENT-EVIDENCE.md). Capture timestamps, test commands, sanitized outputs, and AWS Console screenshots. Redact all secrets, tokens, and customer data.

## 8. Destroy and verify cleanup
After collecting required evidence:
```bash
cd projects/project-01-scalable-webapp/infrastructure/terraform
terraform destroy
```

Verify EC2/ASG, ALB, CloudFront, NAT Gateways/EIPs, RDS, Secrets Manager secrets, Route 53 health checks/records, CloudWatch resources, SNS resources, and VPC networking resources are removed when no longer needed. Check retained snapshots and other billable resources separately.

## Deployment status
No live deployment is claimed by this runbook. Mark deployment and runtime tests complete only after collecting evidence from the learner's AWS account.
