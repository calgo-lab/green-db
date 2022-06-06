from __future__ import annotations

import subprocess
from configparser import ConfigParser
from datetime import datetime

from core.constants import (
    TABLE_NAME_SCRAPING_AMAZON,
    TABLE_NAME_SCRAPING_ASOS,
    TABLE_NAME_SCRAPING_HM,
    TABLE_NAME_SCRAPING_OTTO,
    TABLE_NAME_SCRAPING_ZALANDO_DE,
    TABLE_NAME_SCRAPING_ZALANDO_FR,
    TABLE_NAME_SCRAPING_ZALANDO_UK,
)

MERCHANTS = [
    TABLE_NAME_SCRAPING_ASOS,
    TABLE_NAME_SCRAPING_HM,
    TABLE_NAME_SCRAPING_OTTO,
    TABLE_NAME_SCRAPING_ZALANDO_DE,
    TABLE_NAME_SCRAPING_ZALANDO_FR,
    TABLE_NAME_SCRAPING_ZALANDO_UK,
    TABLE_NAME_SCRAPING_AMAZON,
]

START_TIMESTAMP = datetime.utcnow()

# Read scrapy config and get target URL for local scraping
scrapy_config_parser = ConfigParser()
scrapy_config_parser.read("/green-db/scraping/scrapy.cfg")  # Repo gets cloned
SCRAPYD_CLUSTER_TARGET = scrapy_config_parser.get("deploy:in-cluster", "url")

if __name__ == "__main__":

    for merchant in MERCHANTS:
        command = (
            f"scrapyd-client -t {SCRAPYD_CLUSTER_TARGET} schedule -p scraping --arg "
            f"timestamp='{START_TIMESTAMP}' {merchant}"
        )
        output = subprocess.run(command, shell=True, capture_output=True)
        print(output.stdout.decode("utf-8"))
