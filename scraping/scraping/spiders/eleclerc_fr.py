import json
import datetime
import math

from logging import getLogger
from typing import Iterator
from urllib.parse import parse_qs, urlparse

from scrapy.http.request import Request as ScrapyHttpRequest
from scrapy.http.response import Response as ScrapyHttpResponse

from core.constants import TABLE_NAME_SCRAPING_ELECLERC_FR

from ._base import BaseSpider

logger = getLogger(__name__)


class EleclercSpider(BaseSpider):
    name = TABLE_NAME_SCRAPING_ELECLERC_FR
    source, _ = name.rsplit("_", 1)
    allowed_domains = ["e.leclerc"]
    _product_api = "https://www.e.leclerc/api/rest/live-api/product-details-by-sku/{sku}/stores/0100-0000"

    def __init__(self, timestamp: datetime.datetime, **kwargs):  # type: ignore
        super().__init__(timestamp, **kwargs)
        self.StartRequest = ScrapyHttpRequest

    def parse_SERP(self, response: ScrapyHttpResponse) -> Iterator[ScrapyHttpRequest]:
        # Save HTML to database
        self._save_SERP(response)
        data = response.json()
        skus = [product.get("sku") for product in data.get("items", {})]

        # If set a subset of the products are scraped
        if self.products_per_page:
            skus = skus[: self.products_per_page]

        logger.info(f"Number of products {len(skus)} to be scraped")

        for sku in skus:
            yield ScrapyHttpRequest(
                url=self._product_api.format(sku=sku),
                callback=self.parse_PRODUCT,
                meta=self.create_default_request_meta(response),
                priority=2,  # higher prio than SERP => finish product requests first
            )

        # Pagination: Request SERPS if we are on start_url (offset=0)
        if "page=1&" in response.url:
            yield from self.request_SERPs(url=response.url, data=data, meta=response.meta)

    def request_SERPs(self, url: str, data: dict, meta: dict) -> Iterator[ScrapyHttpRequest]:
        """
        It is responsible for yielding new `ScrapyHttpRequest` for results pages (a.k.a `SERP`)
            if more products are available.

        Args:
            meta: dict with meta information
            url (str): url of the start_url
            data (dict): responded data of initial request

        Yields:
            Iterator[ScrapyHttpRequest]: New request for each SERP necessary to get all product urls
        """

        parsed_url = urlparse(url)
        url_query_params = parse_qs(parsed_url.query)

        limit = int(url_query_params.get("size", ["30"])[0])  # default limit is 72 products/ page
        product_count = data.get("total", 0)
        logger.info(f"Total products in category: {product_count}")
        logger.info(f"Creating {math.floor(product_count/limit)} additional SERP Requests")

        # Pagination: Request SERPS if there are more available
        for offset in range(limit, product_count, limit):
            page = int(offset / limit + 1)
            next_page = url.replace("page=1", f"page={page}")
            yield ScrapyHttpRequest(
                url=next_page,
                callback=self.parse_SERP,
                meta=meta,
                priority=1,
            )
