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
    #TODO: this variables will help later to iterate over the page

    headers = {
        "cookie": "session-id=260-4111553-0597163; session-id-time=2082787201l; i18n-prefs=EUR; session-token=DDsIcwXgnBm8tsZ%2FT7mbf%2BpsazpNpTyJ0SS5F8jUgH%2BL8Drkmi%2BsY%2Fg3ytkuObCTZGF%2BJ8ke1qTBlNuZAAO9BfPvSxC3fHaTcHa%2BDjr6iVfTtyOQdk4cCiI2fomOCDc4pSNpofbM4ID2rWrV9UmQyQuml8abDod0QbWPicd0GyntPcCOlK%2BjI0tECbKUEQi5",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.amazon.de/gcx/Climate-Pledge-Friendly/gfhz/events/?categoryId=cpf-landing&scrollState=eyJpdGVtSW5kZXgiOjAsInNjcm9sbE9mZnNldCI6MjQ4LjIzNTI3NTI2ODU1NDd9&sectionManagerState=eyJzZWN0aW9uVHlwZUVuZEluZGV4Ijp7ImFtYWJvdCI6MH19",
        "Content-Type": "application/json",
        "DNT": "1",
        "Connection": "keep-alive",
        "Cookie": "session-id=259-6200788-0015162; session-id-time=2082787201l; i18n-prefs=EUR; csm-hit=tb:s-8WYRN1T6VJ1G486X11HC|1648465745862&t:1648465745944&adb:adblk_no; ubid-acbde=262-9800708-6400655; session-token=nqDqe3VdYcFOkQVRqLGVKao/xkcpd3aZSgyA8fcnbtcxlh6H+60E7go0vNW0Spm8RFBWL8YqP82U+Mcse/cdMrXhICtMZZB7otRy5LHBsAGFaKBt3L7EzHt0piBCpACljM9FgXg+WDQU2tqu1RP1AXXHhiNTaHs/6Votf9JU2Oc0GsHDgR2Md5dToEdnNLfh; lc-acbde=de_DE; av-timezone=Europe/Berlin",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers"
    }
    custom_settings = {"DEFAULT_REQUEST_HEADERS": headers}

    def start_requests(self) -> Iterator[ScrapyHttpRequest]:
        """
        The `Scrapy` framework executes this method.

        Yields:
            Iterator[ScrapyHttpRequest]: Requests that will be performed
        """
        for start_url in self.start_urls:
            yield ScrapyHttpRequest(
                url=start_url,
                callback=self.parse_SERP,
                meta={"original_URL": start_url},
            )


    def parse_SERP(self,  response: ScrapyHttpResponse) -> Iterator[SplashRequest]:
        """
        The `Scrapy` framework executes this method.

        Yields:
            Iterator[SplashRequest]: Requests that will be performed to scrap each product page
        """
        # Save HTML to database
        self._save_SERP(response)
        product_list = json.loads(response.body)

        logger.info(f"Number of products to be scraped {len(product_list['asins'])}")
        logger.info(f"Number of products in category {len(product_list['totalCount'])}")
        for i in range(0, len(product_list['asins'])):
            product = product_list['asins'][i]
            yield SplashRequest(url=f'https://www.amazon.de/dp/{product["asin"]}',
                                callback=self.parse_PRODUCT,
                                endpoint="execute",
                                args={  # passed to Splash HTTP API
                                    "wait": self.request_timeout,
                                    "lua_source": scroll_end_of_page_script,
                                    "timeout": 180,
                                }
                                )
        if "offset=0" in response.url:
            yield from self.parse_next_SERP(product_list)


    def parse_next_SERP(self, product_list: dict) -> Iterator[ScrapyHttpRequest]:
        """
        The `Scrapy` framework executes this method to ask for more results as if we were scrolling.

        Yields:
            Iterator[ScrapyHttpRequest]: Requests that will be performed if category has more results to be scrapped.
        """
        n_products_category = int(product_list['totalCount'])
        print(n_products_category)
        searchBlob = product_list['searchBlob']
        print(searchBlob)
        count = 50
        offset = 0
        for i in range(0, n_products_category/count):
            offset = offset + count
            SERP_api = 'https://www.amazon.de/gcx/-/gfhz/api/scroll'
            filters = f'?canBeEGifted=false&canBeGiftWrapped=false&categoryId=cpf-landing&count={count}&isLimitedTimeOffer=false&isPrime=false&' \
                      f'offset={offset}&priceFrom=&priceTo=&searchBlob={searchBlob}&subcategoryIds=cpf-landing:Clothing'
            next_url = f'{SERP_api}{filters}'
            print(next_url)
            yield ScrapyHttpRequest(
                url=next_url,
                callback=self.parse_SERP,
                #meta={"original_URL": start_url},
                )


