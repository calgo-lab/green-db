DOCKER_IMAGE_NAME=calgo-lab/workers
PACKAGE_VERSION=$(shell poetry version -s)

.PHONY: build-docker

build-docker:
	docker build -t $(DOCKER_IMAGE_NAME):${PACKAGE_VERSION} -f Dockerfile ..