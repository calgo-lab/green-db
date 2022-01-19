# green-db-worker

## Deploy to Kubernetes Cluster

1. Before you can deploy the helm chart, make sure the following secrets and keys exist.
   - `postgres-secret` with key `postgresql-password`
   - `root-password` with key `root-password`

2. Build the Docker image and push it to the registry.
   - `make build-docker`
   - `docker tag calgo-lab/green-db-worker:<package-version> <docker-registry>/green-db-worker:<package-version>`
   - If necessary login, e.g.: `docker login <docker-registry> -u <user-name> -p <password>`
   - `docker push <docker-registry>/green-db-worker:<package-version>`

Then run the following command. Make sure you replaced the placeholders (`<...>`) appropriately.

```bash
QUEUE=<queue-name>
helm install green-db-worker-$QUEUE --set image.repository=<docker-registry>/green-db-worker --set imagePullSecrets\[0\].name=<pull-secret-for-docker-registry> --set queue=$QUEUE charts/green-db-worker
```
