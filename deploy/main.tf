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


variable "telemetry_app_image" {
  description = "used to store the ECR image generate in the build_push stage of the ci/cd workflow"
  default     = "128363080680.dkr.ecr.eu-west-1.amazonaws.com/telemetry-app:b1fb29ab12b7bbf95125509a8c885e79d71f5883"
}