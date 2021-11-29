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
  default     = "128363080680.dkr.ecr.eu-west-1.amazonaws.com/telemetry-app:c684ae5c9e9879879049db5c5288d4cd7d226c9e"
}
