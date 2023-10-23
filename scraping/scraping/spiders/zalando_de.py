import datetime
import json
from logging import getLogger
from typing import Iterator
from urllib.parse import urlsplit

from scrapy.http.request import Request as ScrapyHttpRequest
from scrapy.http.response import Response as ScrapyHttpResponse
from scrapy_playwright.page import PageMethod

from core.constants import TABLE_NAME_SCRAPING_ZALANDO_DE

from ._base import BaseSpider

logger = getLogger(__name__)

excluded_resource_types = ["image", "media"]
excluded_file_extensions = [".jpg", ".png", ".svg", ".jpeg"]

def block_requests(request):
    return (request.resource_type in excluded_resource_types) or \
        any(extension in request.url for extension in excluded_file_extensions)


class ZalandoSpider(BaseSpider):
    name = TABLE_NAME_SCRAPING_ZALANDO_DE
    source, _ = name.rsplit("_", 1)
    allowed_domains = ["zalando.de"]

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "LOG_LEVEL": "INFO",
        # Abort requests which are not of type document e.g. images, scripts, etc.
        # all types: https://playwright.dev/python/docs/api/class-request#request-resource-type
        # Routing disables http caching (e.g. scripts are not saved)
        "PLAYWRIGHT_ABORT_REQUEST": block_requests,
    }

    _playwright_meta = {
        "playwright": True,
        "playwright_page_methods": [
            PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
            PageMethod("wait_for_load_state", "domcontentloaded"),
        ],
    }

    def __init__(self, timestamp: datetime.datetime, **kwargs):  # type: ignore
        super().__init__(timestamp, **kwargs)
        self.StartRequest = ScrapyHttpRequest

    def parse_SERP(
        self, response: ScrapyHttpResponse, is_first_page: bool = True
    ) -> Iterator[ScrapyHttpRequest]:
        if original_URL := response.meta.get("original_URL"):
            if urlsplit(response.url).path.strip("/") != urlsplit(original_URL).path.strip("/"):
                # If Zalando do not have results for a given filter,
                # the will redirect to a page where results are found.
                # Therefore, the URL path changes and we should return here
                # and do not use those products,
                # because this disturbs our product categories..
                logger.info("Got redirected!")
                logger.info(f"Request Path:  {urlsplit(original_URL).path.strip('/')}")
                logger.info(f"Response Path: {urlsplit(response.url).path.strip('/')}")
                return None

        # Save HTML to database
        self._save_SERP(response)

        # Splash does not load all the links into the html, so we have to extract the links
        # from a JSON stored inside a script tag
        data = json.loads(response.css("script.re-data-el-hydrate::text").get())
        all_product_links = []

        # Loop over all items and retrieve the product url
        for key, value in data.get("graphqlCache", {}).items():
            url = value.get("data", {}).get("product", {}).get("uri")
            if url is not None:
                all_product_links.append(url)

        all_product_links = list(set(all_product_links))

        # If set a subset of the products are scraped
        if self.products_per_page:
            all_product_links = all_product_links[: self.products_per_page]

        logger.info(f"Number of products per page {len(all_product_links)} to be scraped")

        for product_link in all_product_links:
            yield ScrapyHttpRequest(
                url=product_link,
                callback=self.parse_PRODUCT,
                priority=2,
                meta=self._playwright_meta | self.create_default_request_meta(response),
            )

        # Pagination: Parse next SERP 'recursively'
        pagination = response.css('[class^="DJxzzA"]::attr(href)').getall()

        if (is_first_page and pagination) or len(pagination) == 2:
            next_page = response.urljoin(pagination[-1])
            yield ScrapyHttpRequest(
                url=next_page,
                callback=self.parse_SERP,
                cb_kwargs=dict(is_first_page=False),
                meta=response.meta,
                priority=1,
            )
        else:
            logger.info(f"No further pages: {response.url}")
