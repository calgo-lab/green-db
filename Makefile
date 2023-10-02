SCRAPYD_CHART=infrastructure/charts/scrapyd
WORKERS_CHART=infrastructure/charts/workers
MONITORING_CHART=infrastructure/charts/monitoring
PRODUCT_CLASSIFICATION_CHART=infrastructure/charts/product-classification/helm
DB_EXPORTING_CHART=infrastructure/charts/db-exporting
START_JOB_CHART=infrastructure/charts/start-job


.PHONY: patch-core-version patch-database-version patch-extract-version patch-message-queue-version patch-scraping-version patch-workers-version patch-product-classification-version patch-start-job-version patch-db-exporting-version patch-all patch-version

patch-core-version:
	$(MAKE) -C core patch-version

patch-database-version:
	$(MAKE) -C database patch-version

patch-extract-version:
	$(MAKE) -C extract patch-version

patch-message-queue-version:
	$(MAKE) -C message-queue patch-version

patch-monitoring-version:
	$(MAKE) -C monitoring patch-version

patch-scraping-version:
	$(MAKE) -C scraping patch-version

patch-workers-version:
	$(MAKE) -C workers patch-version

patch-product-classification-version:
	$(MAKE) -C product-classification patch-version

patch-start-job-version:
	$(MAKE) -C start-job patch-version

patch-db-exporting-version:
	$(MAKE) -C db-exporting patch-version

patch-all: patch-core-version patch-database-version patch-extract-version patch-message-queue-version patch-monitoring-version patch-scraping-version patch-workers-version patch-product-classification-version patch-db-exporting-version patch-start-job-version

patch-version: patch-all
	# get version from core package.
	$(eval VERSION=$(shell cd core; poetry version -s))
	
	git add core/pyproject.toml database/pyproject.toml extract/pyproject.toml message-queue/pyproject.toml monitoring/pyproject.toml scraping/pyproject.toml workers/pyproject.toml db-exporting/pyproject.toml product-classification/pyproject.toml ${MONITORING_CHART}/Chart.yaml ${WORKERS_CHART}/Chart.yaml ${SCRAPYD_CHART}/Chart.yaml ${PRODUCT_CLASSIFICATION_CHART}/Chart.yaml ${DB_EXPORTING_CHART}/Chart.yaml ${START_JOB_CHART}/Chart.yaml
	git commit -m "bump version to '${VERSION}'"
	git tag ${VERSION}

patch-version-push: patch-version
	# push everything
	git push
	git push origin ${VERSION}

scrapyd-test-deploy:
	$(MAKE) -C scraping deploy-test

workers-test-deploy:
	$(MAKE) -C workers deploy-test

start-job-test-deploy:
	$(MAKE) -C start-job deploy-test

product-classification-test-deploy:
	$(MAKE) -C product-classification deploy-test

test:
	$(MAKE) -C extract test
	$(MAKE) -C scraping test
	$(MAKE) -C product-classification test
