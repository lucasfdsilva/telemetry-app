resource "aws_dynamodb_table" "temperature_readings" {
  name         = "${local.prefix}-temperature-readings"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "sensor_id"
  range_key    = "timestamp"

  attribute {
    name = "sensor_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  tags = merge(
    local.common_tags,
    tomap({
      "Name" = "${local.prefix}-temperature-readings"
    })
  )
}


resource "aws_dynamodb_table" "temperature_readings_aggregation" {
  name         = "${local.prefix}_temperature-readings-aggregation"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "aggregation_period"

  attribute {
    name = "aggregation_period"
    type = "S"
  }

  tags = merge(
    local.common_tags,
    tomap({
      "Name" = "${local.prefix}-temperature-readings-aggregation"
    })
  )
}