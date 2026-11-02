variable "aws_region" {
  description = "AWS Region for the workload."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Short project identifier used in resource names."
  type        = string
  default     = "aws-portfolio-p01"
}

variable "environment" {
  description = "Environment name."
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "IPv4 CIDR for the VPC. Must be large enough for six /24 subnets."
  type        = string
  default     = "10.20.0.0/16"
}

variable "instance_type" {
  description = "EC2 instance type for the Auto Scaling group."
  type        = string
  default     = "t3.micro"
}

variable "min_size" {
  description = "Minimum number of EC2 instances."
  type        = number
  default     = 2
}

variable "desired_capacity" {
  description = "Desired number of EC2 instances."
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Maximum number of EC2 instances."
  type        = number
  default     = 4
}

variable "db_instance_class" {
  description = "RDS DB instance class. Small classes are for learning workloads only."
  type        = string
  default     = "db.t4g.micro"
}

variable "db_name" {
  description = "Initial PostgreSQL database name."
  type        = string
  default     = "portfolio"
}

variable "db_username" {
  description = "RDS master username. RDS manages and stores its password in Secrets Manager."
  type        = string
  default     = "portfolio_admin"
}

variable "db_multi_az" {
  description = "Enable RDS Multi-AZ for the assessment high-availability design."
  type        = bool
  default     = true
}

variable "nat_gateway_per_az" {
  description = "Create one NAT Gateway per Availability Zone for resilient private-subnet egress."
  type        = bool
  default     = true
}

variable "app_db_username" {
  description = "Least-privilege PostgreSQL application account; bootstrapped separately from the RDS master account."
  type        = string
  default     = "portfolio_app"

  validation {
    condition     = can(regex("^[a-zA-Z_][a-zA-Z0-9_]{0,62}$", var.app_db_username))
    error_message = "app_db_username must be a valid PostgreSQL role name with at most 63 characters."
  }
}

variable "alb_domain_name" {
  description = "Optional Route 53 hostname aliasing directly to the ALB for the assessment health-check exercise."
  type        = string
  default     = ""
}

variable "alb_certificate_arn" {
  description = "Optional ACM certificate ARN in the ALB Region for HTTPS from CloudFront to the ALB. Requires alb_domain_name."
  type        = string
  default     = ""

  validation {
    condition     = var.alb_certificate_arn == "" || var.alb_domain_name != ""
    error_message = "alb_domain_name must be set when alb_certificate_arn is configured."
  }
}

variable "origin_verify_header" {
  description = "Long random value sent by CloudFront and required by the ALB WAF rule."
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.origin_verify_header) >= 32
    error_message = "origin_verify_header must contain at least 32 characters."
  }
}

variable "domain_name" {
  description = "Optional custom hostname for CloudFront, for example app.example.com."
  type        = string
  default     = ""
}

variable "hosted_zone_id" {
  description = "Route 53 public hosted zone ID. Required for configured CloudFront or ALB aliases."
  type        = string
  default     = ""

  validation {
    condition     = (var.domain_name == "" && var.alb_domain_name == "") || var.hosted_zone_id != ""
    error_message = "hosted_zone_id is required when domain_name or alb_domain_name is configured."
  }
}

variable "cloudfront_certificate_arn" {
  description = "ACM certificate ARN in us-east-1 for domain_name. Required when domain_name is set."
  type        = string
  default     = ""

  validation {
    condition     = var.domain_name == "" || var.cloudfront_certificate_arn != ""
    error_message = "cloudfront_certificate_arn is required when domain_name is configured."
  }
}

variable "alarm_email" {
  description = "Optional email address for SNS alarm notifications. Subscription must be confirmed."
  type        = string
  default     = ""
}

variable "deletion_protection" {
  description = "Enable RDS deletion protection. Keep false for disposable learning environments."
  type        = bool
  default     = false
}

variable "skip_final_snapshot" {
  description = "Skip final RDS snapshot on destroy. Use true only for disposable lab data."
  type        = bool
  default     = true
}
