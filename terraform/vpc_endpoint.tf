resource "aws_vpc_endpoint" "dynamo_db" {
  vpc_id = aws_vpc.main.id
  route_table_ids = [
    aws_route_table.private_a.id,
    aws_route_table.private_b.id
  ]
  service_name = "com.amazonaws.eu-west-1.dynamodb"

  tags = merge(
    local.common_tags,
    tomap({
      "Name" = "${local.prefix}-dynamodb"
    })
  )
}