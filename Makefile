### This is the Terraform-generated header for alma-patronload-dev. If  ###
###   this is a Lambda repo, uncomment the FUNCTION line below  ###
###   and review the other commented lines in the document.     ###
ECR_NAME_DEV:=alma-patronload-dev
ECR_URL_DEV:=222053980223.dkr.ecr.us-east-1.amazonaws.com/alma-patronload-dev
# FUNCTION_DEV:=
### End of Terraform-generated header                            ###
SHELL=/bin/bash
DATETIME:=$(shell date -u +%Y%m%dT%H%M%SZ)
S3_BUCKET=shared-files-$(shell aws sts get-caller-identity --query "Account" --output text)
ORACLE_ZIP:=instantclient-basiclite-linux.x64-21.9.0.0.0dbru.zip

CPU_ARCH ?= $(shell cat .aws-architecture 2>/dev/null || echo "linux/amd64")

help: # Preview Makefile commands
	@awk 'BEGIN { FS = ":.*#"; print "Usage:  make <target>\n\nTargets:" } \
/^[-_[:alpha:]]+:.?*#/ { printf "  %-15s%s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ensure OS binaries aren't called if naming conflict with Make recipes
.PHONY: help install venv update test coveralls lint lint-fix security check-arch dist-dev publish-dev docker-clean dependencies patronload dist-stage publish-stage database-connection-test-stage

##############################################
# Python Environment and Dependency commands
##############################################

install: .venv .git/hooks/pre-commit .git/hooks/pre-push # Install Python dependencies and create virtual environment if not exists
	uv sync --dev

.venv: # Creates virtual environment if not found
	@echo "Creating virtual environment at .venv..."
	uv venv .venv

.git/hooks/pre-commit: # Sets up pre-commit commit hooks if not setup
	@echo "Installing pre-commit commit hooks..."
	uv run pre-commit install --hook-type pre-commit

.git/hooks/pre-push: # Sets up pre-commit push hooks if not setup
	@echo "Installing pre-commit push hooks..."
	uv run pre-commit install --hook-type pre-push

venv: .venv # Create the Python virtual environment

update: # Update Python dependencies
	uv lock --upgrade
	uv sync --dev

dependencies: # Download Oracle Instant Client from S3
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

###############################################
# Docker image, ECR, and Lambda Management
###############################################
check-arch:
	@ARCH_FILE=".aws-architecture"; \
	if [[ "$(CPU_ARCH)" != "linux/amd64" && "$(CPU_ARCH)" != "linux/arm64" ]]; then \
        echo "Invalid CPU_ARCH: $(CPU_ARCH)"; exit 1; \
    fi; \
	if [[ -f $$ARCH_FILE ]]; then \
		echo "latest-$(shell echo $(CPU_ARCH) | cut -d'/' -f2)" > .arch_tag; \
	else \
		echo "latest" > .arch_tag; \
	fi

dist-dev: check-arch # Build docker container (intended for developer-based manual build)
	@ARCH_TAG=$$(cat .arch_tag); \
	docker buildx inspect $(ECR_NAME_DEV) >/dev/null 2>&1 || docker buildx create --name $(ECR_NAME_DEV) --use; \
	docker buildx use $(ECR_NAME_DEV); \
	docker buildx build --platform $(CPU_ARCH) \
		--load \
		--tag $(ECR_URL_DEV):$$ARCH_TAG \
		--tag $(ECR_URL_DEV):make-$$ARCH_TAG \
		--tag $(ECR_URL_DEV):make-$(shell git describe --always) \
		--tag $(ECR_NAME_DEV):$$ARCH_TAG \
		.

publish-dev: dist-dev # Build, tag and push (intended for developer-based manual publish)
	@ARCH_TAG=$$(cat .arch_tag); \
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(ECR_URL_DEV); \
	docker push $(ECR_URL_DEV):$$ARCH_TAG; \
	docker push $(ECR_URL_DEV):make-$$ARCH_TAG; \
	docker push $(ECR_URL_DEV):make-$(shell git describe --always); \
	echo "Cleaning up dangling Docker images..."; \
	docker image prune -f --filter "dangling=true"

docker-clean: # Clean up Docker detritus
	@ARCH_TAG=$$(cat .arch_tag); \
	echo "Cleaning up Docker leftovers (containers, images, builders)"; \
	docker rmi -f $(ECR_URL_DEV):$$ARCH_TAG; \
	docker rmi -f $(ECR_URL_DEV):make-$$ARCH_TAG; \
	docker rmi -f $(ECR_URL_DEV):make-$(shell git describe --always) || true; \
	docker rmi -f $(ECR_NAME_DEV):$$ARCH_TAG || true; \
	docker buildx rm $(ECR_NAME_DEV) || true
	@rm -rf .arch_tag

### Manual shortcuts for deploying to Stage. Requires ECR_NAME_STAGE and        ###
### ECR_URL_STAGE environment variables to be set locally. Stage is necessary   ###
### for Data Warehouse testing since Cloud Connector is not enabled on dev1.    ###
dist-stage: # Build docker container for stage (developer manual use only — requires Data Warehouse access)
	docker buildx build --platform $(CPU_ARCH) \
		--load \
		-t $(ECR_URL_STAGE):latest \
		-t $(ECR_URL_STAGE):`git describe --always` \
		-t $(ECR_NAME_STAGE):latest .

publish-stage: # Build, tag and push to stage (developer manual use only — requires Data Warehouse access)
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(ECR_URL_STAGE)
	docker push $(ECR_URL_STAGE):latest
	docker push $(ECR_URL_STAGE):`git describe --always`

database-connection-test-stage: # Use after the Data Warehouse password is changed every year to confirm that the new password works.
	aws ecs run-task --cluster alma-integrations-patronload-stage --task-definition alma-integrations-patronload-stage --propagate-tags="TASK_DEFINITION" --launch-type="FARGATE" --network-configuration '{ "awsvpcConfiguration": {"subnets": ["subnet-05df31ac28dd1a4b0", "subnet-04cfa272d4f41dc8a"],"securityGroups": ["sg-0bb8b96173511b379"],"assignPublicIp": "DISABLED"}}' --overrides '{"containerOverrides": [ {"name": "alma-integrations-patronload-stage", "command": ["-t"]}]}'
####################################
# CLI convenience commands
####################################

patronload: # Run patronload CLI without any arguments
	uv run patronload
