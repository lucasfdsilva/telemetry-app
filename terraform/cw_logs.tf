resource "aws_cloudwatch_log_group" "ecs_task_logs" {
  name = "${local.prefix}-telemetry-app"

  tags = local.common_tags
}