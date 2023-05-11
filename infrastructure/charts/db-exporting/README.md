# `start-job` Helm Chart


## Deploy to Kubernetes Cluster

1. Run the following command.
   ```bash
   helm -n greendb install db-exporting-test --set image.tag=${DOCKER_IMAGE_TAG} --set image.pullPolicy=Always ${DB_EXPORTING_CHART}
   ```
#### More info and commands in green-db/db-exporting/Makefile