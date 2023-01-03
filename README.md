# python-cli-template

A template repository for creating Python CLI applications.

## App setup (delete this section and above after initial application setup)

1. Rename "my_app" to the desired app name across the repo. (May be helpful to do a project-wide find-and-replace).
2. Update Python version if needed.
3. Install all dependencies with `make install`  to create initial Pipfile.lock with latest dependency versions.
4. Add initial app description to README and update initial required ENV variable documentation as needed.
5. Update license if needed (check app-specific dependencies for licensing terms).
6. Check Github repository settings:
   - Confirm repo branch protection settings are correct (see [dev docs](https://mitlibraries.github.io/guides/basics/github.html) for details)
   - Confirm that all of the following are enabled in the repo's code security and analysis settings:
      - Dependabot alerts
      - Dependabot security updates
      - Secret scanning
7. Create a Sentry project for the app if needed (we want this for most apps):
   - Send initial exceptions to Sentry project for dev, stage, and prod environments to create them.
   - Create an alert for the prod environment only, with notifications sent to the appropriate team(s).
   - If *not* using Sentry, delete Sentry configuration from config.py and test_config.py, and remove sentry_sdk from project dependencies.

# my_app

Description of the app

## Development

- To install with dev dependencies: `make install`
- To update dependencies: `make update`
- To run unit tests: `make test`
- To lint the repo: `make lint`
- To run the app: `pipenv run my_app --help`

## Required ENV

- `SENTRY_DSN` = If set to a valid Sentry DSN, enables Sentry exception monitoring. This is not needed for local development.
- `WORKSPACE` = Set to `dev` for local development, this will be set to `stage` and `prod` in those environments by Terraform.
