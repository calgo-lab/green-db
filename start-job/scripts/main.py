import subprocess
from configparser import ConfigParser
from datetime import datetime

from asos import get_settings as get_asos_settings
from otto import get_settings as get_otto_settings
from zalando import get_settings as get_zalando_settings

from core.constants import (
    TABLE_NAME_SCRAPING_ASOS,
    TABLE_NAME_SCRAPING_OTTO,
    TABLE_NAME_SCRAPING_ZALANDO,
)

START_TIMESTAMP = datetime.utcnow()
SETTINGS = {
    TABLE_NAME_SCRAPING_OTTO: get_otto_settings(),
    TABLE_NAME_SCRAPING_ZALANDO: get_zalando_settings(),
    TABLE_NAME_SCRAPING_ASOS: get_asos_settings(),
}

# Read scrapy config and get target URL for local
scrapy_config_parser = ConfigParser()
scrapy_config_parser.read("/green-db/scraping/scrapy.cfg")  # Repo get cloned
SCRAPYD_CLUSTER_TARGET = scrapy_config_parser.get("deploy:in-cluster", "url")


if __name__ == "__main__":

    for merchant, settings in SETTINGS.items():
        for setting in settings:
            url = setting["start_urls"]
            category = setting["category"]
            meta_data = setting["meta_data"]

            # -t in-cluster gets pachted by entrypoint.sh...
            command = f"scrapyd-client -t {SCRAPYD_CLUSTER_TARGET} schedule -p scraping --arg start_urls='{url}' \
            --arg category='{category}' --arg timestamp='{START_TIMESTAMP}' \
            --arg meta_data='{meta_data}' {merchant}"
            output = subprocess.run(command, shell=True, capture_output=True)
            print(output.stdout.decode("utf-8"))
