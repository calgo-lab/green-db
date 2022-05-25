START_JOB_CHART=../infrastructure/charts/start-job

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
	-helm delete start-job

helm-install: docker
	# for private docker registry, we need 'private-registry-auth' imagePullSecrets
	helm install start-job --set image.repository=${DOCKER_IMAGE_NAME} --set imagePullSecrets[0].name=private-registry-auth ${START_JOB_CHART}

helm: helm-delete helm-install

deploy-test: docker helm-delete
	# for private docker registry, we need 'private-registry-auth' imagePullSecrets
	helm install start-job --set image.repository=${DOCKER_IMAGE_NAME} --set image.tag=test --set imagePullSecrets[0].name=private-registry-auth ${START_JOB_CHART}
	