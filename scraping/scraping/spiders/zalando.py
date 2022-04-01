from logging import getLogger
from typing import Iterator
from urllib.parse import urlsplit

from scrapy_splash import SplashJsonResponse, SplashRequest

from ..splash import scroll_end_of_page_script
from ._base import BaseSpider

logger = getLogger(__name__)


class ZalandoSpider(BaseSpider):
    name = "zalando"
    allowed_domains = ["zalando.de"]

    def parse_SERP(self, response: SplashJsonResponse) -> Iterator[SplashRequest]:
        print(type(response))

        if urlsplit(response.url).path.strip("/") != urlsplit(
            response.meta["original_URL"]
        ).path.strip("/"):

            # If Zalando do not have results for a given filter,
            # the will redirect to a page where results are found.
            # Therefore, the URL path changes and we should return here
            # and do not use those products,
            # because this disturbs our product categories..
            logger.info("Got redirected!")
            logger.info(f"Request Path:  {urlsplit(response.meta['original_URL']).path.strip('/')}")
            logger.info(f"Response Path: {urlsplit(response.url).path.strip('/')}")
            return None

        # Save HTML to database
        self._save_SERP(response)

        # ads are less often than real products
        article_elements = response.css("article::attr(class)").getall()
        most_class_selector = max(set(article_elements), key=article_elements.count)
        all_product_links = response.css(f"[class='{most_class_selector}']>a::attr(href)").getall()
        all_product_links = list(set(all_product_links))

        # Scrape products on page to database
        all_product_links = [response.urljoin(link) for link in all_product_links]

        # If set a subset of the products are scraped
        if self.products_per_page:
            all_product_links = all_product_links[: self.products_per_page]

        logger.info(f"Number of products per page {len(all_product_links)} to be scraped")

        for product_link in all_product_links:
            yield SplashRequest(
                url=product_link,
                callback=self.parse_PRODUCT,
                endpoint="execute",
                args={  # passed to Splash HTTP API
                    "wait": self.request_timeout,
                    "lua_source": scroll_end_of_page_script,
                    "timeout": 180,
                },
            )

        # Pagination: Parse next SERP 'recursively'
        for next_page in response.css('[class="DJxzzA PgtkyN"]::attr(href)').getall():
            # scrapy automatically filters the previous page
            yield SplashRequest(
                url=response.urljoin(next_page),
                callback=self.parse_SERP,
                meta={"original_URL": response.urljoin(next_page)},
                endpoint="execute",
                args={  # passed to Splash HTTP API
                    "wait": self.request_timeout,
                    "lua_source": scroll_end_of_page_script,
                    "timeout": 180,
                },
            )
