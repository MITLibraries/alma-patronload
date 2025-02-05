# patronload

Creates Alma-compliant XML patron profiles from information extracted from the Data Warehouse and transmits those files to an S3 bucket for ingest into Alma.

## Description

This application runs daily to create and deliver XML files for Alma to retrieve and load. It establishes a connection to the [Data Warehouse](https://ist.mit.edu/warehouse) and retrieves data for student and staff patrons via SQL queries. Different data are required for students and staff so separate queries are run againt the student and staff tables to retrieve the necessary data for each.

Though the zip files receive a suffix from Alma after processing to prevent them being re-processed, the application removes any existing zip files from the S3 bucket at the start of a run. This prevents any potential errors if Alma were to process more than 1 zip file of either staff or student data. 

Given that student employees may appear as both staff and students, the application processing the staff names first and checks student names against the staff names to ensure that student employees only loaded into Alma once. 

A zip file is created for each patron type containing an XML file with the Data Warehouse output formatted according to a template.

The staff and student zip files are then posted to the specified S3 bucket.

Finally, the application sends an email with the logs from the run to the `lib-alma-notifications` list.

## Alma Processing Requirements

Maximum size for a zip file is 4 GB
Maximum limit of 50 XML files in one zip file
Maximum of 20 zip files for each import/synchronization

This app uploads 2 under 50MB zip files, each containing 1 XML file, so it is unlikely that the files produced will conflict with these requirements.


## Development

- To install with dev dependencies: `make install`
- To update dependencies: `make update`
- To run unit tests: `make test`
- To lint the repo: `make lint`
- To run the app: `pipenv run patronload --help`

The Data Warehouse runs on a older version of Oracle that necessitates the `thick` mode of `python-oracledb` which requires the Oracle Instant Client Library (this app was developed with version 21.9.0.0.0.).

### With Docker

Note: as of this writing, the Apple M1 Macs cannot run Oracle Instant Client, so Docker is the only option for development on those machines. 

From the project folder:

1. Run `make dependencies` with appropriate AWS credentials.

2. Run `make dist-dev` to build the container.

3. Run `docker run alma-patronload-dev:latest`.

### Without Docker

1. Download [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client/downloads.html) (`basiclite` is sufficient) and set the `ORACLE_LIB_DIR` env variable.
   
2. Run `pipenv run patronload`.

## Connecting to the Data Warehouse

The password for the Data Warehouse is updated each year. To verify that the updated password works, the app must be run as an ECS task in the `stage` environment because Cloudconnector is not enabled in `dev1`. The app can run a database connection test when called with the flag, `--database_connection_test` or `-t`.

1. Set AWS credentials for `PatronloadManagers` role in stage
2. Run `make database-connection-test-stage`.
3. View the logs from the ECS task run on CloudWatch. 
   * On CloudWatch, select the `alma-integrations-patronload-ecs-stage` log group.
   * Select the most recent log stream. 
   * Verify that the following log is included: 

     > Successfully connected to Oracle Database version: \<VERSION NUMBER\>


## Running AWS ECS Tasks

To properly test with a connection to the Data Warehouse, the app must be run as an ECS task in the `stage` environment.

1. Set AWS credentials for `PatronloadManagers` role in stage
2. Set `ECR_NAME_STAGE` and `ECR_URL_STAGE` in `.env` file (see `ECR_NAME_DEV` and `ECR_URL_DEV` from `Makefile` for guidance).
3. Run `make dependencies`.
4. Build the image locally: `make dist-stage`.
5. Publish the image to AWS ECR for stage: `make publish-stage`.
6. From Terraform Cloud, select the `workloads-patronload-stage` workspace and copy the `aws_cli_run_task` command.
7. Run the command in your terminal and observe the results in AWS.


## Environment Variables

### Required
```shell
DATA_WAREHOUSE_USER=# The user for the Data Warehouse database.
DATA_WAREHOUSE_PASSWORD=# The password for the Data Warehouse database.
DATA_WAREHOUSE_HOST=# The host for the Data Warehouse database.
DATA_WAREHOUSE_PORT=# The port for the Data Warehouse database.
DATA_WAREHOUSE_SID=# The system identifier for the Data Warehouse database instance.
SES_RECIPIENT_EMAIL=# The email address to send to, typically a Moira list.
SES_SEND_FROM_EMAIL=# The email address to send from.
S3_BUCKET_NAME=# The S3 bucket in which files are deposited.
S3_PREFIX=# The file path prefix for files deposited to the S3 bucket.
WORKSPACE=# Set to `dev` for local development, this will be set to `stage` and `prod` in those environments by Terraform.
```


### Optional

```shell
LOG_LEVEL=# The log level for the `alma-patronload` application. Defaults to `INFO` if not set.
ORACLE_LIB_DIR=# The directory containing the Oracle Instant Client library. 
SENTRY_DSN=# If set to a valid Sentry DSN, enables Sentry exception monitoring. This is not needed for local development.
```

## Related Assets

* Infrastructure: [mitlib-tf-workloads-patronload](https://github.com/MITLibraries/mitlib-tf-workloads-patronload)
* Depends-on Application: [CloudConnector](https://github.com/MITLibraries/cloudconnector)

```mermaid
mindmap
    root((alma-patronload))
        (infrastructure)
            ["`mitlib-tf-
            workloads-patronload`"]
        (depends-on)
            [CloudConnector]
        (output)
            ["`Writes data as 
            zip file(s) to S3`"]
        (reporting)
            [Emails stakeholders]
```

## Maintainers

* Team: [DataEng](https://github.com/orgs/MITLibraries/teams/dataeng)
* Last Maintenance: 2025-01
* External Documentation: _TODO..._