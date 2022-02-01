# `database` Package

The `database` package:

- implements [`connection`](./database/connection.py)s to the databases (`green-db` and `scraping`). This offers an simple API to get and write data from/to the databases.
- implements a database interface for [`postgres`](./database/postgres.py). (It's possible to use other databases)
- defines the actual [`tables`](./database/tables.py) of the GreenDB. It depends on an an implemented database interface (We use [`postgres`](./database/postgres.py)) that implements:
  - `GreenDBBaseTable`
  - `ScrapingBaseTable`
  - `bootstrap_tables`
  - `get_session_factory`
- contains a set of pre-defined [`sustainability_labels`](./database/sustainability_labels) the pre-populate the GreenDB at first startup.
