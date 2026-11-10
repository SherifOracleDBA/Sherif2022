# Project 01 Architecture Assets

This folder contains the editable architecture source for the graduation submission.

- [Solution architecture (draw.io)](solution-architecture.drawio) — editable diagram. Open it with https://app.diagrams.net/.
- [Solution architecture (Mermaid)](solution-architecture.mmd) — text-based source also embedded in the project README.

## Diagram notes

- The ALB is internet-facing and spans the two public subnets.
- EC2 instances are deployed only in private application subnets across two Availability Zones.
- RDS PostgreSQL is deployed in private database subnets with Multi-AZ enabled by default.
- CloudFront is the public application entry point. The Regional WAF Web ACL is associated with the ALB and validates the CloudFront origin-verification header for application paths.
- Route 53 health check probes the ALB /health endpoint. Custom DNS aliases require a hosted zone owned by the learner.
- NAT Gateways provide outbound connectivity for private application instances; the assessment default is one per AZ.
- Systems Manager, Secrets Manager, CloudWatch, and SNS provide operations, credentials, monitoring, and notifications.

The diagram describes the intended Terraform architecture. It is not evidence that the stack has been deployed or verified in an AWS account.
