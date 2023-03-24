FROM python:3.10.8

MAINTAINER calgo-lab

# Pre-installed some packages
RUN pip install --upgrade --user pip
RUN pip install -U pip
RUN pip install -U setuptools wheel

#CPU version of pytorch has smaller footprint - see installation instructions in
#pytorch documentation - https://pytorch.org/get-started/locally/
RUN pip install torch==1.13.1+cpu torchvision==0.14.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
RUN pip install autogluon.multimodal

# Pre-installed some packages
RUN pip install poetry numpy pandas flask waitress sqlalchemy pydantic
EXPOSE 8282

COPY product-classification /green-db/product-classification
COPY core /green-db/core
COPY database /green-db/database

# Because 'poetry install' would remove packages from the base image,
# we have to build the package and install via pip
WORKDIR /green-db/core
RUN poetry build -f wheel && pip install --no-deps dist/*.whl

WORKDIR /green-db/database
RUN poetry build -f wheel && pip install --no-deps dist/*.whl

WORKDIR /green-db/product-classification
RUN poetry build -f wheel && pip install --no-deps dist/*.whl
#RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi

COPY /product-classification/product-classification/app.py .
ENTRYPOINT ["poetry", "run", "waitress-serve", "--port", "8282", "--call", "app:create_app"]
#ENTRYPOINT ["poetry", "run", "waitress-serve", "--port", "8282", "--call", "app.create_app"]
#ENTRYPOINT ["waitress-serve", "--port", "8282", "--call", "app:create_app"]
