FROM autogluon/autogluon:0.5.2-cpu-framework-ubuntu20.04-py3.8

MAINTAINER calgo-lab

# Pre-installed some packages
RUN pip install --upgrade --user pip
RUN pip install poetry numpy pandas flask waitress
EXPOSE 8282

COPY product-classification /green-db/product-classification

WORKDIR /green-db/product-classification
RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi
COPY /product-classification/product-classification/app.py .

ENTRYPOINT ["poetry", "run", "waitress-serve", "--port", "8282", "--call", "app:create_app"]
#ENTRYPOINT ["waitress-serve", "--port", "8282", "--call", "app:create_app"]
