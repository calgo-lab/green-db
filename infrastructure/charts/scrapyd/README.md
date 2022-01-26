# `scrapyd` Helm Chart


1. Before you can deploy the helm chart, make sure the following secrets and keys exist.
   - `redis-secret` with key `root-password`

2. Then run the following command to install scrapyd.
   ```bash
   # install scrapyd
   helm install scrapyd --set image.tag=<version> .
   ```