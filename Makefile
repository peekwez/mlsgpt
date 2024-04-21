start-services:
	$(info Starting app...)
	dotenv --file=.env run mlsgpt run-services