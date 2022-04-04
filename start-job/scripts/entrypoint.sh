#!/bin/bash

cd /
git clone https://github.com/calgo-lab/green-db.git
cd /green-db/core
poetry build -f wheel && pip install --no-deps dist/*.whl 

# Add a ne Scrapy target that works in the cluster.
# Important: url need to be `scrapy`, which is the service name and project name is scraping
cd /green-db/scraping
cat <<EOF >> scrapy.cfg

[deploy:in-cluster]
url = http://scrapyd:6800
project = scraping
EOF

scrapyd-client deploy in-cluster

# finally start all scraping jobs
cd /workdir
python main.py
