import json
from logging import getLogger
from typing import Iterator
from urllib.parse import urlsplit

from scrapy_splash import SplashJsonResponse, SplashRequest

from ..splash import minimal_script
from ._base import BaseSpider

logger = getLogger(__name__)


class ZalandoSpider(BaseSpider):
    name = "zalando"
    allowed_domains = ["zalando.de"]

    def parse_SERP(
        self, response: SplashJsonResponse, is_first_page: bool = True
    ) -> Iterator[SplashRequest]:

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

        # Extract links from json object
        data = json.loads(response.css("script.re-data-el-hydrate::text").get())
        all_product_links = []
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
            yield SplashRequest(
                url=product_link,
                callback=self.parse_PRODUCT,
                endpoint="execute",
                args={  # passed to Splash HTTP API
                    "wait": 5,
                    "lua_source": minimal_script,
                    "timeout": 180,
                    "allowed_content_type": "text/html",
                },
            )

        # Pagination: Parse next SERP 'recursively'
        pagination = response.css('[class="DJxzzA PgtkyN"]::attr(href)').getall()

        if (is_first_page and pagination) or len(pagination) == 2:
            next_page = response.urljoin(pagination[-1])
            yield SplashRequest(
                url=next_page,
                callback=self.parse_SERP,
                cb_kwargs=dict(is_first_page=False),
                meta={"original_URL": next_page},
                endpoint="execute",
                args={  # passed to Splash HTTP API
                    "wait": 5,
                    "lua_source": minimal_script,
                    "timeout": 180,
                    "allowed_content_type": "text/html",
                },
            )
        else:
            logger.info(f"No further pages: {response.url}")
