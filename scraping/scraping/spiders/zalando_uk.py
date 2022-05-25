from logging import getLogger

from .zalando import ZalandoSpider

logger = getLogger(__name__)


class ZalandoUkSpider(ZalandoSpider):
    name = "zalando_uk"
    allowed_domains = ["www.zalando.co.uk"]
