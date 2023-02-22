# patronload

Creates Alma-compliant XML patron profiles from information extracted from the Data Warehouse and transmits those files to an S3 bucket for ingest into Alma.

## Development

- To install with dev dependencies: `make install`
- To update dependencies: `make update`
- To run unit tests: `make test`
- To lint the repo: `make lint`
- To run the app: `pipenv run patronload --help`

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
- `SENTRY_DSN` = If set to a valid Sentry DSN, enables Sentry exception monitoring. This is not needed for local development.
