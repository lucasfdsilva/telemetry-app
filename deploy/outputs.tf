output "telemetry_app_endpoint" {
  value = aws_lb.telemetry_app.dns_name
}