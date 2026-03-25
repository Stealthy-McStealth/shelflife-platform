resource "aws_db_subnet_group" "main" {
  name       = "shelflife-db-${var.environment}"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "shelflife-db-subnet-group"
  }
}

resource "aws_security_group" "rds" {
  name_prefix = "shelflife-rds-"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.services.id]
    description     = "PostgreSQL access from platform services"
  }

  tags = {
    Name = "shelflife-rds-sg"
  }
}

resource "aws_rds_cluster" "main" {
  cluster_identifier = "shelflife-${var.environment}"
  engine             = "aurora-postgresql"
  engine_version     = "15.4"

  database_name   = "shelflife"
  master_username = "shelflife_admin"
  master_password = data.aws_secretsmanager_secret_version.db_password.secret_string

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  storage_encrypted       = true
  deletion_protection     = true

  tags = {
    Name = "shelflife-aurora-cluster"
  }
}

resource "aws_rds_cluster_instance" "main" {
  count              = 2
  identifier         = "shelflife-${var.environment}-${count.index}"
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = var.db_instance_class
  engine             = aws_rds_cluster.main.engine
  engine_version     = aws_rds_cluster.main.engine_version

  tags = {
    Name = "shelflife-aurora-instance-${count.index}"
  }
}

data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "shelflife/${var.environment}/db-password"
}
