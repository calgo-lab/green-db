ifndef DOCKER_IMAGE_NAME
DOCKER_IMAGE_NAME=registry.datexis.com/trajanovska/db-exporting
$(info DOCKER_IMAGE_NAME is not set. Using ${DOCKER_IMAGE_NAME})
endif


DB_EXPORTING_CHART=../infrastructure/charts/db-exporting

.PHONY: patch-package patch-chart patch-version check-docker-prerequisites build-docker push-docker docker-test docker-tag helm-delete helm-install helm deploy-test set-docker-tag patch-and-deploy

patch-package:
	# update green-db dependencies
	git submodule update --remote

	$(eval OLD_VERSION=$(shell poetry version -s))
	poetry version patch

patch-chart:
	$(eval NEW_VERSION=$(shell poetry version -s))
	sed -i '' -e 's/${OLD_VERSION}/${NEW_VERSION}/' ${DB_EXPORTING_CHART}/Chart.yaml

patch-version: patch-package patch-chart
	# commit and push new version
	git add pyproject.toml ${DB_EXPORTING_CHART}/Chart.yaml
	git commit -m "bump version to '${NEW_VERSION}'"
	git tag ${NEW_VERSION}

	# push everything
	git push
	git push origin ${NEW_VERSION}

set-docker-tag:
	$(eval DOCKER_IMAGE_TAG=$(shell poetry version -s))

set-docker-test:
	$(eval DOCKER_IMAGE_TAG=test)

build-docker:
	docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} .

push-docker:
	docker push ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}

docker-test: set-docker-test build-docker push-docker
docker-tag: set-docker-tag build-docker push-docker

helm-delete:
	# ignoring error as long as it does not exist
	helm -n greendb delete db-exporting

helm-install:
	helm -n greendb install db-exporting --set image.tag=${DOCKER_IMAGE_TAG} --set image.pullPolicy=Always ${DB_EXPORTING_CHART}

helm: helm-delete helm-install

deploy-test: docker-test helm
deploy-tag: docker-tag helm