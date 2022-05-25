from __future__ import annotations

import subprocess
from configparser import ConfigParser
from datetime import datetime
from typing import Any, Iterator, List

from amazon import get_settings as get_amazon_settings
from asos import get_settings as get_asos_settings
from otto import get_settings as get_otto_settings
from zalando import get_settings as get_zalando_de_settings
from zalando_fr import get_settings as get_zalando_fr_settings
from zalando_uk import get_settings as get_zalando_uk_settings

from core.constants import (
    TABLE_NAME_SCRAPING_AMAZON,
    TABLE_NAME_SCRAPING_AMAZON_FR,
    TABLE_NAME_SCRAPING_ASOS,
    TABLE_NAME_SCRAPING_OTTO,
    TABLE_NAME_SCRAPING_ZALANDO_DE,
    TABLE_NAME_SCRAPING_ZALANDO_FR,
    TABLE_NAME_SCRAPING_ZALANDO_UK,
)

START_TIMESTAMP = datetime.utcnow()
SETTINGS = [
    [(TABLE_NAME_SCRAPING_ASOS, x) for x in get_asos_settings()],
    [(TABLE_NAME_SCRAPING_AMAZON, x) for x in get_amazon_settings()],
    [(TABLE_NAME_SCRAPING_AMAZON_FR, x) for x in get_amazon_settings()],
    [(TABLE_NAME_SCRAPING_OTTO, x) for x in get_otto_settings()],
    [(TABLE_NAME_SCRAPING_ZALANDO_DE, x) for x in get_zalando_de_settings()],
    [(TABLE_NAME_SCRAPING_ZALANDO_FR, x) for x in get_zalando_fr_settings()],
    [(TABLE_NAME_SCRAPING_ZALANDO_UK, x) for x in get_zalando_uk_settings()],
]

# Read scrapy config and get target URL for local scraping
scrapy_config_parser = ConfigParser()
scrapy_config_parser.read("/green-db/scraping/scrapy.cfg")  # Repo gets cloned
SCRAPYD_CLUSTER_TARGET = scrapy_config_parser.get("deploy:in-cluster", "url")


def get_round_robin_iterator(*lists: List[Any]) -> Iterator[Any]:
    """
    Creates an `Iterator`, which `yield`s objects in `lists` in a round robin fashion.
    This means: First elements of all `lists`, then second elements of all `lists`, ..
        until all `lists` are fully consumed.

    Args:
        lists (List[Any]): Contains `list`s of arbitrary objects and not necessary same length

    Yields:
        Iterator[Any]: Objects of `lists` in round robin fashion
    """
    if lists:
        for i in range(max(map(len, lists))):
            for list in lists:
                if i < len(list):
                    yield list[i]


if __name__ == "__main__":

    # Using `roundrobin` helps to mix the shops and increases scraping speed
    # since we can request them in parallel but throttle for same domain.
    for merchant, setting in get_round_robin_iterator(*SETTINGS):
        url = setting["start_urls"]
        category = setting["category"]
        meta_data = setting["meta_data"]

        command = f"scrapyd-client -t {SCRAPYD_CLUSTER_TARGET} schedule -p scraping --arg start_urls='{url}' \
        --arg category='{category}' --arg timestamp='{START_TIMESTAMP}' \
        --arg meta_data='{meta_data}' {merchant}"
        output = subprocess.run(command, shell=True, capture_output=True)
        print(output.stdout.decode("utf-8"))
