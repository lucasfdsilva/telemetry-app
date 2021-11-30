data "aws_route53_zone" "zone" {
  name = "${var.dns_zone_name}."
}

resource "aws_route53_record" "telemetry_app" {
  zone_id = data.aws_route53_zone.zone.zone_id
  name    = join("", [lookup(var.subdomain, terraform.workspace), data.aws_route53_zone.zone.name])
  type    = "CNAME"
  ttl     = "300"

  records = [aws_lb.telemetry_app.dns_name]
}

resource "aws_acm_certificate" "cert" {
  domain_name       = aws_route53_record.telemetry_app.fqdn
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = local.common_tags
}

resource "aws_route53_record" "cert_validation" {
  name    = aws_acm_certificate.cert.domain_validation_options.0.resource_record_name
  type    = aws_acm_certificate.cert.domain_validation_options.0.resource_record_type
  zone_id = data.aws_route53_zone.zone.zone_id

  records = [
    aws_acm_certificate.cert.domain_validation_options.0.resource_record_value
  ]

  ttl = "60"
}

#Not an actual TF resource. Used to trigger the cert validation
resource "aws_acm_certificate_validation" "cert" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [aws_route53_record.cert_validation.fqdn]
}