SCRAPYD_CHART=../infrastructure/charts/scrapyd

.PHONY: patch-version patch-package patch-chart patch-chart check-docker-prerequisites build-docker push-docker docker helm-delete helm-install helm deploy-test

patch-version: patch-package patch-chart

patch-package:
	$(eval OLD_VERSION=$(shell poetry version -s))
	poetry version patch

patch-chart:
	$(eval NEW_VERSION=$(shell poetry version -s))
	sed -i '' -e 's/${OLD_VERSION}/${NEW_VERSION}/' ../infrastructure/charts/scrapyd/Chart.yaml

check-docker-prerequisites:
ifndef DOCKER_IMAGE_NAME
	$(error DOCKER_IMAGE_NAME is not set)
endif

build-docker: check-docker-prerequisites
	docker build -t ${DOCKER_IMAGE_NAME}:test -f Dockerfile ..

push-docker: check-docker-prerequisites
	docker push ${DOCKER_IMAGE_NAME}:test

docker: build-docker push-docker

helm-delete:
	# ignoring error as long as it does not exist
	-helm delete scrapyd

helm-install:
	helm install scrapyd ${SCRAPYD_CHART}

helm: helm-delete helm-install

deploy-test: docker helm-delete
	# for private docker registry, we need 'private-registry-auth' imagePullSecrets
	helm install scrapyd --set image.pullPolicy=Always --set image.repository=${DOCKER_IMAGE_NAME} --set image.tag=test --set imagePullSecrets[0].name=private-registry-auth ${SCRAPYD_CHART}
	