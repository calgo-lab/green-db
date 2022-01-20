# Scraping

1. Before you can deploy the helm chart, make sure the following secrets and keys exist.
   - `postgres-secret` with key `postgresql-password`

2. Build the Docker image and push it to the registry.
   - `make build-docker`
   - `docker tag calgo-lab/scrapyd:<package-version> <docker-registry>/scrapyd:<package-version>`
   - If necessary login, e.g.: `docker login <docker-registry> -u <user-name> -p <password>`
   - `docker push <docker-registry>/scrapyd:<package-version>`

3. Then run the following commands. Make sure you replaced the placeholders (`<...>`) appropriate
   ```bash
   # install scrapyd
   helm install scrapyd --set image.repository=<docker-registry>/scrapyd --set imagePullSecrets\[0\].name=<pull-secret-for-docker-registry> charts/scrapyd

   # install splash
   helm install splash --set imagePullSecrets\[0\].name=<pull-secret-for-docker-registry> charts/splash
   ```