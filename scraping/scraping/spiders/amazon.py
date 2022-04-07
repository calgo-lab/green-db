import json
from scrapy_splash import SplashJsonResponse, SplashRequest
from ..splash import scroll_end_of_page_script
from ._base import BaseSpider
from logging import getLogger
from typing import Iterator
from scrapy.http.request import Request as ScrapyHttpRequest
from scrapy.http.response import Response as ScrapyHttpResponse

logger = getLogger(__name__)

class AmazonSpider(BaseSpider):
    name = 'amazon'
    allowed_domains = ['amazon.de']

    def parse_SERP(self,  response: SplashJsonResponse) -> Iterator[SplashRequest]:
        """
        The `Scrapy` framework executes this method.

        Yields:
            Iterator[SplashRequest]: Requests that will be performed to scrap each product page
        """
        # Save HTML to database
        self._save_SERP(response)
        product_urls = response.css('div.a-section.a-spacing-small.s-padding-left-micro.s-padding-right-micro a::attr(href)').getall()
        print(type(product_urls))
        print(product_urls)
        logger.info(f"Number of products to be scraped {len(product_urls)}")
        #logger.info(f"Number of products in category {product_list['totalCount']}")
        for url in product_urls:
            print(url)
            #product = product_list['asins'][i]
            yield SplashRequest(url=f'https://www.amazon.de{url}',
                                callback=self.parse_PRODUCT,
                                endpoint="execute",
                                args={  # passed to Splash HTTP API
                                    "wait": self.request_timeout,
                                    "lua_source": scroll_end_of_page_script,
                                    "timeout": 180,
                                }
                                )



