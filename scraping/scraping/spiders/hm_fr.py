import datetime
import math
import time
from logging import getLogger
from typing import Iterator
from urllib.parse import parse_qs, urlparse

from scrapy.http.request import Request as ScrapyHttpRequest
from scrapy.http.response import Response as ScrapyHttpResponse
from scrapy_playwright.page import PageMethod

from core.constants import TABLE_NAME_SCRAPING_HM_FR

from ._base import BaseSpider

logger = getLogger(__name__)


class HMSpider(BaseSpider):
    name = TABLE_NAME_SCRAPING_HM_FR
    allowed_domains = ["hm.com"]

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "USER_AGENT": "Green Consumption Assistant",
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "LOG_LEVEL": "INFO",
        # Abort requests which are not of type document e.g. images, scripts, etc.
        # all types: https://playwright.dev/python/docs/api/class-request#request-resource-type
        # Routing disables http caching (e.g. scripts are not saved)
        "PLAYWRIGHT_ABORT_REQUEST": lambda req: req.resource_type != "document",
    }

    _playwright_meta = {
        "playwright": True,
        "playwright_page_methods": [
            PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
            PageMethod("wait_for_load_state", "domcontentloaded"),
        ],
    }

    @staticmethod
    def _check_time() -> None:
        """
        Checks the current time when the spider was initialized and awaits the necessary time to
        be compliant to robots.txt crawl time (This functionality is not supported by scrapy).
        """
        now = datetime.datetime.now()
        if now.hour in range(7, 24):
            next_day = now + datetime.timedelta(days=1)
            wait_time = datetime.datetime.combine(next_day, datetime.time.min) - now
            logger.info(f"H&M allows crawling from 0 to 9 am. Waiting {str(wait_time)} to start.")
            time.sleep(wait_time.total_seconds())

    def __init__(self, timestamp: datetime.datetime, **kwargs):  # type: ignore
        super().__init__(timestamp, **kwargs)
        self._check_time()
        self.StartRequest = ScrapyHttpRequest

    def parse_SERP(self, response: ScrapyHttpResponse) -> Iterator[ScrapyHttpRequest]:
        self._save_SERP(response)

        data = response.json()

        all_product_links = list(
            set(
                [
                    variant.get("articleLink")
                    for product in data.get("products", [])
                    for variant in product.get("swatches", {})
                ]
            )
        )

        product_count = len(data.get("products"))  # product_count is just needed for debugging
        logger.info(f"Parsing SERP with {product_count} products & {len(all_product_links)} colors")

        for product_link in all_product_links:
            yield ScrapyHttpRequest(
                url=response.urljoin(product_link),
                callback=self.parse_PRODUCT,
                priority=2,  # higher prio than SERP => finish product requests first
                meta=self._playwright_meta | self.create_default_request_meta(response),
            )

        # Pagination: Request SERPS if we are on start_url (offset=0)
        if "offset=0" in response.url:
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
        limit = int(url_query_params.get("page-size", ["72"])[0])  # default limit is 72
        product_count = data.get("total", 0)
        logger.info(f"Total products in category: {product_count}")
        logger.info(f"Creating {math.floor(product_count / limit)} additional SERP Requests")

        # Pagination: Request SERPS if there are more available
        for offset in range(limit, product_count, limit):
            next_page = url.replace("offset=0", f"offset={offset}")
            yield ScrapyHttpRequest(
                url=next_page,
                callback=self.parse_SERP,
                meta=meta,
                priority=1,
            )
