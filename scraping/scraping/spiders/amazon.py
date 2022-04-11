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
        print(type(response))
        # Save HTML to database
        self._save_SERP(response)
        #Get product urls
        product_urls = response.css('a.a-link-normal.s-no-outline::attr(href)').getall()
        logger.info(f"Number of products to be scraped {len(product_urls)}")
        for product_url in product_urls:
            #There are some color variations of same product that are not cpf elegible
            if 'refinements=p_n_cpf_eligible' in product_url:
                yield SplashRequest(url=f'https://www.amazon.de/{product_url}',
                                    callback=self.parse_PRODUCT,
                                    endpoint="execute",
                                    args={  # passed to Splash HTTP API
                                        "wait": self.request_timeout,
                                        "lua_source": scroll_end_of_page_script,
                                        "timeout": 180,
                                    }
                                    )

        pagination = response.css('span.s-pagination-strip a.s-pagination-item.s-pagination-button::attr(href)').getall()
        if len(pagination) != 0:
            next_page = f'https://www.amazon.de/{pagination[0]}'
            if response.url != next_page:
                yield SplashRequest(
                    url=next_page,
                    callback=self.parse_SERP,
                    # cb_kwargs=dict(is_first_page=False),
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
        else:
            logger.info(f"No second page found: {response.url}")




