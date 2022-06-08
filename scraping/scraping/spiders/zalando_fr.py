from logging import getLogger

from core.constants import TABLE_NAME_SCRAPING_ZALANDO_FR
from .zalando import ZalandoSpider

logger = getLogger(__name__)


class ZalandoFrSpider(ZalandoSpider):
    name = TABLE_NAME_SCRAPING_ZALANDO_FR
    allowed_domains = ["zalando.fr"]
