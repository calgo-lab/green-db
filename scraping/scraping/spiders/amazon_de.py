from logging import getLogger
from typing import Iterator, Optional

from scrapy_splash import SplashJsonResponse, SplashRequest

from core.constants import TABLE_NAME_SCRAPING_AMAZON_DE

from ..splash import minimal_script
from ..utils import random_user_agent, strip_url
from ._base import BaseSpider

logger = getLogger(__name__)


class AmazonSpider(BaseSpider):
    name = TABLE_NAME_SCRAPING_AMAZON_DE
    source, _ = name.rsplit("_", 1)
    allowed_domains = ["amazon.de"]
    download_delay = 30

    def parse_SERP(
        self, response: SplashJsonResponse, user_agent: Optional[str] = None
    ) -> Iterator[SplashRequest]:
        """
        The `Scrapy` framework executes this method.

        Yields:
            Iterator[SplashRequest]: Requests that will be performed to scrap each product page
        """
        # Save HTML to database
        self._save_SERP(response)
        if user_agent is None:
            user_agent = random_user_agent()
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
                        }
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
                    headers={"User-Agent": random_user_agent()},
                )

        # Pagination
        next_path = response.css(".s-pagination-selected+ .s-pagination-button::attr(href)").get()
        if next_path:
            page_number = response.css(".s-pagination-selected+ .s-pagination-button::text").get()
            next_page = response.urljoin(next_path)

            logger.info(f"Next page found, number {page_number} at {next_page}")

            yield SplashRequest(
                url=next_page,
                callback=self.parse_SERP,
                cb_kwargs=dict(user_agent=user_agent),
                meta=self.create_default_request_meta(response, original_url=next_page),
                endpoint="execute",
                args={  # passed to Splash HTTP API
                    "wait": self.request_timeout,
                    "lua_source": minimal_script,
                    "timeout": 180,
                    "allowed_content_type": "text/html",
                },
                headers={"User-Agent": user_agent},
            )
        else:
            logger.info(f"No further pages found for {response.url}")
