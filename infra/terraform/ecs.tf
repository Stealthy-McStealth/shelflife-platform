resource "aws_ecs_cluster" "main" {
  name = "shelflife-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "shelflife-ecs-cluster"
  }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 1
    capacity_provider = "FARGATE"
  }
}

locals {
  services = {
    web-gateway = {
      port     = 8080
      cpu      = 512
      memory   = 1024
      replicas = 3
    }
    order-service = {
      port     = 8081
      cpu      = 256
      memory   = 512
      replicas = 2
    }
    fulfillment-engine = {
      port     = 8082
      cpu      = 512
      memory   = 1024
      replicas = 2
    }
    warehouse-api = {
      port     = 8083
      cpu      = 256
      memory   = 512
      replicas = 2
    }
    notification-service = {
      port     = 8084
      cpu      = 256
      memory   = 512
      replicas = 1
    }
    analytics-service = {
      port     = 8085
      cpu      = 256
      memory   = 512
      replicas = 1
    }
    auth-service = {
      port     = 8086
      cpu      = 256
      memory   = 512
      replicas = 2
    }
    scheduler-service = {
      port     = 8087
      cpu      = 256
      memory   = 512
      replicas = 1
    }
  }
}

resource "aws_ecs_task_definition" "services" {
  for_each = local.services

  family                   = "shelflife-${each.key}-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = each.value.cpu
  memory                   = each.value.memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = each.key
      image     = "${aws_ecr_repository.services[each.key].repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = each.value.port
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.platform.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = each.key
        }
      }
    }
  ])

  tags = {
    Service = each.key
  }
}

resource "aws_ecs_service" "services" {
  for_each = local.services

  name            = each.key
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.services[each.key].arn
  desired_count   = each.value.replicas
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [aws_security_group.services.id]
  }

  tags = {
    Service = each.key
  }
}

resource "aws_ecr_repository" "services" {
  for_each = local.services

  name                 = "shelflife/${each.key}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_iam_role" "ecs_execution" {
  name = "shelflife-ecs-execution-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role" "ecs_task" {
  name = "shelflife-ecs-task-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
