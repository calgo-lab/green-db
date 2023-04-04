import json
from logging import getLogger
from typing import Iterator
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from scrapy_splash import SplashJsonResponse, SplashRequest

from core.constants import TABLE_NAME_SCRAPING_OTTO_DE

from ..splash import minimal_script
from ..start_scripts.otto_de import SUSTAINABILITY_FILTER
from ._base import BaseSpider

logger = getLogger(__name__)


class OttoSpider(BaseSpider):
    name = TABLE_NAME_SCRAPING_OTTO_DE
    source, _ = name.rsplit("_", 1)
    allowed_domains = ["otto.de"]
    custom_settings = {"DOWNLOAD_DELAY": 4}

    def parse_SERP(self, response: SplashJsonResponse) -> Iterator[SplashRequest]:
        # Save HTML to database
        self._save_SERP(response)

        # we exclude 'similar products', since some belong to a different category
        # preceding-sibling::* retrieves all previous nodes at the same level
        if similar_section := response.xpath(
            "//*[contains(text(), 'Ähnliche Artikel')]/preceding-sibling::*"
        ):
            all_links = list(set(similar_section.css("[href]::attr(href)").getall()))
        else:
            all_links = list(set(response.css("[href]::attr(href)").getall()))

        # Filter for product links
        all_product_links = [
            response.urljoin(link)
            for link in all_links
            if "/#variationId=" in link and "/p/" in link
        ]

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

        # Pagination uses parameters 'l' and 'o' to load next batch of products
        pagination_list = response.css(
            '[class*="js_pagingLink ts-link p_btn50"]::attr(data-page)'
        ).getall()

        if len(pagination_list) > 0:
            pagination_info = json.loads(pagination_list[-1])
            if int(pagination_info["o"]) > response.meta.get("o", 0):
                # Drop existing 'o' and 'l' parameters
                url_parsed = urlparse(response.url)
                queries = parse_qs(url_parsed.query, keep_blank_values=True)
                queries.pop("o", None)
                queries.pop("l", None)
                url_parsed = url_parsed._replace(query=urlencode(queries, True))
                url = urlunparse(url_parsed)

                if SUSTAINABILITY_FILTER in url:
                    url = f'{url.rstrip("/")}&l={pagination_info["l"]}&o={pagination_info["o"]}'
                else:
                    url = f'{url}?l={pagination_info["l"]}&o={pagination_info["o"]}'

                yield SplashRequest(
                    url=url,
                    callback=self.parse_SERP,
                    meta={"o": int(pagination_info["o"])}
                    | self.create_default_request_meta(response),
                    endpoint="execute",
                    priority=1,
                    args={  # passed to Splash HTTP API
                        "wait": 5,
                        "lua_source": minimal_script,
                        "timeout": 180,
                        "allowed_content_type": "text/html",
                    },
                )
            else:
                logger.info(f"No further pages: {response.url}")

        else:
            logger.info(f"No pagination: {response.url}")
