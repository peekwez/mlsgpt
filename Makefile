BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

start-services:
	$(info Starting app...)
	dotenv --file=.env-deploy run mlsgpt run-services --api-vesion=v2 --ngrok

push-code:
	$(info Pushing to remote...)
	git push origin $(BRANCH)

build-amd64:
	$(info Building mlsgpt for amd64...)
	docker build -t mlsgpt-amd64:latest --platform linux/amd64 -f Dockerfile .
	docker tag mlsgpt-amd64:latest kwesi/mlsgpt-amd64:latest
	docker push kwesi/mlsgpt-amd64:latest
	docker system prune -f

build-arm64:
	$(info Building mlsgpt for arm64...)
	docker build -t mlsgpt-arm64:latest --platform linux/arm64 -f Dockerfile .
	docker tag mlsgpt-arm64:latest kwesi/mlsgpt-arm64:latest
	docker push kwesi/mlsgpt-arm64:latest
	docker system prune -f