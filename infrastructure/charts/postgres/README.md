# `postgres` Helm Chart



## Create Persistent Volume Claim

Make sure you replace all the `<...>` placeholders.

```
cat <<EOF | kubectl create -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: <namespace>
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
EOF
```


## Create Secrets

```
kubectl create secret generic postgres-secret -n <namespace> --from-file=postgresql-postgres-password=../credentials/postgresql-postgres-password --from-file=postgresql-password=../credentials/postgresql-password --from-file=postgresql-replication-password=../credentials/postgresql-replication-password
```


## Install Bitnami Postgres with Custom Values

Make sure you replace all the `<...>` placeholders.


```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install postgresql bitnami/postgresql --values values.yaml --set postgresqlUsername=<name of your non-root user> --namespace <namespace>
```

## Login/Connect to your Postgres and Create the Necessary Databases

Make sure your non-root user can access them.

