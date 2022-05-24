from logging import getLogger

from .amazon import AmazonSpider

logger = getLogger(__name__)


class AmazonFrSpider(AmazonSpider):
    name = "amazon_fr"
    allowed_domains = ["amazon.fr"]
