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
