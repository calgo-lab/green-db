# Workers

## Deploy to Kubernetes Cluster

1. Before you can deploy the helm chart, make sure the following secrets and keys exist.
   - `postgres-secret` with key `postgresql-password`
   - `root-password` with key `root-password`

2. Build the Docker image and push it to the registry.
   - `make build-docker`
   - `docker tag calgo-lab/workers:<package-version> <docker-registry>/workers:<package-version>`
   - If necessary login, e.g.: `docker login <docker-registry> -u <user-name> -p <password>`
   - `docker push <docker-registry>/workers:<package-version>`

3. Then run the following command. Make sure you replaced the placeholders (`<...>`) appropriate
   ```bash
   helm install workers --set image.repository=<docker-registry>/workers --set imagePullSecrets\[0\].name=<pull-secret-for-docker-registry> charts/workers
   ```
