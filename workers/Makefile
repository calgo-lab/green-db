WORKER_CHART=../infrastructure/charts/workers

.PHONY: patch-version patch-package patch-chart patch-chart check-docker-prerequisites build-docker push-docker docker helm-delete helm-install helm deploy-test

patch-version: patch-package patch-chart

patch-package:
	$(eval OLD_VERSION=$(shell poetry version -s))
	poetry version patch

patch-chart:
	$(eval NEW_VERSION=$(shell poetry version -s))
	sed -i '' -e 's/${OLD_VERSION}/${NEW_VERSION}/' ${WORKER_CHART}/Chart.yaml

check-docker-prerequisites:
ifndef DOCKER_IMAGE_NAME
	$(error DOCKER_IMAGE_NAME is not set)
endif
ifndef DOCKER_IMAGE_TAG
	DOCKER_IMAGE_TAG=test
	$(info DOCKER_IMAGE_TAG is not set. Using ${DOCKER_IMAGE_TAG})
endif

build-docker: check-docker-prerequisites
	docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} -f Dockerfile ..

push-docker: check-docker-prerequisites
	docker push ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}

docker: build-docker push-docker

helm-delete:
	# ignoring error as long as it does not exist
	-helm delete workers

helm-install:
	helm install workers ${WORKER_CHART}

helm: helm-delete helm-install

deploy-test: docker helm-delete
	# for private docker registry, we need 'private-registry-auth' imagePullSecrets
	helm install workers --set image.repository=${DOCKER_IMAGE_NAME} --set image.tag=test --set imagePullSecrets[0].name=private-registry-auth ${WORKER_CHART}
	