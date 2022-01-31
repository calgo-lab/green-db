# `workers` Helm Chart


## Deploy to Kubernetes Cluster

1. Before you can deploy the helm chart, make sure the following secrets and keys exist.
   - `green-db-secret` with key `postgres-password` and `postgres-user`
   - `scraping-secret` with key `postgres-password` and `postgres-user`
   - `redis-secret` with key `root-password`

2. Then run the following command.
   ```bash
   helm install workers .
   ```