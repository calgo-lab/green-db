# `scrapyd` Helm Chart


1. Before you can deploy the helm chart, make sure the following secrets and keys exist.
   - `postgres-secret` with key `postgresql-password`

2. Then run the following command to install scrapyd.
   ```bash
   # install scrapyd
   helm install scrapyd charts/scrapyd
   ```