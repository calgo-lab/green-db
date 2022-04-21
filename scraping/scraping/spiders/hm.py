import json
import math
from logging import getLogger
from typing import Iterator
from urllib.parse import parse_qs, urlparse

import scrapy
from scrapy.http.request import Request as ScrapyHttpRequest
from scrapy.http.response import Response as ScrapyHttpResponse
from scrapy_playwright.page import PageMethod
from ._base import BaseSpider

logger = getLogger(__name__)


class HMSpider(BaseSpider):
#class HMSpider(scrapy.Spider):
    name = "hm"
    allowed_domains = ["hm.com"]
    # start_urls = [
    #     "https://www2.hm.com/fr_fr/homme/developpement-durable/our-products.html?sort=stock&sustainabilities=Conscious+choice&productTypes=Pantalon&image-size=small&image=model&offset=0&page-size=36"
    # ]

    custom_settings = {
        "COOKIES_ENABLED": True,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "USER_AGENT": "Green Consumption Assistant",
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "LOG_LEVEL": "INFO",
        # "DUPEFILTER_DEBUG": True,

        # Abort requests which are not of type document e.g. images, scripts, etc.
        "PLAYWRIGHT_ABORT_REQUEST": lambda req: req.resource_type != "document",
        # "PLAYWRIGHT_ABORT_REQUEST": lambda req: req.resource_type == "image",
        # "PLAYWRIGHT_ABORT_REQUEST": lambda req: req.resource_type in ["image", "media"],
        # "PLAYWRIGHT_ABORT_REQUEST": lambda req: req.headers.get("Content-Type") not in ["application/json;charset=utf-8", "text/html; charset=UTF-8"]

        # "PLAYWRIGHT_LAUNCH_OPTIONS" viewport

        # Launch browser non-headless:
        #"PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False}
    }

    _playwright_meta = {
        "playwright": True,
        # "playwright_include_page": True,
        "playwright_page_methods": [
            PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
            PageMethod("wait_for_load_state", "domcontentloaded"),
        ],
    }

    def start_requests(self) -> Iterator[ScrapyHttpRequest]:
        for start_url in self.start_urls:
            yield ScrapyHttpRequest(
                url=start_url,
                callback=self.parse_SERP,
                #errback=self.errback,
                meta=self._playwright_meta,
            )

    #only needed when playwright_include_page of _playwright_meta is set to True
    #async def errback(self, failure):
    #    page = failure.request.meta["playwright_page"]
    #    await page.close()

    # async def errback(self, failure):
    #     page = failure.request.meta["playwright_page"]
    #     await page.close()

    def parse_SERP(self, response: ScrapyHttpResponse) -> Iterator[ScrapyHttpRequest]:
        # page = response.meta.get("playwright_page")
        self._save_SERP(response)

        all_links = list(set(response.css("[href]::attr(href)").getall()))
        # more links than shown products due to multiple colour variations for each item
        all_product_links = [
            response.urljoin(link) for link in all_links if "/fr_fr/productpage." in link
        ]

        # products_count is just needed for debugging
        products_count = len(response.css("li.product-item").getall())
        logger.info(f"{products_count} products and {len(all_product_links)} colors")

        for product_link in all_product_links:
            yield ScrapyHttpRequest(
                url=product_link,
                callback=self.parse_PRODUCT,
                # errback=self.errback,
                priority=1,  # higher prio than SERP => finish product requests first
                meta=self._playwright_meta,
            )

        next_page = response.css("a.pagination-links-list::attr(href)").get()

        if next_page:
            yield ScrapyHttpRequest(
                url=next_page,
                callback=self.parse_SERP,
                # errback=self.errback,
                meta=self._playwright_meta,
            )
        else:
            logger.info(f"No further pages: {response.url}")

    # await page.close()

    # def parse_SERP(self, response: ScrapyHttpResponse) -> Iterator[ScrapyHttpRequest]:
    #     self._save_SERP(response)
    #
    #     # data = response.json()
    #     data = json.loads(response.body.decode("utf-8"))
    #
    #     all_product_links = list(
    #         set(
    #             [
    #                 variation.get("articleLink")
    #                 for product in data.get("products")
    #                 for variation in product.get("swatches")
    #             ]
    #         )
    #     )
    #
    #     # products_count is just needed for debugging
    #     product_count = len(data.get("products"))
    #     logger.info(f"Parsing SERP with {product_count} products & {len(all_product_links)} colors")
    #
    #     for product_link in all_product_links:
    #         yield ScrapyHttpRequest(
    #             url=response.urljoin(product_link),
    #             callback=self.parse_PRODUCT,
    #             #errback=self.errback,
    #             priority=1,  # higher prio than SERP => finish product requests first
    #             meta=self._playwright_meta,
    #         )
    #     # Pagination: Request SERPS if we are on start_url (offset=0)
    #     if "offset=0" in response.url:
    #         yield from self.request_SERPs(url=response.url, data=data)
    #
    # def request_SERPs(self, url: str, data: dict) -> Iterator[ScrapyHttpRequest]:
    #     """
    #     It is responsible for yielding new `ScrapyHttpRequest` for results pages (a.k.a `SERP`)
    #         if more products are available.
    #
    #     Args:
    #         url (str): url of the start_url
    #         data (dict): responded data of initial request
    #
    #     Yields:
    #         Iterator[ScrapyHttpRequest]: New request for each SERP necessary to get all product urls
    #     """
    #
    #     parsed_url = urlparse(url)
    #     url_query_params = parse_qs(parsed_url.query)
    #     limit = int(url_query_params.get("limit", ["36"])[0])  # default limit is 36 products/ page
    #     product_count = data.get("total", 0)
    #     logger.info(f"Total products in category: {product_count}")
    #     logger.info(f"Creating {math.floor(product_count / limit)} additional SERP Requests")
    #
    #     # Pagination: Request SERPS if there are more available
    #     for offset in range(limit, product_count, limit):
    #         next_page = url.replace("offset=0", f"offset={offset}")
    #         yield ScrapyHttpRequest(
    #             url=next_page,
    #             callback=self.parse_SERP,
    #             #errback=self.errback,
    #             meta=self._playwright_meta,
    #         )
