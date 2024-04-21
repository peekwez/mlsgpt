BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

start-services:
	$(info Starting app...)
	dotenv --file=.env run mlsgpt run-services

push-code:
	$(info Pushing to Heroku...)
	git push origin $(BRANCH)