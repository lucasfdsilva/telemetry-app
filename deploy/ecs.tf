resource "aws_ecs_cluster" "main" {
  name = "${local.prefix}-cluster"

  tags = local.common_tags
}

resource "aws_iam_policy" "task_definition_role_policy" {
  name        = "${local.prefix}-task-exec-role-policy"
  path        = "/"
  description = "Allow retrieving of images and adding to logs"
  policy      = file("./templates/ecs/task-exec-role.json")
}

resource "aws_iam_role" "task_execution_role" {
  name               = "${local.prefix}-task-exec-role"
  assume_role_policy = file("./templates/ecs/assume-role-policy.json")

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "task_execution_role" {
  role       = aws_iam_role.task_execution_role.name
  policy_arn = aws_iam_policy.task_definition_role_policy.arn
}

resource "aws_iam_role" "telemetry_app_iam_role" {
  name               = "${local.prefix}-telemetry-app-task"
  assume_role_policy = file("./templates/ecs/assume-role-policy.json")

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "ecs_task_logs" {
  name = "${local.prefix}-telemetry-app"

  tags = local.common_tags
}

data "template_file" "telemetry_app_container_definitions" {
  template = file("./templates/ecs/container-definitions.json.tpl")

  vars = {
    telemetry_app_image = var.ecr_image_telemetry_app
    prefix              = "${var.prefix}-${terraform.workspace}"
    log_group_name      = aws_cloudwatch_log_group.ecs_task_logs.name
    log_group_region    = data.aws_region.current.name
    allowed_hosts       = "*"
  }
}

resource "aws_ecs_task_definition" "telemetry_app" {
  family                   = "${local.prefix}-telemetry-app"
  container_definitions    = data.template_file.telemetry_app_container_definitions.rendered
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.task_execution_role.arn
  task_role_arn            = aws_iam_role.telemetry_app_iam_role.arn

  tags = local.common_tags
}



