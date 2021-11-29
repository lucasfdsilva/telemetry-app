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

  tags = local.common_tags
}

resource "aws_dynamodb_table" "temperature_readings_aggregation" {
  name         = "${local.prefix}-temperature-readings-aggregation"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "aggregation_period"

  attribute {
    name = "aggregation_period"
    type = "S"
  }

  tags = local.common_tags
}

resource "aws_dynamodb_table_item" "stats_aggregation" {
  table_name = aws_dynamodb_table.temperature_readings_aggregation.name
  hash_key   = aws_dynamodb_table.temperature_readings_aggregation.aggregation_period

  item = <<ITEM
{
  "aggregation_period": {"S": "total"},
  "maximum": {"N": "0"},
  "minimum": {"N": "0"},
  "total_readings_count": {"N": "0"},
  "total_temperature_sum": {"N": "0"}
}
ITEM
}