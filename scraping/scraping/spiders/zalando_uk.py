from logging import getLogger

from core.constants import TABLE_NAME_SCRAPING_ZALANDO_UK
from .zalando_de import ZalandoSpider

logger = getLogger(__name__)


class ZalandoUkSpider(ZalandoSpider):
    name = TABLE_NAME_SCRAPING_ZALANDO_UK
    allowed_domains = ["www.zalando.co.uk"]
