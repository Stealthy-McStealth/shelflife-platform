variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "vpc_id" {
  description = "VPC ID for the platform"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for ECS tasks and databases"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "Public subnet IDs for load balancers"
  type        = list(string)
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.medium"
}

variable "ecs_task_cpu" {
  description = "Default CPU units for ECS tasks"
  type        = number
  default     = 256
}

variable "ecs_task_memory" {
  description = "Default memory (MiB) for ECS tasks"
  type        = number
  default     = 512
}

variable "domain_name" {
  description = "Primary domain name for the platform"
  type        = string
  default     = "api.shelflife.io"
}

variable "tags" {
  description = "Common tags applied to all resources"
  type        = map(string)
  default = {
    Project   = "shelflife"
    ManagedBy = "terraform"
  }
}
