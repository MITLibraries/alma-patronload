# patronload

Creates Alma-compliant XML patron profiles from information extracted from the Data Warehouse and transmits those files to an S3 bucket for ingest into Alma.

## Development

- To install with dev dependencies: `make install`
- To update dependencies: `make update`
- To run unit tests: `make test`
- To lint the repo: `make lint`
- To run the app: `pipenv run patronload --help`

The Data Warehouse runs on a older version of Oracle that necessitates the `thick` mode of `python-oracledb` which requires the Oracle Instant Client Library (this app was developed with version 21.9.0.0.0.)

# With Docker
Note: as of this writing, the Apple M1 Macs cannot run Oracle Instant Client, so Docker is the only option for development on those machines. 

From the project folder:

1. Run `make dependencies` with appropriate AWS credentials

2. Run `make dist-dev` to build the container

3. Run `docker run alma-patronload-dev:latest`

# Without Docker
1. Download [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client/downloads.html) (`basiclite` is sufficient) and set the `ORACLE_LIB_DIR` env variable.
   
2. Run `pipenv run patronload`

# Running AWS ECS Task
To properly test with a connection to the Data Warehouse, the app must be run as an ECS task in the `stage` environment.

1. Export stage credentials and set `ECR_NAME_STAGE` and `ECR_URL_STAGE` env variables for `alma-patronload-stage`.
2. To build and publish the container to stage, run `make dist-stage` and `make publish-stage`.
3. From Terraform Cloud, select the `workloads-patronload-stage` workspace and copy the `aws_cli_run_task` command.
4. Run the command in your terminal and observe the results in AWS.


## Required ENV

- `DATA_WAREHOUSE_USER` = The user for the Data Warehouse database.
- `DATA_WAREHOUSE_PASSWORD` = The password for the Data Warehouse database.
- `DATA_WAREHOUSE_HOST` = The host for the Data Warehouse database.
- `DATA_WAREHOUSE_PORT` = The port for the Data Warehouse database.
- `DATA_WAREHOUSE_SID` = The system identifier for the Data Warehouse database instance.
- `S3_BUCKET_NAME` = The S3 bucket in which files are deposited.
- `S3_PATH` = The file path prefix for files deposited to the S3 bucket.
- `WORKSPACE` = Set to `dev` for local development, this will be set to `stage` and `prod` in those environments by Terraform.

## Optional ENV
- `LOG_LEVEL` = The log level for the `alma-patronload` application. Defaults to `INFO` if not set.
- `ORACLE_LIB_DIR` = The directory containing the Oracle Instant Client library. 
- `SENTRY_DSN` = If set to a valid Sentry DSN, enables Sentry exception monitoring. This is not needed for local development.
