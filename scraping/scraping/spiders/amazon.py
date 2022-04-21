import json
from scrapy_splash import SplashJsonResponse, SplashRequest
from ..splash import scroll_end_of_page_script
from ._base import BaseSpider
from logging import getLogger
from typing import Iterator
from scrapy.http.request import Request as ScrapyHttpRequest
from scrapy.http.response import Response as ScrapyHttpResponse
from urllib.parse import parse_qs, urlparse

logger = getLogger(__name__)

class AmazonSpider(BaseSpider):
    name = "amazon"
    allowed_domains = ["amazon.de"]

    def parse_SERP(self,  response: SplashJsonResponse) -> Iterator[SplashRequest]:
        """
        The `Scrapy` framework executes this method.

        Yields:
            Iterator[SplashRequest]: Requests that will be performed to scrap each product page
        """
        print(type(response))
        # Save HTML to database
        self._save_SERP(response)
        # We filter the urls to avoid duplicated asins for different variations of the same product
        urls = response.css('a.a-link-normal.s-no-outline::attr(href)').getall()
        logger.info(f"Number of products scraped initially {len(urls)}")
        filtered_urls = []
        last_url_key = ''
        for url in urls:
            parsed_url = urlparse(url)
            new_url_key = parse_qs(parsed_url.path).keys()
            if (last_url_key != new_url_key) and ('refinements=p_n_cpf_eligible' in url):
                last_url_key = new_url_key
                filtered_urls.append(url)
        #TODO: Validate there are no more filters to be added
        logger.info(f"Number of products to be scraped {len(filtered_urls)}")
        #Yield request for each product
        for filtered_url in filtered_urls:
            yield SplashRequest(url=f'https://www.amazon.de{filtered_url}',
                                callback=self.parse_PRODUCT,
                                endpoint="execute",
                                priority=1,  # higher prio than SERP => finish product requests first
                                args={  # passed to Splash HTTP API
                                    "wait": self.request_timeout,
                                    "lua_source": scroll_end_of_page_script,
                                    "timeout": 180,
                                }
                                )


        #Pagination
        next_path = response.css(".s-pagination-selected+ .s-pagination-button::attr(href)").get()
        print(next_path)

        if next_path is not None:
            page_number = response.css(".s-pagination-selected+ .s-pagination-button::text").get()
            next_page = f"https://www.amazon.de{next_path}"
            logger.info(f"Next page found, number {page_number} at {next_page}")
            yield SplashRequest(url=next_page,
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











