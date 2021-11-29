variable "prefix" {
  default = "telemetry"
}

variable "project" {
  default = "telemetry-app"
}

variable "owner" {
  default = "lucas@acceltra.ie"
}

variable "TF_VAR_ecr_telemetry_app_image" {
  type        = string
  description = "used to store the ECR image generate in the build_push stage of the ci/cd workflow"
}

