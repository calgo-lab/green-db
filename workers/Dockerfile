FROM python:3.10.2

MAINTAINER calgo-lab

# Pre-installed some packages
RUN pip install redis rq psycopg2 poetry SQLAlchemy pydantic

COPY core /green-db/core
COPY database /green-db/database
COPY workers /green-db/workers
COPY message-queue /green-db/message-queue

WORKDIR /green-db/workers

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT ["worker"]