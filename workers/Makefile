DOCKER_IMAGE_NAME=ghcr.io/calgo-lab/green-db/workers
PACKAGE_VERSION=test

.PHONY: build-docker

build-docker:
	docker build -t $(DOCKER_IMAGE_NAME):${PACKAGE_VERSION} -f Dockerfile ..