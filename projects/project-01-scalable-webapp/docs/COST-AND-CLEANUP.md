# Project 01 Cost and Cleanup Controls

## Cost drivers
This architecture is intentionally high-availability oriented. The default configuration includes two NAT Gateways and Multi-AZ RDS. Other billable services include EC2 and EBS, ALB and capacity units, NAT Gateway hourly/data processing, RDS compute/storage/backups/I/O, CloudFront requests and transfer, WAF Web ACL/rules/requests, Route 53 health checks, CloudWatch metrics/alarms/dashboards/logs, and SNS notifications.

Actual charges depend on Region, duration, traffic, resource sizing, storage, and current AWS pricing. Use the AWS Pricing Calculator for a Region-specific estimate before deployment. This document is not a price quote.

## Cost review before apply
- Confirm Region and instance sizes.
- Confirm two NAT Gateways are required for assessment deployment.
- Confirm Multi-AZ RDS is required for assessment deployment.
- Estimate intended test duration.
- Check whether custom certificates, domains, WAF rules, and CloudFront traffic add cost.
- Review Terraform plan for unexpected resources.
- Create an AWS Budget / billing alert.
- Obtain approval before applying the plan.

## Temporary cost-saving mode
Terraform supports a single NAT Gateway and single-AZ RDS configuration:
```hcl
nat_gateway_per_az = false
db_multi_az        = false
```
This is suitable only for a temporary cost-controlled code or connectivity exercise. It does NOT satisfy the intended high-availability assessment configuration and must not be represented as a successful Multi-AZ demonstration.

## Cleanup
After exporting required evidence:
```bash
terraform destroy
```
Then inspect the AWS account for resources that may remain or be retained separately:
- RDS snapshots and automated backups.
- CloudWatch log groups or custom metrics.
- S3 objects if extensions add them.
- Elastic IP addresses and NAT Gateways.
- CloudFront distributions still deploying or disabled but not deleted.
- Route 53 records and health checks.
- Secrets Manager secrets pending deletion.
- Manually created ACM certificates, hosted zones, or SNS subscriptions.

Review AWS Cost Explorer / Billing after teardown to confirm no unexpected ongoing charges. Retain only sanitized evidence required for assessment.
