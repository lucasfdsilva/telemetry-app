output "telemetry_app_endpoint" {
  value = aws_route53_record.telemetry_app.fqdn
}