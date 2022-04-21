from logging import getLogger

from .zalando import ZalandoSpider

logger = getLogger(__name__)


class ZalandoFrSpider(ZalandoSpider):
    name = "zalando_fr"
    allowed_domains = ["zalando.fr"]
