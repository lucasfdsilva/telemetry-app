terraform {
  backend "s3" {
    bucket         = "telemetry-app-devops-tfstate"
    key            = "telemetry-app.tfstate"
    region         = "eu-west-1"
    encrypt        = true
    dynamodb_table = "telemetry-app-devops-tfstate-lock"
  }
}

provider "aws" {
  region  = "eu-west-1"
  version = "~> 2.54"
}

locals {
  prefix = "${var.prefix}-${terraform.workspace}"
  common_tags = {
    Environment = terraform.workspace
    Project     = var.project
    Owner       = var.owner
    ManagedBy   = "Terraform"
  }
}

data "aws_region" "current" {}