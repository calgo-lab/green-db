from logging import getLogger

from core.constants import TABLE_NAME_SCRAPING_AMAZON_FR
from .amazon_de import AmazonSpider

logger = getLogger(__name__)


class AmazonFrSpider(AmazonSpider):
    name = TABLE_NAME_SCRAPING_AMAZON_FR
    allowed_domains = ["amazon.fr"]
