FROM easypi/scrapyd:1.3.0-2.6.1

MAINTAINER calgo-lab

# Pre-installed some packages
RUN pip install redis rq poetry pydantic scrapy-playwright asyncio

# Playwright only fully supports installing dependencies for Ubuntu 18.04 and 20.04.
# easypi/scrapyd is based on debian:bullseye, so we have to manually install the missing deps:
# fonts-ubuntu, ttf-ubuntu-font-family, libenchant1c2a, libicu66, libjpeg-turbo8

# add non-free to all package sources, update and install wget
RUN ex +"%s/$/ non-free/g" -cwq /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y wget

# download and install the missing packages for playwright
RUN wget -i - http://ftp.de.debian.org/debian/pool/non-free/f/fonts-ubuntu/fonts-ubuntu_0.83-4_all.deb \
    http://ftp.de.debian.org/debian/pool/non-free/f/fonts-ubuntu/ttf-ubuntu-font-family_0.83-4_all.deb \
    http://ftp.de.debian.org/debian/pool/main/e/enchant/libenchant1c2a_1.6.0-11.1+b1_amd64.deb \
    http://security.ubuntu.com/ubuntu/pool/main/i/icu/libicu66_66.1-2ubuntu2.1_amd64.deb \
    http://security.ubuntu.com/ubuntu/pool/main/libj/libjpeg-turbo/libjpeg-turbo8_2.0.3-0ubuntu1.20.04.1_amd64.deb \
    && dpkg --install fonts-ubuntu_0.83-4_all.deb \
    && dpkg --install ttf-ubuntu-font-family_0.83-4_all.deb \
    && dpkg --force-all --install libenchant1c2a_1.6.0-11.1+b1_amd64.deb \
    && dpkg --install libicu66_66.1-2ubuntu2.1_amd64.deb \
    && dpkg --install libjpeg-turbo8_2.0.3-0ubuntu1.20.04.1_amd64.deb \
    && rm fonts-ubuntu_0.83-4_all.deb \
    ttf-ubuntu-font-family_0.83-4_all.deb \
    libenchant1c2a_1.6.0-11.1+b1_amd64.deb \
    libicu66_66.1-2ubuntu2.1_amd64.deb \
    libjpeg-turbo8_2.0.3-0ubuntu1.20.04.1_amd64.deb \
    && apt --fix-broken -y install

# install playwright with dependencies and chromium and cleanup:
RUN playwright install --with-deps chromium \
    && apt-get clean \
    && apt autoremove

COPY core /green-db/core
COPY message-queue /green-db/message-queue

# Because 'poetry install' would remove packages from the base image,
# we have to build the package and install via pip
WORKDIR /green-db/core
RUN poetry build -f wheel && pip install --no-deps dist/*.whl 

WORKDIR /green-db/message-queue
RUN poetry build -f wheel && pip install --no-deps dist/*.whl
