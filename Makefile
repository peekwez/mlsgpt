BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

start-services:
	$(info Starting app...)
	dotenv --file=.env run mlsgpt run-services

push-code:
	$(info Pushing to remote...)
	git push origin $(BRANCH)

build-amd64:
	$(info Building mlsgpt for amd64...)
	docker build -t mlsgpt-amd64/python3.12:latest --platform linux/amd64 -f Dockerfile . 

build-arm64:
	$(info Building mlsgpt for arm64...)
	docker build -t mlsgpt-arm64/python3.12:latest --platform linux/arm64 -f Dockerfile .