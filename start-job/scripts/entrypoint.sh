#!/bin/sh

cd /
git clone https://github.com/calgo-lab/green-db.git
cd /green-db/core
poetry build -f wheel && pip install --no-deps dist/*.whl 

scrapyd-client deploy in-cluster

# finally start all scraping jobs
cd /workdir/scripts
python main.py
