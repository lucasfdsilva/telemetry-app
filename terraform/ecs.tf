resource "aws_ecs_cluster" "main" {
  name = "${local.prefix}-cluster"

  tags = local.common_tags
}

resource "aws_iam_policy" "task_definition_role_policy" {
  name        = "${local.prefix}-task-exec-role-policy"
  path        = "/"
  description = "Allow retrieving of images, adding to logs writing/reading from DynamoDB"
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

data "template_file" "telemetry_app_container_definitions" {
  template = file("./templates/ecs/container-definitions.json.tpl")

  vars = {
    telemetry_app_image = var.telemetry_app_image
    prefix              = "${var.prefix}-${terraform.workspace}"
    log_group_name      = aws_cloudwatch_log_group.ecs_task_logs.name
    log_group_region    = data.aws_region.current.name
    allowed_hosts       = aws_route53_record.telemetry_app.fqdn
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
  task_role_arn            = aws_iam_role.task_execution_role.arn

  tags = local.common_tags
}

resource "aws_security_group" "ecs_service" {
  description = "Access for the ECS Service"
  name        = "${local.prefix}-ecs-service"
  vpc_id      = aws_vpc.main.id

  egress = [
    {
      description      = ""
      from_port        = 443
      to_port          = 443
      protocol         = "tcp"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      self             = false
    }
  ]

  ingress = [
    {
      description      = "HTTP"
      from_port        = 9000
      to_port          = 9000
      protocol         = "tcp"
      cidr_blocks      = []
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = [aws_security_group.lb.id]
      self             = false
    }
  ]

  tags = local.common_tags
}

resource "aws_ecs_service" "telemetry_app" {
  name             = "${local.prefix}-telemetry-app"
  cluster          = aws_ecs_cluster.main.name
  task_definition  = aws_ecs_task_definition.telemetry_app.family
  desired_count    = 1
  launch_type      = "FARGATE"
  platform_version = "1.4.0"

  network_configuration {
    subnets = [
      aws_subnet.private_a.id,
      aws_subnet.private_b.id
    ]

    security_groups = [aws_security_group.ecs_service.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.telemetry_app.id
    container_name   = "telemetry-app"
    container_port   = 9000
  }

  #Ensures that the LB listener for HTTPS gets created before creating the ECS Service
  depends_on = [aws_lb_listener.telemetry_app]
}


