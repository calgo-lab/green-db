FROM python:3.10.2

MAINTAINER calgo-lab

# Pre-installed some packages
RUN pip install redis rq psycopg2 poetry SQLAlchemy pydantic

WORKDIR /green-db
COPY core /green-db/core
COPY database /green-db/database
COPY workers /green-db/workers

WORKDIR /green-db/workers

# No virtualenv necessary in container
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT ["python3.10", "/green-db/workers/workers/main.py"]