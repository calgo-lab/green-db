# `redis` Helm Chart

## Installation

### Create Persistent Volume Claim

```bash
cat <<EOF | kubectl create -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
EOF
```


### Create Secrets

```bash
kubectl create secret generic redis-secret --from-file=root-password=../../.credentials/redis-root-password
```


### Install Bitnami Redis With Custom Values

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install redis bitnami/redis --values values.yaml
```
