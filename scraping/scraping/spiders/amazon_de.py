from logging import getLogger
from typing import Iterator

from scrapy_splash import SplashJsonResponse, SplashRequest

from core.constants import TABLE_NAME_SCRAPING_AMAZON_DE

from ..splash import minimal_script
from ..utils import strip_url
from ._base import BaseSpider

logger = getLogger(__name__)


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
        },
    }

    def parse_SERP(self, response: SplashJsonResponse) -> Iterator[SplashRequest]:
        """
        The `Scrapy` framework executes this method.

        Yields:
            Iterator[SplashRequest]: Requests that will be performed to scrap each product page
        """
        # Save HTML to database
        self._save_SERP(response)

        # Abort scraping if SERP does not correspond to Climate Pledge Friendly (CPF) products
        # abort if amazon redirects to non-CPF SERP
        if redirect_URLs := response.request.meta.get('redirect_urls'):
            if ("p_n_cpf_eligible" in redirect_URLs[0] and "p_n_cpf_eligible" not in response.url):
                return None
        # abort if non-CPF results are returned anyway
        if bool(response.css("div.widgetId\=correction-messages-aps-redirect").extract()):
            return None

        urls = response.css("div.a-row.a-size-base.a-color-base a::attr(href)").getall()
        prices = response.css(
            "div.a-row.a-size-base.a-color-base span.a-price-whole::text"
        ).getall()

        # Yield request for each product
        logger.info(f"Number of products to be scraped {len(urls)}")

        for url, price in zip(urls, prices):
            if "refinements=p_n_cpf_eligible" in url:
                yield SplashRequest(
                    url=strip_url(response.urljoin(url)),
                    callback=self.parse_PRODUCT,
                    meta={
                        "request_meta_information": {
                            "price": price.encode("ascii", "ignore").decode()
                        },
                        "dont_merge_cookies": True,
                    }
                    | self.create_default_request_meta(response),
                    endpoint="execute",
                    priority=1,  # higher priority than SERP
                    args={  # passed to Splash HTTP API
                        "wait": self.request_timeout,
                        "lua_source": minimal_script,
                        "timeout": 180,
                        "allowed_content_type": "text/html",
                    },
                )

        # Pagination
        next_path = response.css(".s-pagination-selected+ .s-pagination-button::attr(href)").get()
        if next_path:
            page_number = response.css(".s-pagination-selected+ .s-pagination-button::text").get()
            next_page = strip_url(response.urljoin(next_path), {"c", "qid", "ts_id", "ref"})

            logger.info(f"Next page found, number {page_number} at {next_page}")

            yield SplashRequest(
                url=next_page,
                callback=self.parse_SERP,
                meta=self.create_default_request_meta(response, original_url=next_page)
                | {"dont_merge_cookies": True},
                endpoint="execute",
                args={  # passed to Splash HTTP API
                    "wait": self.request_timeout,
                    "lua_source": minimal_script,
                    "timeout": 180,
                    "allowed_content_type": "text/html",
                },
            )
        else:
            logger.info(f"No further pages found for {response.url}")
