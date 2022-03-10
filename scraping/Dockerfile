FROM easypi/scrapyd:1.3.0-2.6.1

MAINTAINER calgo-lab

# Pre-installed some packages
RUN pip install redis rq poetry pydantic

COPY core /green-db/core
COPY message-queue /green-db/message-queue

# Because 'poetry install' would remove packages from the base image,
# we have to build the package and install via pip
WORKDIR /green-db/core
RUN poetry build -f wheel && pip install --no-deps dist/*.whl 

WORKDIR /green-db/message-queue
RUN poetry build -f wheel && pip install --no-deps dist/*.whl 