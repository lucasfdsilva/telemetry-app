variable "prefix" {
  default = "telemetry"
}

variable "project" {
  default = "telemetry-app"
}

variable "owner" {
  default = "lucas@acceltra.ie"
}

variable "telemetry_app_image" {
  description = "used to store the ECR image generate in the build_push stage of the ci/cd workflow"
  default     = "128363080680.dkr.ecr.eu-west-1.amazonaws.com/telemetry-app:b1fb29ab12b7bbf95125509a8c885e79d71f5883"
}