SCRAPYD_CHART=infrastructure/charts/scrapyd
WORKERS_CHART=infrastructure/charts/workers

.PHONY: patch-core-version patch-database-version patch-extract-version patch-message-queue-version patch-scraping-version patch-workers-version patch-all patch-version

patch-core-version:
	$(MAKE) -C core patch-version

patch-database-version:
	$(MAKE) -C database patch-version

patch-extract-version:
	$(MAKE) -C extract patch-version

patch-message-queue-version:
	$(MAKE) -C message-queue patch-version

patch-scraping-version:
	$(MAKE) -C scraping patch-version

patch-workers-version:
	$(MAKE) -C workers patch-version

patch-all: patch-core-version patch-database-version patch-extract-version patch-message-queue-version patch-scraping-version patch-workers-version

patch-version: patch-all
	# get version from core package.
	$(eval VERSION=$(shell cd core; poetry version -s))
	
	git add core/pyproject.toml database/pyproject.toml extract/pyproject.toml message-queue/pyproject.toml scraping/pyproject.toml workers/pyproject.toml ${SCRAPYD_CHART}/Chart.yaml ${WORKERS_CHART}/Chart.yaml
	git commit -m "bump version to '${VERSION}'"
	git tag ${VERSION}

	# push everything
	git push
	git push origin ${VERSION}

scrapyd-test-deploy:
	$(MAKE) -C scraping deploy-test

workers-test-deploy:
	$(MAKE) -C workers deploy-test