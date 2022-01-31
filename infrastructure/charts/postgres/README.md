# `postgres` Helm Chart

## Installation

### Create Persistent Volume Claim

```bash
cat <<EOF | kubectl create -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: greendb
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
EOF
```

### Create Postgres Secrets

```bash
kubectl create secret generic postgres-secret -n greendb --from-file=postgresql-postgres-password=../../.credentials/postgresql-postgres-password --from-file=postgresql-password=../../.credentials/postgresql-postgres-password --from-file=postgresql-replicator-password=../../.credentials/postgresql-replicator-password
```

### Install Bitnami Postgres with Custom Values

This will use the above created secret to bootstrap the postgres instance. The root users' (`postgres`) password accordingly to the content of the file `postgresql-postgres-password`, respective the replication user (`replicator`) as in file `postgresql-replicator-password`.

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install postgresql bitnami/postgresql --values values.yaml --namespace greendb
```

### Create the Necessary Users, Databases and Grant Privileges

The standard GreenDB setup requires [two databases.](../../../core/core/constants.py) Their default names are: `scraping` and `green-db`.

We recommend to use separated users for the databases and store their credentials in secrets. This is described in the following.


#### Create User

```sql
CREATE USER "green-db" WITH ENCRYPTED PASSWORD '<password>';
CREATE USER "scraping" WITH ENCRYPTED PASSWORD '<password>';
```

#### Create Database

```sql
CREATE DATABASE "green-db";
CREATE DATABASE "scraping";
```


#### Grant Privileges

```sql
GRANT CONNECT ON DATABASE "green-db" TO "green-db";
GRANT USAGE ON SCHEMA "public" TO "green-db";
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA "public" TO "green-db";

GRANT CONNECT ON DATABASE "scraping" TO "scraping";
GRANT USAGE ON SCHEMA "public" TO "scraping";
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA "public" TO "scraping";
```


#### Create Secrets

As for the postgres secret, you need to set the referenced file contents accordingly.

```bash
kubectl create secret generic scraping-secret -n greendb --from-file=postgres-user=../../.credentials/scraping-postgres-user --from-file=postgres-password=../../.credentials/scraping-postgres-password
```

```bash
kubectl create secret generic green-db-secret -n greendb --from-file=postgres-user=../../.credentials/green-db-postgres-user --from-file=postgres-password=../../.credentials/green-db-postgres-password
```
