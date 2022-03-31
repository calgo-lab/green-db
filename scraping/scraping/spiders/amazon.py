import scrapy
import json
from scrapy_splash import SplashJsonResponse, SplashRequest
#from ..splash import scroll_end_of_page_script
from ._base import BaseSpider
from logging import getLogger

logger = getLogger(__name__)

class AmazonSpider(BaseSpider):
    name = 'amazon'
    allowed_domains = ['amazon.de']
    SERP_api = '"https://www.amazon.de/gcx/-/gfhz/api/scroll'
    filters = '?canBeEGifted=false&canBeGiftWrapped=false&categoryId=cpf-landing&count=50&isLimitedTimeOffer=false&isPrime=false&' \
              'offset=0&priceFrom=&priceTo=&searchBlob=&subcategoryIds=cpf-landing:Clothing'
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

    def start_requests(self) -> Iterator[ScrapyJsonRequest]:
        """
        The `Scrapy` framework executes this method.

        Yields:
            Iterator[ScrapyJsonRequest]: Requests that will be performed
        """
        for start_url in self.start_urls:
            yield SplashJsonResponse(
                url=start_url,
                callback=self.parse_SERP,
                meta={"original_URL": start_url},
            )

    def parse_SERP(self, response):
        product_list = json.loads(response.body)
        products_category = product_list['totalCount']
        print(products_category)
        logger.info(f"Number of products {product_list['asins']} to be scraped")
        if len(product_list['asins']) != 0:
            for i in range(0, len(product_list['asins'])):
                product = product_list['asins'][i]
                yield SplashRequest(url=f'https://www.amazon.de/dp/{product["asin"]}',
                                        callback=self.parse_PRODUCT,
                                        endpoint="execute",
                                        args={  # passed to Splash HTTP API
                                            "wait": 0.5,
                                            "lua_source": scroll_end_of_page_script,
                                            "timeout": 180,
                                    }
                                    )