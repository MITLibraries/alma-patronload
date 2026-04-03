### This is the Terraform-generated header for alma-patronload-dev. If  ###
###   this is a Lambda repo, uncomment the FUNCTION line below  ###
###   and review the other commented lines in the document.     ###
ECR_NAME_DEV:=alma-patronload-dev
ECR_URL_DEV:=222053980223.dkr.ecr.us-east-1.amazonaws.com/alma-patronload-dev
# FUNCTION_DEV:=
### End of Terraform-generated header                            ###
SHELL=/bin/bash
DATETIME:=$(shell date -u +%Y%m%dT%H%M%SZ)
S3_BUCKET:=shared-files-$(shell aws sts get-caller-identity --query "Account" --output text)
ORACLE_ZIP:=instantclient-basiclite-linux.x64-21.9.0.0.0dbru.zip
CPU_ARCH ?= $(shell cat .aws-architecture 2>/dev/null || echo "linux/amd64")

help: # Preview Makefile commands
	@awk 'BEGIN { FS = ":.*#"; print "Usage:  make <target>\n\nTargets:" } \
/^[-_[:alpha:]]+:.?*#/ { printf "  %-15s%s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: help install venv update test coveralls lint lint-fix security patronload dependencies dist-dev publish-dev dist-stage publish-stage database-connection-test-stage check-arch

##############################################
# Python Environment and Dependency commands
##############################################

install: .venv .git/hooks/pre-commit .git/hooks/pre-push # Install Python dependencies
	uv sync --dev

.venv:
	@echo "Creating virtual environment at .venv..."
	uv venv .venv

.git/hooks/pre-commit:
	@echo "Installing pre-commit commit hooks..."
	uv run pre-commit install --hook-type pre-commit

.git/hooks/pre-push:
	@echo "Installing pre-commit push hooks..."
	uv run pre-commit install --hook-type pre-push

venv: .venv

update: # Update Python dependencies
	uv lock --upgrade
	uv sync --dev

dependencies: # Download Oracle Instant Client
	aws s3 cp s3://$(S3_BUCKET)/files/$(ORACLE_ZIP) vendor/$(ORACLE_ZIP)

######################
# Unit test commands
######################

test: # Run tests and print a coverage report
	uv run coverage run --source=patronload -m pytest -vv
	uv run coverage report -m

coveralls: test # Write coverage data to an LCOV report
	uv run coverage lcov -o ./coverage/lcov.info

####################################
# Code linting and formatting
####################################

lint: # Run linting, alerts only, no code changes
	uv run ruff format --diff
	uv run mypy .
	uv run ruff check .

lint-fix: # Run linting, auto fix behaviors where supported
	uv run ruff format .
	uv run ruff check --fix .

security: # Run security / vulnerability checks
	uv run pip-audit

patronload: # CLI without any arguments, utilizing uv script entrypoint
	uv run patronload

####################################
# Terraform-generated Docker Build/Deploy Targets for Dev
####################################

check-arch: # Validate CPU_ARCH and set .arch_tag
	@if [ -z "$(CPU_ARCH)" ]; then \
		echo "ERROR: CPU_ARCH is not set"; \
		exit 1; \
	fi
	@echo "$(CPU_ARCH)" > .arch_tag

dist-dev: check-arch ## Build docker container (intended for developer-based manual build)
	docker buildx build --platform $(CPU_ARCH) \
	    -t $(ECR_URL_DEV):latest \
		-t $(ECR_URL_DEV):`git describe --always` \
		-t $(ECR_NAME_DEV):latest .

publish-dev: dist-dev ## Build, tag and push (intended for developer-based manual publish)
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(ECR_URL_DEV)
	docker push $(ECR_URL_DEV):latest
	docker push $(ECR_URL_DEV):`git describe --always`

### Terraform-generated manual shortcuts for deploying to Stage. This requires  ###
###   that ECR_NAME_STAGE, ECR_URL_STAGE, and FUNCTION_STAGE environment        ###
###   variables are set locally by the developer and that the developer has     ###
###   authenticated to the correct AWS Account. The values for the environment  ###
###   variables can be found in the stage_build.yml caller workflow.            ###
dist-stage: ## While stage should generally only be used in an emergency for most repos, it is necessary for any testing requiring access to the Data Warehouse because Cloud Connector is not enabled on dev1.
	docker buildx build --platform $(CPU_ARCH) \
	    -t $(ECR_URL_STAGE):latest \
		-t $(ECR_URL_STAGE):`git describe --always` \
		-t $(ECR_NAME_STAGE):latest .

publish-stage: ## While stage should generally only be used in an emergency for most repos, it is necessary for any testing requiring access to the Data Warehouse because Cloud Connector is not enabled on dev1.
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(ECR_URL_STAGE)
	docker push $(ECR_URL_STAGE):latest
	docker push $(ECR_URL_STAGE):`git describe --always`

database-connection-test-stage: ## Use after the Data Warehouse password is changed every year to confirm that the new password works.
	aws ecs run-task --cluster alma-integrations-patronload-ecs-stage --task-definition alma-integrations-patronload-ecs-stage --launch-type="FARGATE" --network-configuration '{"awsvpcConfiguration": {"subnets": ["subnet-05df31ac28dd1a4b0", "subnet-04cfa272d4f41dc8a"],"securityGroups": ["sg-08d197ec4530ff6b7"],"assignPublicIp": "DISABLED"}}' --overrides '{"containerOverrides": [ {"name": "alma-integrations-patronload-ecs-stage", "command": ["-t"]}]}'
