resource "aws_elasticache_subnet_group" "redis" {
  name       = "shelflife-redis-${var.environment}"
  subnet_ids = var.private_subnet_ids
}

resource "aws_security_group" "redis" {
  name_prefix = "shelflife-redis-"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.services.id]
    description     = "Redis access from platform services"
  }

  tags = {
    Name = "shelflife-redis-sg"
  }
}

resource "aws_elasticache_replication_group" "inventory_cache" {
  replication_group_id = "shelflife-inventory-cache-${var.environment}"
  description          = "Inventory cache — write-through with TTL"

  engine               = "redis"
  engine_version       = "7.0"
  node_type            = var.redis_node_type
  num_cache_clusters   = 2
  port                 = 6379

  subnet_group_name  = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]

  automatic_failover_enabled = true
  multi_az_enabled           = true
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  parameter_group_name = aws_elasticache_parameter_group.redis.name

  tags = {
    Name    = "shelflife-inventory-cache"
    Service = "inventory-cache"
  }
}

resource "aws_elasticache_parameter_group" "redis" {
  name   = "shelflife-redis-params-${var.environment}"
  family = "redis7"

  parameter {
    name  = "maxmemory-policy"
    value = "noeviction"
  }

  parameter {
    name  = "notify-keyspace-events"
    value = "Ex"
  }
}
