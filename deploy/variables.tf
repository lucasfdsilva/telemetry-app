variable "prefix" {
  default = "telemetry"
}

variable "project" {
  default = "telemetry-app"
}

variable "owner" {
  default = "lucas@acceltra.ie"
}

variable "ecr_image_telemetry_app" {
  description = "ECR image for the telemetry app"
  default     = "128363080680.dkr.ecr.eu-west-1.amazonaws.com/telemetry-app:latest"
}
