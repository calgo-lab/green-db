# `postgres` Helm Chart

## Installation

### Create Persistent Volume Claim

```bash
cat <<EOF | kubectl create -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
EOF
```

### Create Postgres Secrets

First, you need to choose a postgres and a replicator password. Make sure you avoid special characters.

Note that these paths are relative to ``green-db/infrastructure/charts/postgres``.

```bash
umask 077
echo -n "<some password>" > ../../.credentials/postgresql-postgres-password
echo -n "<some other password>" > ../../.credentials/postgresql-replicator-password
```

Now you can create the secret.
```bash
kubectl create secret generic postgres-secret --from-file=postgres-password=../../.credentials/postgresql-postgres-password --from-file=replicator-password=../../.credentials/postgresql-replicator-password
```


### Install Bitnami Postgres with Custom Values

This will use the above created secret to bootstrap the postgres instance. The root users' (`postgres`) password accordingly to the content of the file `postgresql-postgres-password`, respective the replication user (`replicator`) as in file `postgresql-replicator-password`.

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install postgresql bitnami/postgresql --values values.yaml
```

### Create the Necessary Users, Databases and Grant Privileges

The standard GreenDB setup requires [two databases.](../../../core/core/constants.py) Their default names are: `scraping` and `green-db`.

We recommend to use separated users for the databases and store their credentials in secrets. This is described in the following.

You need to create port forwarding to access postgres:
```bash
kubectl port-forward svc/postgresql 5432:5432
```
This allows allows you to use your favorite Postgres client to access the instance via `localhost:5432` and execute the following SQL statements.


#### Create User

```sql
CREATE USER "green-db" WITH ENCRYPTED PASSWORD '<green-db-password>';
CREATE USER "scraping" WITH ENCRYPTED PASSWORD '<scraping-password>';
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

As for the postgres secret, you need to set usernames and passwords.

```bash
umask 077
echo -n "scraping" > ../../.credentials/scraping-postgres-user
echo -n "<scraping-password>" > ../../.credentials/scraping-postgres-password
echo -n "green-db" > ../../.credentials/green-db-postgres-user
echo -n "<green-db-password>" > ../../.credentials/green-db-postgres-password
```

make sure that the usernames/passwords match those in the database.

```bash
kubectl create secret generic scraping-secret --from-file=postgres-user=../../.credentials/scraping-postgres-user --from-file=postgres-password=../../.credentials/scraping-postgres-password
```

```bash
kubectl create secret generic green-db-secret --from-file=postgres-user=../../.credentials/green-db-postgres-user --from-file=postgres-password=../../.credentials/green-db-postgres-password
```
