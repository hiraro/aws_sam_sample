AWS_PROFILE = develop
CFN_STACK_NAME_STAGE = slack-polly-stage
S3_BUCKET_NAME_STAGE = slack-polly-stage
CFN_STACK_NAME_PROD = slack-polly-prod
S3_BUCKET_NAME_PROD = slack-polly-prod

.PHONY: all slack_app polly_task deploy build dep slack_app_deps polly_task_deps

all: deploy

define build_lambda_func
	cp -v $1/*.py $1/build/
endef

define resolve_deps
	pip install -r $1/requirements.txt -t $1/build/
endef

slack_app:
	$(call build_lambda_func, slack_app)
polly_task:
	$(call build_lambda_func, polly_task)

slack_app_deps:
	$(call resolve_deps, slack_app)
polly_task_deps:
	$(call resolve_deps, polly_task)

clean:
	rm -rfv slack_app/build/*
	rm -rfv polly_task/build/*

dep: slack_app_deps polly_task_deps

build: slack_app polly_task


deploy: dep build
	sam package --profile $(AWS_PROFILE) \
		--template-file template.yaml \
		--s3-bucket $(S3_BUCKET_NAME_STAGE) \
		--output-template-file packaged.yaml
	sam deploy --profile $(AWS_PROFILE) \
		--template-file packaged.yaml \
		--stack-name $(CFN_STACK_NAME_STAGE) \
		--capabilities CAPABILITY_IAM

deploy_prod: dep build
	sam package --profile $(AWS_PROFILE) \
		--template-file template.yaml \
		--s3-bucket $(S3_BUCKET_NAME_PROD) \
		--output-template-file packaged.yaml
	sam deploy --profile $(AWS_PROFILE) \
		--template-file packaged.yaml \
		--stack-name $(CFN_STACK_NAME_PROD) \
		--parameter-overrides "Env=Prod" \
		--capabilities CAPABILITY_IAM
