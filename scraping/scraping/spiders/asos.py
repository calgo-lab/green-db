import json
import math
from logging import getLogger
from typing import Iterator
from urllib.parse import parse_qs, urlparse

from scrapy.http.request import Request as ScrapyHttpRequest
from scrapy.http.response import Response as ScrapyHttpResponse

from ._base import BaseSpider

logger = getLogger(__name__)


class AsosSpider(BaseSpider):
    name = "asos"
    allowed_domains = ["asos.com"]
    _product_api = "https://www.asos.com/api/product/catalogue/v3/products/"
    _filters = "?currency=EUR&lang=fr-FR&sizeSchema=FR&store=FR&keyStoreDataversion=dup0qtf-35"

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",  # noqa
        "accept-encoding": "deflate",
        "accept-language": "de-DE,de;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    }

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": headers,
        "DOWNLOAD_DELAY": 15,  # decrease this to increase speed
    }

    def start_requests(self) -> Iterator[ScrapyHttpRequest]:
        """
        The `Scrapy` framework executes this method.

        Yields:
            Iterator[ScrapyHttpRequest]: Requests that will be performed
        """
        for start_url in self.start_urls:
            yield ScrapyHttpRequest(
                url=start_url,
                callback=self.parse_SERP,
                meta={"original_URL": start_url},
            )

    def parse_SERP(self, response: ScrapyHttpResponse) -> Iterator[ScrapyHttpRequest]:
        # Save HTML to database
        self._save_SERP(response)

        data = json.loads(response.body.decode("utf-8"))
        product_ids = [str(product.get("id", None)) for product in data.get("products", {})]

        # get id where id has more than 6 digits (6 digit products or less are mix & match products)
        product_ids = [product_id for product_id in product_ids if len(product_id) > 6]

        # If set a subset of the products are scraped
        if self.products_per_page:
            product_ids = product_ids[: self.products_per_page]

        logger.info(f"Number of products {len(product_ids)} to be scraped")

        for product_id in product_ids:
            yield ScrapyHttpRequest(
                url=f"{self._product_api}{product_id}{self._filters}",
                callback=self.parse_PRODUCT,
                meta={"original_URL": response.url},
                priority=1,  # higher prio than SERP => finish product requests first
            )

        # Pagination: Request SERPS if we are on start_url (offset=0)
        if "offset=0" in response.url:
            yield from self.request_SERPs(url=response.url, data=data)

    def request_SERPs(self, url: str, data: dict) -> Iterator[ScrapyHttpRequest]:
        """
        It is responsible for yielding new `ScrapyHttpRequest` for results pages (a.k.a `SERP`)
            if more products are available.

        Args:
            url (str): url of the start_url
            data (dict): responded data of initial request

        Yields:
            Iterator[ScrapyHttpRequest]: New request for each SERP necessary to get all product urls
        """

        parsed_url = urlparse(url)
        url_query_params = parse_qs(parsed_url.query)
        limit = int(url_query_params.get("limit", ["72"])[0])  # default limit is 72 products/ page
        product_count = data.get("itemCount", 0)
        logger.info(f"Total products in category: {product_count}")
        logger.info(f"Creating {math.floor(product_count/limit)} additional SERP Requests")

        # Pagination: Request SERPS if there are more available
        for offset in range(limit, product_count, limit):
            next_page = url.replace("offset=0", f"offset={offset}")
            yield ScrapyHttpRequest(
                url=next_page,
                callback=self.parse_SERP,
            )
