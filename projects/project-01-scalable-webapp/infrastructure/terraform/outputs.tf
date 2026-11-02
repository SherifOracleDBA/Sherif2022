output "application_url" {
  description = "CloudFront application URL."
  value       = var.domain_name == "" ? "https://${aws_cloudfront_distribution.app.domain_name}" : "https://${var.domain_name}"
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution identifier."
  value       = aws_cloudfront_distribution.app.id
}

output "alb_dns_name" {
  description = "ALB origin DNS name. Direct origin requests are restricted by security group and WAF."
  value       = aws_lb.app.dns_name
}

output "autoscaling_group_name" {
  description = "Auto Scaling group name."
  value       = aws_autoscaling_group.app.name
}

output "rds_endpoint" {
  description = "Private PostgreSQL endpoint."
  value       = aws_db_instance.main.address
}

output "rds_master_secret_arn" {
  description = "ARN of the RDS-managed master credential secret. Secret value is never output."
  value       = try(aws_db_instance.main.master_user_secret[0].secret_arn, null)
}

output "rds_app_secret_arn" {
  description = "ARN of the generated least-privilege application database secret. Secret value is never output."
  value       = aws_secretsmanager_secret.app_db.arn
}

output "alb_route53_health_check_id" {
  description = "Route 53 health check ID for the ALB /health endpoint."
  value       = aws_route53_health_check.alb.id
}

output "alb_route53_name" {
  description = "Optional Route 53 ALB alias name."
  value       = var.alb_domain_name == "" ? null : var.alb_domain_name
}

output "nat_gateway_ids" {
  description = "NAT Gateway IDs, one per AZ by default."
  value       = { for az, nat in aws_nat_gateway.main : az => nat.id }
}

output "sns_alert_topic_arn" {
  description = "SNS topic ARN for CloudWatch alarms."
  value       = aws_sns_topic.alerts.arn
}

output "cloudwatch_dashboard_name" {
  description = "CloudWatch dashboard name."
  value       = aws_cloudwatch_dashboard.app.dashboard_name
}

output "vpc_id" {
  description = "VPC identifier."
  value       = aws_vpc.main.id
}
