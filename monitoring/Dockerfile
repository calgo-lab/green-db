FROM python:3.10.2

MAINTAINER calgo-lab

# Pre-installed some packages
RUN pip install streamlit numpy pandas plotly poetry watchdog
EXPOSE 8501

COPY core /green-db/core
COPY database /green-db/database
COPY monitoring /green-db/monitoring

WORKDIR /green-db/monitoring
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi
COPY /monitoring/monitoring/streamlit_app.py .

ENTRYPOINT ["streamlit", "run"]
CMD ["streamlit_app.py"]