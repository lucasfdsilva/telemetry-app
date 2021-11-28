[
    {
        "name": "telemetry-app",
        "image": "${telemetry_app_image}",
        "essential": true,
        "memoryReservation": 512,
        "environment": [
            {
                "name": "prefix",
                "value": "${prefix}"
            }
        ],
        "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
                "awslogs-group": "${log_group_name}",
                "awslogs-region": "${log_group_region}",
                "awslogs-stream-prefix": "telemetry-app"
            }
        },
        "portMappings": [
            {
                "containerPort": 9000,
                "hostPort": 9000
            }
        ]
    }
]