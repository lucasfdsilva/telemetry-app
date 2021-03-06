

# Telemetry App &middot; [![GitHub Super-Linter](https://github.com/lucasfdsilva/telemetry-app/workflows/Lint%20Code%20Base/badge.svg)](https://github.com/marketplace/actions/super-linter)

A Python API that takes in temperature readings from remote sensors and store these readings in AWS DynamoDB. The API also provides temperature statistics such as Max, Min and Average temperatures, based on the readings received.

## Contents
- [API Reference](https://github.com/lucasfdsilva/telemetry-app#api-reference)
  - [Public URL](https://github.com/lucasfdsilva/telemetry-app#public-url)   
  - [Endpoints](https://github.com/lucasfdsilva/telemetry-app#endpoints)
- [Built With](https://github.com/lucasfdsilva/telemetry-app#built-with)
- [Running the API locally](https://github.com/lucasfdsilva/telemetry-app#running-the-api-locally)
  - [Prerequisites](https://github.com/lucasfdsilva/telemetry-app#prerequisites)
  - [Terraform Prerequisites](https://github.com/lucasfdsilva/telemetry-app#terraform-prerequisites)
  - [Setting up Dev environment](https://github.com/lucasfdsilva/telemetry-app#setting-up-dev-environment)
  - [Creating Terraform Stack in your AWS Account](https://github.com/lucasfdsilva/telemetry-app#creating-terraform-stack-in-your-aws-account)
- [Deploying the API](https://github.com/lucasfdsilva/telemetry-app#deploying-the-api)
- [Tearing down the Terraform stack](https://github.com/lucasfdsilva/telemetry-app#tearing-down-the-terraform-stack)
- [CI/CD Pipeline](https://github.com/lucasfdsilva/telemetry-app#cicd-pipeline)
- [Architecture](https://github.com/lucasfdsilva/telemetry-app#architecture)
- [Database](https://github.com/lucasfdsilva/telemetry-app#database)

## API Reference
A Swagger documentation page is currently under development for the API but in the meantime the below should provide enough guidance on how to interact with the API.


### Public URL
The API is available at: https://prod.lucastelemetry3m.com

The API running on the staging environment is also available at: https://staging.lucastelemetry3m.com

The only reason why the staging environment is exposed is to demonstrate the multiple environments development strategy implemented. More about that in the [CI/CD Pipeline Section](https://github.com/lucasfdsilva/telemetry-app#cicd-pipeline)


### Endpoints
The API exposes two endpoints:

- **GET /api/stats** <br>
  Used to retrieve the current temperature statistics based on the readings received. No authentication required.
  
  **Response Sample:** <br>
  ```
  200 OK
  {
    "Maximum": 28,
    "Minimum": -6,
    "Average": 10
  }
  ```

- **PUT /api/temperature** <br>
  Used to store a new reading. No authentication required.
  
  **Expected payload sample:** <br>
  ```
  {
    "sensorId": "202",
    "temperature": 18,
    "timestamp": "YYYY-MM-DDTHH:MM:SS"
  }
  ```

  **Response Sample:** <br>
  ```
  200 OK
  {
    "message": "Temperature reading recorded successfully"
  }
  ```
  
## Built With
**Python Application**
- Python 3.8
- Docker v20.10.10
- Flask Web Framework v2.0.2
- Flask-RESTful 0.3.9
- Boto3 v1.20.14 (AWS SDK)
- uWSGI v2.0.18 (Web server)
- AutoPEP8 v1.6.0 (Python Linter)

**Infrastructure as Code (IaC)**
- Terraform v2.4


## Running the API locally
### Prerequisites
- [Python](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/cli/pip_download/)
- [Flask](https://pypi.org/project/Flask/)
- [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/Download.html)
- [Docker](https://docs.docker.com/get-docker/)
- [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)
- [AWS CLI](https://aws.amazon.com/cli/)
- [AWS-Vault](https://github.com/99designs/aws-vault) (Not mandatory but highly recommended to configure AWS Credentials locally safely) 

### Terraform Prerequisites
The following are required to create this stack in your AWS Account.

1. AWS IAM user with at least the permission listed in this [Sample IAM Policy](https://github.com/lucasfdsilva/telemetry-app/tree/main/documentation)
2. Custom Domain registered in AWS Route53 <br>
  After registering your domain, update the "dns_zone_name" variable in deploy/variables.tf with your domain name.

The Terraform state and lock are stored remotely following best practices when working as part of a team. Terraform requires the following AWS Resources to be set up for remote state/lock.
- S3 Bucket (Used to store the TF State)
- DynamoDB Table (Used to store the TF Lock)

To replicate this, create the resources above and replace the details in the terraform/main.tf file to match your S3 bucket name and DynamoDB Lock table. [More information about setting up Terraform](https://learn.hashicorp.com/collections/terraform/aws-get-started).
  


### Setting up Dev environment
 
1. Given that all the Prerequisites above have been correctly installed, execute the below

```shell
git clone https://github.com/lucasfdsilva/telemetry-app
cd telemetry-app/
pip install -r /requirements.txt
export FLASK_APP=wsgi.py
export FLASK_ENV=development
export PREFIX=telemetry-dev
```

### Creating Terraform Stack in your AWS Account

**IMPORTANT**<br>
Terraform will use your AWS account to build all resources required. This in turn will generate costs in you AWS account.

**Estimated costs for running the infrastructure required (per environment)** <br>
**Monthly:** $125.19 <br>
**Daily:** $4.04 <br>
**Hourly:** $0.17 <br>

Please refer to the [Architecture Diagram](https://github.com/lucasfdsilva/telemetry-app/tree/main/documentation) to understand which resources are part of this Terraform Stack. <br>


1. Once the AWS credentials have been configured locally, We will use Docker Compose to run Terraform. 
```
docker-compose -f terraform/docker-compose.yml run --rm terraform init
docker-compose -f terraform/docker-compose.yml run --rm terraform workspace select dev || terraform workspace create dev
docker-compose -f terraform/docker-compose.yml run --rm terraform plan
docker-compose -f terraform/docker-compose.yml run --rm terraform apply
```

2. Run the following command to "seed" the Aggregations DynamoDB Table. <br>
   Remember to replace "dev" with your workspace name if using a different name.
```
aws dynamodb put-item \
--table-name telemetry-dev-temperature-readings-aggregation \
--item file://terraform/templates/dynamodb/seed.json \
--condition-expression "attribute_not_exists(total_readings_count)" \
|| true
```

3. Now that Terraform has been initialized and the AWS Resources have been provisioned, run the application:
```
cd /app
flask run
```


## Deploying the API
We will use Docker to build a new docker image and then push this image to the ECR repository in AWS so that ECS can pull in and use this image.

1. Before we deploy, make sure your Terraform is valid.
```
docker-compose -f terraform/docker-compose.yml run --rm terraform init
docker-compose -f terraform/docker-compose.yml run --rm terraform fmt
docker-compose -f terraform/docker-compose.yml run --rm terraform validate
```

2. Now run the following at the project root. Make sure you replace the variables where applicable to match your ECR Repo.
```
docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:latest .
docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
```

3. We can now apply the Terraform stack so that ECS uses the newest version of the API.
```
docker-compose -f terraform/docker-compose.yml run --rm terraform plan
docker-compose -f terraform/docker-compose.yml run --rm terraform apply
```

4. After the apply job is complete, Terraform will output the URL you can use to access the application.


## Tearing down the Terraform stack
Since Terraform manages our entire stack, destroying and re-creating it can be done very quickly. The stack created for this application takes approx. 6 minutes to be created from scratch.

1. Ensure you're in the correct Terraform workspace. <br>
2. Destroy your Terraform stack
```
docker-compose -f terraform/docker-compose.yml run --rm terraform workspace select dev
docker-compose -f terraform/docker-compose.yml run --rm terraform destroy
```


## CI/CD Pipeline
In this repository you will find GitHub Actions workflows that automate the process of continuous integrations and continuous deployment of this application.

The workflows available make it possible to have the environments "staging" and "prod" being constantly and seamlessly tested, created and updated. 

The Staging environment is built following changes and updates to the "main" branch, while "prod" is updated when new commits and pull requests are made to the "prod" branch.

For more information on the configuration of these workflows, please refer to the following:
- [CI/CD Pipeline Diagram](https://github.com/lucasfdsilva/telemetry-app/tree/main/documentation)
- [Development Lifecycle Strategy Diagram](https://github.com/lucasfdsilva/telemetry-app/tree/main/documentation)
- [GitHub Workflows files](https://github.com/lucasfdsilva/telemetry-app/tree/main/.github/workflows)


## Architecture
The Terraform stack was developed following the [5 pillars of the AWS Well-Architected framework](https://aws.amazon.com/blogs/apn/the-5-pillars-of-the-aws-well-architected-framework/). 

Please refer to the [Architecture Diagram](https://github.com/lucasfdsilva/telemetry-app/tree/main/documentation) to understand the resources used and the relationship between these resources.

![Architecture Diagram](documentation/architecture-diagram.png)

## Database
This application only uses DynamoDB to persistent and access the data required. Due to the nature of NoSQL databases the schemas are very simple and basic. 

Please refer to the [Database Diagram](https://github.com/lucasfdsilva/telemetry-app/tree/main/documentation) to understand how the DynamoDB tables are set up.

