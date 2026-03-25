terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "shelflife-terraform-state"
    key            = "platform/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "shelflife-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = var.tags
  }
}

data "aws_vpc" "main" {
  id = var.vpc_id
}

resource "aws_security_group" "services" {
  name_prefix = "shelflife-services-"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
    description = "Allow inter-service communication"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name = "shelflife-services-sg"
  }
}

resource "aws_cloudwatch_log_group" "platform" {
  name              = "/shelflife/platform"
  retention_in_days = 30
}
