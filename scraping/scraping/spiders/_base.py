import json
from abc import abstractmethod
from datetime import datetime
from logging import getLogger
from typing import Any, Dict, Iterator, List, Optional, Union

from message_queue import MessageQueue
from scrapy import Spider
from scrapy.http.response import Response as ScrapyHttpResponse
from scrapy.http.response.text import TextResponse as ScrapyTextResponse
from scrapy_splash import SplashJsonResponse, SplashRequest

from core.constants import (
    TABLE_NAME_SCRAPING_AMAZON_DE,
    TABLE_NAME_SCRAPING_AMAZON_FR,
    TABLE_NAME_SCRAPING_ASOS_FR,
    TABLE_NAME_SCRAPING_HM_FR,
    TABLE_NAME_SCRAPING_OTTO_DE,
    TABLE_NAME_SCRAPING_ZALANDO_DE,
    TABLE_NAME_SCRAPING_ZALANDO_FR,
    TABLE_NAME_SCRAPING_ZALANDO_GB,
)
from core.domain import PageType, ScrapedPage

from ..splash import minimal_script
from ..start_scripts.amazon_de import get_settings as get_amazon_de_settings
from ..start_scripts.amazon_fr import get_settings as get_amazon_fr_settings
from ..start_scripts.asos_fr import get_settings as get_asos_fr_settings
from ..start_scripts.hm_fr import get_settings as get_hm_fr_settings
from ..start_scripts.otto_de import get_settings as get_otto_de_settings
from ..start_scripts.zalando_de import get_settings as get_zalando_de_settings
from ..start_scripts.zalando_fr import get_settings as get_zalando_fr_settings
from ..start_scripts.zalando_uk import get_settings as get_zalando_uk_settings

logger = getLogger(__name__)

SETTINGS = {
    TABLE_NAME_SCRAPING_OTTO_DE: get_otto_de_settings(),
    TABLE_NAME_SCRAPING_ASOS_FR: get_asos_fr_settings(),
    TABLE_NAME_SCRAPING_ZALANDO_DE: get_zalando_de_settings(),
    TABLE_NAME_SCRAPING_ZALANDO_FR: get_zalando_fr_settings(),
    TABLE_NAME_SCRAPING_ZALANDO_GB: get_zalando_uk_settings(),
    TABLE_NAME_SCRAPING_HM_FR: get_hm_fr_settings(),
    TABLE_NAME_SCRAPING_AMAZON_DE: get_amazon_de_settings(),
    TABLE_NAME_SCRAPING_AMAZON_FR: get_amazon_fr_settings(),
}


class BaseSpider(Spider):
    def __init__(
        self,
        timestamp: datetime,
        start_urls: Optional[Union[str, List[str]]] = None,
        category: Optional[str] = None,
        gender: Optional[str] = None,
        consumer_lifestage: Optional[str] = None,
        search_term: Optional[str] = None,
        meta_data: Optional[Union[str, Dict[str, str]]] = None,
        products_per_page: Optional[int] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        """
        Base `class` for all spiders.
        It implements a bunch of methods that are re-used by child classes.
        Also, defines an `abstractmethod` that needs to implemented.

        Args:
            timestamp (datetime): When was this scraping run started
            start_urls (Optional[Union[str, List[str]]], optional): URL the spider should start at
            category (Optional[str], optional): All products found belong to this category
            gender (Optional[str]): All products found belong to this gender
            consumer_lifestage (Optional[str]): All products found belong to this consumer_lifestage
            search_term (Optional[str], optional): Meta information about this scraping run.
                Defaults to None.
            meta_data (Optional[Union[str, Dict[str, str]]], optional): Additional meta information
                that could be useful downstream. Defaults to None.
            products_per_page (Optional[int], optional): Limits how many products should be
                scraped for each starting page. Defaults to None.
        """

        if not self.name:
            logger.error("It's necessary to set the Spider's 'name' attribute.")

        super().__init__(name=self.name, **kwargs)
        self.table_name: str = getattr(self, "table_name", self.name)  # type: ignore
        self.merchant, self.country = self.name.rsplit("_", 1)

        # set default value
        self.request_timeout = getattr(self, "request_timeout", 0.5)
        self.StartRequest = SplashRequest  # default StartRequest is set to SplashRequest
        self.source = self.merchant  # TODO: change when source is no more equal to merchant

        self.timestamp = timestamp
        self.message_queue = MessageQueue()

        if start_urls:
            self.start_urls = start_urls
            if category:
                self.category = category
                self.meta_data = meta_data
                self.gender = gender
                self.consumer_lifestage = consumer_lifestage
                if search_term and self.meta_data:
                    self.meta_data |= {"search_term": search_term}  # type: ignore
                elif search_term:
                    self.meta_data = {"search_term": search_term}  # type: ignore
            else:
                logger.error("When setting 'start_urls', 'category', also needs to be set.")
        else:
            logger.info("Spider will be initialized using start_script.")

        # By default there will be no limit to the amount of products scraped per page
        self.products_per_page = int(products_per_page) if products_per_page else products_per_page

    @staticmethod
    def parse_urls(start_urls: Union[str, List[str]]) -> List[str]:  # type: ignore
        """
        Helper method to parse start_urls.

        Args:
            start_urls: Additional meta information that could be useful downstream.

        Returns:
            List[str]: start_urls represented as a List.
        """
        if not (type(start_urls) == str or type(start_urls) == list):
            logger.error(
                "Argument 'start_urls' need to be of type list or (comma-separated) string."
            )
        else:
            return start_urls.split(",") if type(start_urls) == str else start_urls  # type: ignore

    @staticmethod
    def parse_meta_data(meta_data: Union[Dict[str, str], str]) -> Union[dict, None]:  # type: ignore
        """
        Helper method to parse meta_data.

        Args:
            meta_data: Additional meta information that could be useful downstream.

        Returns:
            dict: meta_data represented as dict.
        """
        if meta_data:
            meta_data = json.loads(meta_data) if isinstance(meta_data, str) else meta_data  # type: ignore # noqa
            if isinstance(meta_data, dict):
                return meta_data  # type: ignore
            else:
                logger.error(
                    "Argument 'meta_data' needs to be of type dict or serialized JSON " "string."
                )
                return None  # type: ignore
        return None

    def start_requests(self) -> Iterator[SplashRequest]:
        """
        The `Scrapy` framework executes this method. If start_urls are set, the spider will just
        crawl the specified urls. If no start_urls are specified (default) the spider will read
        all settings from its respective start_script file and generate start_requests.

        Yields:
            Iterator[SplashRequest]: Requests that will be performed
        """

        def get_request_specific_parameters() -> dict:
            if self.StartRequest == SplashRequest:
                return {
                    "endpoint": "execute",
                    "args": {  # passed to Splash HTTP API
                        "wait": self.request_timeout,
                        "lua_source": minimal_script,
                        "timeout": 180,
                    },
                }
            return {}

        # If a start URL is given, we need to create the settings manually
        if self.start_urls:
            settings = [
                {
                    "start_urls": self.start_urls,
                    "category": self.category,
                    "gender": self.gender,
                    "consumer_lifestage": self.consumer_lifestage,
                    "meta_data": self.meta_data,
                }
            ]
        else:
            settings = SETTINGS.get(self.name)  # type: ignore

        for setting in settings:
            for start_url in self.parse_urls(setting.get("start_urls")):  # type: ignore
                yield self.StartRequest(
                    url=start_url,
                    callback=self.parse_SERP,
                    meta={
                        "category": setting.get("category"),
                        "gender": setting.get("gender"),
                        "consumer_lifestage": setting.get("consumer_lifestage"),
                        "meta_data": self.parse_meta_data(setting.get("meta_data")),  # type: ignore
                    },
                    **get_request_specific_parameters(),
                )
            logger.info(f"Crawling setting: {setting}")

    def _save_SERP(
        self, response: Union[SplashJsonResponse, ScrapyHttpResponse, ScrapyTextResponse]
    ) -> None:
        """
        Helper method for child classes. Simply instantiates a `SrapedPage` object
            and enqueues this to the scraping `Queue`.

        Args:
            response (SplashJsonResponse): Response from a performed request
        """
        scraped_page = ScrapedPage(
            timestamp=self.timestamp,
            source=self.source,
            merchant=self.merchant,
            country=self.country,
            url=response.url,
            html=response.body.decode("utf-8"),
            page_type=PageType.SERP,
            category=response.meta.get("category"),
            gender=response.meta.get("gender"),
            consumer_lifestage=response.meta.get("consumer_lifestage"),
            meta_information=response.meta.get("meta_data"),
        )

        self.message_queue.add_scraping(table_name=self.table_name, scraped_page=scraped_page)

    def parse_PRODUCT(self, response: Union[SplashJsonResponse, ScrapyHttpResponse]) -> None:
        """
        Helper method for child classes. Simply instantiates a `SrapedPage` object
            and enqueues this to the scraping `Queue`.

        Args:
            response (SplashJsonResponse): Response from a performed request
        """

        if meta_information := response.meta.get("meta_data"):
            meta_information |= response.meta.get("request_meta_information", {})
        else:
            meta_information = response.meta.get("request_meta_information")

        scraped_page = ScrapedPage(
            timestamp=self.timestamp,
            source=self.source,
            merchant=self.merchant,
            country=self.country,
            url=response.url,
            html=response.body.decode("utf-8"),
            page_type=PageType.PRODUCT,
            category=response.meta.get("category"),
            gender=response.meta.get("gender"),
            consumer_lifestage=response.meta.get("consumer_lifestage"),
            meta_information=meta_information,
        )

        self.message_queue.add_scraping(table_name=self.table_name, scraped_page=scraped_page)

    @abstractmethod
    def parse_SERP(self, response: SplashJsonResponse) -> Iterator[SplashRequest]:
        """
        Abstract method forces child classes to implement this.
        It is responsible for yielding new `SplashRequest` for each product on the `response` page
            and use pagination to the new result page (a.k.a `SERP`).

        Args:
            response (SplashJsonResponse): Response from a performed request

        Yields:
            Iterator[SplashRequest]: New request for each product on `response` page and pagination
        """

    @staticmethod
    def create_default_request_meta(
        response: Union[ScrapyTextResponse, ScrapyHttpResponse], original_url: Optional[str] = None
    ) -> Dict:
        """
        Helper method to create default request meta. All 'SERP' and 'PRODUCT' requests need to "
        "implement this. It will propagate the meta information from the original/ parent request "
        "to the child requests.

        Args:
            response (ScrapyTextResponse, ScrapyHttpResponse): Response from parent request.
            original_url (str): Optional url to set as original/ parent url instead of response.url

        Returns:
            Dict: Dict with the default meta information to use in child request.
        """

        return {
            "original_URL": original_url if original_url else response.url,
            "category": response.meta.get("category"),
            "gender": response.meta.get("gender"),
            "consumer_lifestage": response.meta.get("consumer_lifestage"),
            "meta_data": response.meta.get("meta_data"),
        }
