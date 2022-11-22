FROM python:3.10.2

MAINTAINER calgo-lab

# Pre-installed some packages
RUN pip install streamlit numpy pandas plotly poetry psycopg2 poetry SQLAlchemy pydantic
EXPOSE 8501

COPY core /green-db/core
COPY database /green-db/database
COPY monitoring /green-db/monitoring

WORKDIR /green-db/monitoring
RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi
COPY /monitoring/monitoring .

ENTRYPOINT ["streamlit", "run"]
CMD ["Monitoring_app.py"]