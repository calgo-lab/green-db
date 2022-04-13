from __future__ import annotations

import subprocess
from collections import deque
from configparser import ConfigParser
from datetime import datetime
from typing import Any, List

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


class RoundRobinIterator(object):
    """
    `RoundRobinIterator` iterates over the given `lists` in a round robin fashion.
    First elements of `lists`, second elements of `lists`, ...

    Args:
        lists (List[Any]): `RoundRobinIterator` will output elements of `lists`
            one after another.
    """

    def __init__(self, *lists: List[Any]) -> None:
        self._lists = [x for x in lists if type(x) == list and len(x) > 0]
        self._deque = deque([[i, 0] for i in range(len(self._lists))])

    def __iter__(self) -> RoundRobinIterator:
        return self

    def __next__(self) -> Any:
        if bool(self._deque):
            current_list, current_index = self._deque.popleft()
            if current_index + 1 != len(self._lists[current_list]):
                self._deque.append([current_list, current_index + 1])
            return self._lists[current_list][current_index]
        else:
            raise StopIteration


if __name__ == "__main__":

    # Using `RoundRobinIterator` helps to mix the shops and increases scraping speed
    # since we can request them in parallel but throttle for same domain.
    for merchant, setting in RoundRobinIterator(*SETTINGS):
        url = setting["start_urls"]
        category = setting["category"]
        meta_data = setting["meta_data"]

        command = f"scrapyd-client -t {SCRAPYD_CLUSTER_TARGET} schedule -p scraping --arg start_urls='{url}' \
        --arg category='{category}' --arg timestamp='{START_TIMESTAMP}' \
        --arg meta_data='{meta_data}' {merchant}"
        output = subprocess.run(command, shell=True, capture_output=True)
        print(output.stdout.decode("utf-8"))
