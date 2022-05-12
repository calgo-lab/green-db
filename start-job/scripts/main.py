from __future__ import annotations

import subprocess
from configparser import ConfigParser
from datetime import datetime
from typing import Any, Iterator, List

from asos import get_settings as get_asos_settings
from otto import get_settings as get_otto_settings
from zalando import get_settings as get_zalando_settings
from zalando_fr import get_settings as get_zalando_fr_settings

from core.constants import (
    TABLE_NAME_SCRAPING_ASOS,
    TABLE_NAME_SCRAPING_HM,
    TABLE_NAME_SCRAPING_OTTO,
    TABLE_NAME_SCRAPING_ZALANDO,
    TABLE_NAME_SCRAPING_ZALANDO_FR,
)

MERCHANTS = [
    TABLE_NAME_SCRAPING_ASOS,
    TABLE_NAME_SCRAPING_HM,
    TABLE_NAME_SCRAPING_OTTO,
    TABLE_NAME_SCRAPING_ZALANDO,
    TABLE_NAME_SCRAPING_ZALANDO_FR,
]

START_TIMESTAMP = datetime.utcnow()

# Read scrapy config and get target URL for local
scrapy_config_parser = ConfigParser()
scrapy_config_parser.read("/green-db/scraping/scrapy.cfg")  # Repo get cloned
SCRAPYD_CLUSTER_TARGET = scrapy_config_parser.get("deploy:in-cluster", "url")

if __name__ == "__main__":

    for merchant in MERCHANTS:
        command = f"scrapyd-client -t {SCRAPYD_CLUSTER_TARGET} schedule -p scraping --arg " \
                  f"timestamp='{START_TIMESTAMP}' {merchant}"
        output = subprocess.run(command, shell=True, capture_output=True)
        print(output.stdout.decode("utf-8"))
