from logging import getLogger

from core.constants import TABLE_NAME_SCRAPING_AMAZON_GB

from .amazon_de import AmazonSpider

logger = getLogger(__name__)


class AmazonFrSpider(AmazonSpider):
    name = TABLE_NAME_SCRAPING_AMAZON_GB
    allowed_domains = ["amazon.co.uk"]
