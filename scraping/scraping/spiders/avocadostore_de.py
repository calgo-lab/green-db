import json
from logging import getLogger
from typing import Iterator
from urllib.parse import urlsplit

from scrapy_splash import SplashJsonResponse, SplashRequest

from core.constants import TABLE_NAME_SCRAPING_ZALANDO_DE

from ..splash import minimal_script
from ._base import BaseSpider

logger = getLogger(__name__)


class AvocadoStoreSpider(BaseSpider):
    name = TABLE_NAME_SCRAPING_AVOCADOSTORE_DE
    source, _ = name.rsplit("_", 1)
    allowed_domains = ["avocadostore.de"]
    custom_settings = {"DOWNLOAD_DELAY": 2}

    def parse_SERP(
        self, response: SplashJsonResponse, is_first_page: bool = True
    ) -> Iterator[SplashRequest]:
        if original_URL := response.meta.get("original_URL"):
            if urlsplit(response.url).path.strip("/") != urlsplit(original_URL).path.strip("/"):
                logger.info("Got redirected!")
                logger.info(f"Request Path:  {urlsplit(original_URL).path.strip('/')}")
                logger.info(f"Response Path: {urlsplit(response.url).path.strip('/')}")
                return None

        # Save HTML to database
        self._save_SERP(response)

        all_product_links = list(set(map(response.urljoin, response.css('.product-list a.product-item::attr(href)').getall())))

        # If set a subset of the products are scraped
        if self.products_per_page:
            all_product_links = all_product_links[: self.products_per_page]

        logger.info(f"Number of products per page {len(all_product_links)} to be scraped")

        for product_link in all_product_links:
            yield SplashRequest(
                url=product_link,
                callback=self.parse_PRODUCT,
                endpoint="execute",
                priority=2,
                meta=self.create_default_request_meta(response),
                args={  # passed to Splash HTTP API
                    "wait": 5,
                    "lua_source": minimal_script,
                    "timeout": 180,
                    "allowed_content_type": "text/html",
                },
            )

        # Pagination: Parse next SERP 'recursively'
        next_page = response.css('.pagination .page-link::attr(href)').getall()[-2]
        if next_page == '#':
            logger.info(f"No further pages: {response.url}")
        else:
            next_page = response.urljoin(next_page)
            yield SplashRequest(
                url=next_page,
                callback=self.parse_SERP,
                cb_kwargs=dict(is_first_page=False),
                meta=self.create_default_request_meta(response, original_url=next_page),
                endpoint="execute",
                priority=1,
                args={  # passed to Splash HTTP API
                    "wait": 5,
                    "lua_source": minimal_script,
                    "timeout": 180,
                    "allowed_content_type": "text/html",
                },
            )
