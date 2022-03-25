from logging import getLogger
from typing import Iterator

from scrapy_splash import SplashJsonResponse, SplashRequest

from ..splash import scroll_end_of_page_script
from ._base import BaseSpider

logger = getLogger(__name__)


class AsosSpider(BaseSpider):
    name = "asos"
    allowed_domains = ["asos.com"]
    api = "https://www.asos.com/api/product/catalogue/v3/products/"
    filters = "?currency=EUR&lang=fr-FR&sizeSchema=FR&store=FR&keyStoreDataversion=dup0qtf-35"

    def parse_SERP(self, response: SplashJsonResponse) -> Iterator[SplashRequest]:

        # Save HTML to database
        self._save_SERP(response)

        # get all products
        products = response.css('article._2qG85dG::attr(id)').getall()
        product_ids = [product.replace("product-", "") for product in products]
        # get id where id has more than 6 digits (6 digit products or less are mixed products)
        product_ids = [product_id for product_id in product_ids if len(product_id) > 6]

        # If set a subset of the products are scraped
        if self.products_per_page:
            product_ids = product_ids[: self.products_per_page]

        logger.info(f"Number of products per page {len(product_ids)} to be scraped")

        for product_id in product_ids:
            yield SplashRequest(
                url=''.join([self.api, product_id, self.filters]),
                callback=self.parse_PRODUCT,
                endpoint="execute",
                priority=1,  # request products before next page
                args={  # passed to Splash HTTP API
                    "wait": self.request_timeout,
                    "lua_source": scroll_end_of_page_script,
                    "timeout": 180,
                },
            )

        # Pagination: Parse next SERP if exists
        next_page = response.css('[data-auto-id=loadMoreProducts]::attr(href)').get()

        if next_page:
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
            logger.info(f"No further pages: {response.url}")
