# AWS Cloud Engineering Portfolio

A hands-on portfolio of seven AWS projects. Each project is an independent learning lab with an architecture, implementation phases, validation checklist, cost notes, and cleanup guide.

> Learning portfolio, not a production-ready turnkey deployment. The guides define the build sequence. Infrastructure code, application code, tests, and deployment automation should be implemented and validated project by project.

## Projects

| # | Project | Architecture | Main services |
|---|---|---|---|
| 01 | [Scalable Web Application](projects/project-01-scalable-webapp/README.md) | EC2 / multi-AZ | VPC, EC2, ALB, ASG, WAF, CloudFront, RDS, Route 53, SSM, CloudWatch |
| 02 | [Serverless Image Processing](projects/project-02-image-processing/README.md) | Event-driven serverless | S3, SQS, DLQ, Lambda, Step Functions, API Gateway, DynamoDB, CloudFront, SNS |
| 03 | [Serverless REST API with Cognito](projects/project-03-serverless-api-cognito/README.md) | Serverless API | API Gateway, Cognito, Lambda, DynamoDB, WAF, CloudFront, X-Ray |
| 04 | [Hybrid Cloud Connectivity](projects/project-04-hybrid-network/README.md) | Hybrid networking | VPC, Transit Gateway, Site-to-Site VPN, Route 53 Resolver, RAM, Network Firewall |
| 05 | [Multi-Region Disaster Recovery](projects/project-05-multi-region-dr/README.md) | Warm standby | Route 53, Aurora Global Database, S3 CRR, DynamoDB Global Tables, EC2/ASG, Backup |
| 06 | [Containerized Microservices](projects/project-06-ecs-microservices/README.md) | Containers | ECS Fargate, ECR, ALB, Cloud Map, Secrets Manager, Redis, CodePipeline, CodeDeploy |
| 07 | [Serverless Data Lake](projects/project-07-serverless-data-lake/README.md) | Data & analytics | S3, Kinesis Data Firehose, Glue, Athena, Lake Formation, QuickSight, EventBridge, KMS |

Project 08 from the original idea list (security monitoring with GuardDuty, Security Hub, KMS, and Config) is intentionally excluded from this seven-project sequence. It can be added as a separate security capstone later.

## Repository layout

~~~text
.
├── README.md
├── docs/
│   └── BUILD-STANDARDS.md
└── projects/
    ├── project-01-scalable-webapp/
    ├── project-02-image-processing/
    ├── project-03-serverless-api-cognito/
    ├── project-04-hybrid-network/
    ├── project-05-multi-region-dr/
    ├── project-06-ecs-microservices/
    └── project-07-serverless-data-lake/
~~~

Each project will grow toward this implementation layout:

~~~text
project-xx/
├── README.md
├── docs/
├── infrastructure/
├── application/
├── tests/
└── scripts/
~~~

README.md documents the architecture and steps; docs holds diagrams, runbooks, evidence; infrastructure holds Terraform/CDK/CloudFormation; application contains the workload; tests contains unit, integration, and smoke tests; scripts contains repeatable deploy, validate, and destroy helpers.

## Recommended build order

1. Complete Project 01 first to establish networking, IAM, compute, load balancing, monitoring, and deployment skills.
2. Build Projects 02 and 03 for asynchronous serverless workflows and authenticated APIs.
3. Build Project 04 as a standalone networking lab. It requires a reachable VPN peer or a clearly labeled simulation.
4. Build Project 05 after Project 01 so the application pattern can be reused in a second Region.
5. Build Project 06 to practice containers and blue/green delivery.
6. Build Project 07 after understanding IAM, S3, encryption, and event-driven ingestion.

## Prerequisites

- AWS account with billing alerts enabled.
- AWS CLI v2 and a named profile using short-lived credentials.
- Git, Terraform, and the runtime listed by each project.
- Basic understanding of IAM, VPCs, subnets, security groups, DNS, and Linux.
- GitHub account and Git installed locally.

## Start here

1. Read [Build standards and AWS safety rules](docs/BUILD-STANDARDS.md).
2. Open a project README.
3. Follow its phases in order.
4. Save sanitized outputs and test evidence in that project's docs folder.
5. Run cleanup and verify billable resources are removed.

## Safety and cost

- Never commit AWS keys, passwords, JWTs, private keys, or real customer data.
- Prefer IAM Identity Center or short-lived role credentials and a least-privilege deployment role.
- Start with small instance/database sizes and short test windows.
- NAT Gateways, ALBs, RDS, Transit Gateway, VPN, ElastiCache, replication, processing, and QuickSight can incur charges even with little traffic.
- Build and destroy one lab at a time.
- Successful resource creation alone does not prove production readiness.

## Reference style

The organization is inspired by [AWS's Dynamic Image Transformation for Amazon CloudFront repository](https://github.com/aws-solutions/dynamic-image-transformation-for-amazon-cloudfront): overview, architecture, deployment/source separation, tests, and operational documentation. This is an independent learning portfolio, not an AWS-owned solution.
