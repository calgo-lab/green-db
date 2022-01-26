# `redis` Helm Chart



## Create Persistent Volume Claim

Make sure you replace all the `<...>` placeholders.

```
cat <<EOF | kubectl create -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: <namespace>
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
EOF
```


## Create Secrets

Make sure you replace all the `<...>` placeholders.

```
kubectl create secret generic redis-secret -n <namespace> --from-file=root-password=../../.credentials/redis-root-password
```


## Install Bitnami Redis With Custom Values

```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install redis bitnami/redis --values values.yaml --namespace <namespace>
```
