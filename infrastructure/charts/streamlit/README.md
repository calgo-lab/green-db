# `streamlit` Helm Chart


## Deploy to Kubernetes Cluster
This chart deploys a streamlit application with basic monitoring for the project.

1. Before you can deploy the helm chart, make sure the following secrets and keys exist.
   - `green-db-secret` with key `postgres-password` and `postgres-user`
   - `scraping-secret` with key `postgres-password` and `postgres-user`

2. Then run the following command.
   ```bash
   helm install streamlit .
   ```