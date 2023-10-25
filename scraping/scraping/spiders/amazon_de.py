import datetime
from logging import getLogger
from typing import Iterator

from scrapy.http.request import Request as ScrapyHttpRequest
from scrapy.http.response import Response as ScrapyHttpResponse
from scrapy_playwright.page import PageMethod

from core.constants import TABLE_NAME_SCRAPING_AMAZON_DE

from ..utils import strip_url
from ._base import BaseSpider

logger = getLogger(__name__)

excluded_resource_types = ["image", "media"]
excluded_file_extensions = [".jpg", ".png", ".svg", ".jpeg"]


def block_requests(request):
    return (request.resource_type in excluded_resource_types) or \
        any(extension in request.url for extension in excluded_file_extensions)


class AmazonSpider(BaseSpider):
    name = TABLE_NAME_SCRAPING_AMAZON_DE
    source, _ = name.rsplit("_", 1)
    allowed_domains = ["amazon.de"]
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scraping.middlewares.RandomUserAgentMiddleware": 400,
            "scraping.middlewares.AmazonSchedulerMiddleware": 543,
            "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
        },
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",  # noqa
            "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        },
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
        # https://github.com/scrapy-plugins/scrapy-playwright#proxy-support
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "proxy": {
                "server": "http://squid:3128",
                # "username": "user",
                # "password": "pass",
            }
        }
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

    def parse_SERP(self, response: ScrapyHttpResponse) -> Iterator[ScrapyHttpRequest]:
        """
        The `Scrapy` framework executes this method.

        Yields:
            Iterator[SplashRequest]: Requests that will be performed to scrap each product page
        """
        # Save HTML to database
        self._save_SERP(response)

        # Abort scraping if SERP does not correspond to Climate Pledge Friendly (CPF) products
        # abort if amazon redirects to non-CPF SERP
        if redirect_URLs := response.request.meta.get("redirect_urls"):
            if "p_n_cpf_eligible" in redirect_URLs[0] and "p_n_cpf_eligible" not in response.url:
                logger.info(
                    f"Abort Scraping of {response.url} as Amazon redirected to a non Climate "
                    f"Pledge Friendly alternative."
                )
                return None
        # abort if non-CPF results are returned anyway
        if bool(response.css(r"div.widgetId\=correction-messages-aps-redirect").extract()):  # noqa
            logger.info(
                f"Abort Scraping of {response.url} as Amazon does not list Climate Pledge "
                f"Friendly products."
            )
            return None

        urls = response.css("div.a-row.a-size-base.a-color-base a::attr(href)").getall()
        prices = response.css(
            "div.a-row.a-size-base.a-color-base span.a-price-whole::text"
        ).getall()

        # Yield request for each product
        logger.info(f"Number of products to be scraped {len(urls)}")

        for url, price in zip(urls, prices):
            if "refinements=p_n_cpf_eligible" in url:
                yield ScrapyHttpRequest(
                    url=strip_url(response.urljoin(url)),
                    callback=self.parse_PRODUCT,
                    meta={
                        "request_meta_information": {
                            "price": price.encode("ascii", "ignore").decode()
                        },
                        "dont_merge_cookies": True,
                    }
                    | self._playwright_meta | self.create_default_request_meta(response),
                    priority=1,  # higher priority than SERP
                )

        # Pagination
        next_path = response.css(".s-pagination-selected+ .s-pagination-button::attr(href)").get()
        if next_path:
            page_number = response.css(".s-pagination-selected+ .s-pagination-button::text").get()
            next_page = strip_url(response.urljoin(next_path), {"c", "qid", "ts_id", "ref"})

            logger.info(f"Next page found, number {page_number} at {next_page}")

            yield ScrapyHttpRequest(
                url=next_page,
                callback=self.parse_SERP,
                meta=self.create_default_request_meta(response, original_url=next_page)
                | {"dont_merge_cookies": True},
            )
        else:
            logger.info(f"No further pages found for {response.url}")
