from logging import getLogger
from typing import Iterator

from scrapy_splash import SplashJsonResponse, SplashRequest

from ..splash import scroll_end_of_page_script
from ._base import BaseSpider

logger = getLogger(__name__)


class AmazonSpider(BaseSpider):
    name = "amazon"
    allowed_domains = ["amazon.de"]

    def parse_SERP(self, response: SplashJsonResponse) -> Iterator[SplashRequest]:
        """
        The `Scrapy` framework executes this method.

        Yields:
            Iterator[SplashRequest]: Requests that will be performed to scrap each product page
        """
        # Save HTML to database
        self._save_SERP(response)
        urls = response.css("div.a-row.a-size-base.a-color-base a::attr(href)").getall()
        prices = response.css(
            "div.a-row.a-size-base.a-color-base span.a-price-whole::text"
        ).getall()
        products = dict(zip(urls, prices))

        # Yield request for each product
        logger.info(f"Number of products to be scraped {len(products)}")
        for key, value in products.items():
            if "refinements=p_n_cpf_eligible" in key:
                yield SplashRequest(
                    url=f"https://www.amazon.de{key}",
                    callback=self.parse_PRODUCT,
                    meta={"amazon_price": value}, #customized meta_information working used just in amazon
                    endpoint="execute",
                    priority=1,  # higher priority than SERP
                    args={  # passed to Splash HTTP API
                        "wait": self.request_timeout,
                        "lua_source": scroll_end_of_page_script,
                        "timeout": 180,
                    },
                )

        # Pagination
        next_path = response.css(".s-pagination-selected+ .s-pagination-button::attr(href)").get()
        if next_path:
            page_number = response.css(".s-pagination-selected+ .s-pagination-button::text").get()
            next_page = f"https://www.amazon.de{next_path}"

            logger.info(f"Next page found, number {page_number} at {next_page}")

            yield SplashRequest(
                url=next_page,
                callback=self.parse_SERP,
                meta={"original_URL": next_page},
                endpoint="execute",
                args={  # passed to Splash HTTP API
                    "wait": self.request_timeout,
                    "lua_source": scroll_end_of_page_script,
                    "timeout": 180,
                },
            )
        else:
            logger.info(f"No further pages found for {response.url}")
