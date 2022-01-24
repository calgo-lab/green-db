# `scrapyd` Helm Chart


## Deploy to Kubernetes Cluster

1. Before you can deploy the helm chart, make sure the following secrets and keys exist.
   - `postgres-secret` with key `postgresql-password`
   - `redis-secret` with key `root-password`

2. Then run the following command.
   ```bash
   helm install workers --set image.tag=<version> .
   ```
