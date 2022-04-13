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
    TABLE_NAME_SCRAPING_OTTO,
    TABLE_NAME_SCRAPING_ZALANDO,
    TABLE_NAME_SCRAPING_ZALANDO_FR,
)

START_TIMESTAMP = datetime.utcnow()
SETTINGS = (
    [(TABLE_NAME_SCRAPING_ASOS, x) for x in get_asos_settings()],
    [(TABLE_NAME_SCRAPING_OTTO, x) for x in get_otto_settings()],
    [(TABLE_NAME_SCRAPING_ZALANDO, x) for x in get_zalando_settings()],
    [(TABLE_NAME_SCRAPING_ZALANDO_FR, x) for x in get_zalando_fr_settings()],
)

# Read scrapy config and get target URL for local
scrapy_config_parser = ConfigParser()
scrapy_config_parser.read("/green-db/scraping/scrapy.cfg")  # Repo get cloned
SCRAPYD_CLUSTER_TARGET = scrapy_config_parser.get("deploy:in-cluster", "url")


def roundrobin(*lists: List[Any]) -> Iterator[Any]:
    """
    `roundrobin` iterates over the given `lists` in a round robin fashion.
    First elements of `lists`, second elements of `lists`, ...
    Args:
        lists (List[Any]): `roundrobin` will output elements of `lists`
            one after another.
    """
    if lists:
        for i in range(max(map(len, lists))):
            for list in lists:
                if i < len(list):
                    yield list[i]


if __name__ == "__main__":

    # Using `roundrobin` helps to mix the shops and increases scraping speed
    # since we can request them in parallel but throttle for same domain.
    for merchant, setting in roundrobin(*SETTINGS):
        url = setting["start_urls"]
        category = setting["category"]
        meta_data = setting["meta_data"]

        command = f"scrapyd-client -t {SCRAPYD_CLUSTER_TARGET} schedule -p scraping --arg start_urls='{url}' \
        --arg category='{category}' --arg timestamp='{START_TIMESTAMP}' \
        --arg meta_data='{meta_data}' {merchant}"
        output = subprocess.run(command, shell=True, capture_output=True)
        print(output.stdout.decode("utf-8"))
