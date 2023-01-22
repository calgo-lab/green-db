FROM python:3.10.8

RUN mkdir /db-exporting
WORKDIR /db-exporting

RUN pip install poetry

COPY poetry.lock .
COPY poetry.toml .
COPY pyproject.toml .

RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

COPY db_exporting /db-exporting/db_exporting

ENTRYPOINT ["poetry", "run", "exporter"]