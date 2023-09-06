DB_EXPORTING_CHART=../infrastructure/charts/db-exporting

## Define `sed` command depending on operating system.

ifeq ($(shell uname), Darwin)
	# macOS
	SED_INPLACE=sed -i '' -e
else
	# otherwise assume GNU sed
	SED_INPLACE=sed -i -e
endif

.PHONY: patch-package patch-chart patch-version check-docker-prerequisites build-docker push-docker docker-test docker-tag helm-delete helm-install helm deploy-test set-docker-tag patch-and-deploy

patch-version: patch-package patch-chart

patch-package:
	# update green-db dependencies
	git submodule update --remote

	$(eval OLD_VERSION=$(shell poetry version -s))
	poetry version patch

patch-chart:
	$(eval NEW_VERSION=$(shell poetry version -s))
	${SED_INPLACE} 's/${OLD_VERSION}/${NEW_VERSION}/' ${DB_EXPORTING_CHART}/Chart.yaml

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
	-helm delete db-exporting

helm-install:
	helm install db-exporting ${DB_EXPORTING_CHART}

helm: helm-delete helm-install

deploy-test: docker helm-delete
	# for private docker registry, we need 'private-registry-auth' imagePullSecrets
	helm install db-exporting --set image.pullPolicy=Always --set image.repository=${DOCKER_IMAGE_NAME} --set image.tag=test --set imagePullSecrets[0].name=private-registry-auth ${DB_EXPORTING_CHART}

test:
	poetry run pytest -W ignore::DeprecationWarning