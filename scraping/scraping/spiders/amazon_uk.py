from logging import getLogger

from .amazon import AmazonSpider

logger = getLogger(__name__)


class AmazonFrSpider(AmazonSpider):
    name = "amazon_uk"
    allowed_domains = ["amazon.co.uk"]
