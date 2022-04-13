#!/bin/sh

# clone green-db repositore
cd /
git clone https://github.com/calgo-lab/green-db.git

# install necessary dependencies
cd /green-db/core
poetry build -f wheel && pip install --no-deps dist/*.whl 

# deploy to scrapyd
cd /green-db/scraping
scrapyd-client deploy in-cluster

# and finally start all scraping jobs
cd /workdir/scripts
python main.py
