from logging import getLogger

from core.constants import TABLE_NAME_SCRAPING_ZALANDO_GB

from .zalando_de import ZalandoSpider

logger = getLogger(__name__)


class ZalandoGbSpider(ZalandoSpider):
    name = TABLE_NAME_SCRAPING_ZALANDO_GB
    allowed_domains = ["www.zalando.co.uk"]
