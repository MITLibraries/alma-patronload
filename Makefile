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

help: ## Print this message
	@awk 'BEGIN { FS = ":.*##"; print "Usage:  make <target>\n\nTargets:" } \
/^[-_[:alpha:]]+:.?*##/ { printf "  %-15s%s\n", $$1, $$2 }' $(MAKEFILE_LIST)

### Dependency commands ###

install: ## Install dependencies and CLI app
	pipenv install --dev
	pipenv run pre-commit install

update: install ## Update all Python dependencies
	pipenv clean
	pipenv update --dev

dependencies: 
	aws s3 cp s3://$(S3_BUCKET)/files/$(ORACLE_ZIP) vendor/$(ORACLE_ZIP)

### Test commands ###

test: ## Run tests and print a coverage report
	pipenv run coverage run --source=patronload -m pytest -vv
	pipenv run coverage report -m

coveralls: test
	pipenv run coverage lcov -o ./coverage/lcov.info

# linting commands
lint: black mypy ruff safety 

black:
	pipenv run black --check --diff .

mypy:
	pipenv run mypy .

ruff:
	pipenv run ruff check .

safety:
	pipenv check
	pipenv verify

# apply changes to resolve any linting errors
lint-apply: black-apply ruff-apply

black-apply: 
	pipenv run black .

ruff-apply: 
	pipenv run ruff check --fix .


### Terraform-generated Developer Deploy Commands for Dev environment           ###
dist-dev: ## Build docker container (intended for developer-based manual build)
	docker build --platform linux/amd64 \
	    -t $(ECR_URL_DEV):latest \
		-t $(ECR_URL_DEV):`git describe --always` \
		-t $(ECR_NAME_DEV):latest .

publish-dev: dist-dev ## Build, tag and push (intended for developer-based manual publish)
	docker login -u AWS -p $$(aws ecr get-login-password --region us-east-1) $(ECR_URL_DEV)
	docker push $(ECR_URL_DEV):latest
	docker push $(ECR_URL_DEV):`git describe --always`

### Terraform-generated manual shortcuts for deploying to Stage. This requires  ###
###   that ECR_NAME_STAGE, ECR_URL_STAGE, and FUNCTION_STAGE environment        ###
###   variables are set locally by the developer and that the developer has     ###
###   authenticated to the correct AWS Account. The values for the environment  ###
###   variables can be found in the stage_build.yml caller workflow.            ###
dist-stage: ## While stage should generally only be used in an emergency for most repos, it is necessary for any testing requiring access to the Data Warehouse because Cloud Connector is not enabled on dev1.
	docker build --platform linux/amd64 \
	    -t $(ECR_URL_STAGE):latest \
		-t $(ECR_URL_STAGE):`git describe --always` \
		-t $(ECR_NAME_STAGE):latest .

publish-stage: ## While stage should generally only be used in an emergency for most repos, it is necessary for any testing requiring access to the Data Warehouse because Cloud Connector is not enabled on dev1.
	docker login -u AWS -p $$(aws ecr get-login-password --region us-east-1) $(ECR_URL_STAGE)
	docker push $(ECR_URL_STAGE):latest
	docker push $(ECR_URL_STAGE):`git describe --always`

database-connection-test-stage: ## Use after the Data Warehouse password is changed every year to confirm that the new password works.
	aws ecs run-task --cluster alma-integrations-patronload-ecs-stage --task-definition alma-integrations-patronload-ecs-stage --launch-type="FARGATE" --network-configuration '{"awsvpcConfiguration": {"subnets": ["subnet-05df31ac28dd1a4b0", "subnet-04cfa272d4f41dc8a"],"securityGroups": ["sg-08d197ec4530ff6b7"],"assignPublicIp": "DISABLED"}}' --overrides '{"containerOverrides": [ {"name": "alma-integrations-patronload-ecs-stage", "command": ["-t"]}]}'
