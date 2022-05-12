import json
from abc import abstractmethod
from datetime import datetime
from logging import getLogger
from typing import Any, Dict, Iterator, List, Optional, Union

from message_queue import MessageQueue
from scrapy import Spider
from scrapy.http.response import Response as ScrapyHttpResponse
from scrapy.http.response.text import TextResponse as ScrapyTextResponse
from scrapy.http.request import Request as ScrapyHttpRequest, Request
from scrapy_splash import SplashJsonResponse, SplashRequest

from core.constants import (
    TABLE_NAME_SCRAPING_ASOS,
    TABLE_NAME_SCRAPING_OTTO,
    TABLE_NAME_SCRAPING_ZALANDO,
    TABLE_NAME_SCRAPING_ZALANDO_FR,
    TABLE_NAME_SCRAPING_HM,
)
from core.domain import PageType, ScrapedPage

from ..splash import scroll_end_of_page_script
from ..start_scripts.asos import get_settings as get_asos_settings
from ..start_scripts.otto import get_settings as get_otto_settings
from ..start_scripts.zalando import get_settings as get_zalando_settings
from ..start_scripts.zalando_fr import get_settings as get_zalando_fr_settings
from ..start_scripts.hm import get_settings as get_hm_settings

logger = getLogger(__name__)

SETTINGS = {
    TABLE_NAME_SCRAPING_OTTO: get_otto_settings(),
    TABLE_NAME_SCRAPING_ZALANDO: get_zalando_settings(),
    TABLE_NAME_SCRAPING_ASOS: get_asos_settings(),
    TABLE_NAME_SCRAPING_ZALANDO_FR: get_zalando_fr_settings(),
    TABLE_NAME_SCRAPING_HM: get_hm_settings(),
}


def load_meta(meta_data: str) -> dict:
    """
    Helper method to load meta_data.

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
                "Argument 'meta_data' need to be of type dict or serialized JSON string."
            )
    else:
        return None  # type: ignore


class BaseSpider(Spider):
    def __init__(
            self,
            timestamp: datetime,
            start_urls: Optional[Union[str, List[str]]] = None,
            category: Optional[str] = None,
            search_term: Optional[str] = None,
            meta_data: Optional[Union[str, Dict[str, str]]] = None,
            products_per_page: Optional[int] = None,
            **kwargs: Dict[str, Any]
    ) -> None:
        """
        Base `class` for all spiders.
        It implements a bunch of methods that are re-used by child classes.
        Also, defines an `abstractmethod` that needs to implemented.

        Args:
            start_urls (Union[str, List[str]]): URL the spider should start at
            category (str): All products found belong to this category
            timestamp (datetime): When was this scraping run started
            search_term (Optional[str], optional): Meta information about this scraping run.
                Defaults to None.
            meta_data (Optional[Union[str, Dict[str, str]]], optional): Additional meta information
                that could be useful downstream. Defaults to None.
            products_per_page (Optional[int], optional): Limits how many products should be
                scraped for each starting page. Defaults to None.
        """

        # set default value
        self.request_timeout = getattr(self, "request_timeout", 0.5)
        self.table_name: str = getattr(self, "table_name", self.name)  # type: ignore
        self.StartRequestType = SplashRequest

        super().__init__(name=self.name, **kwargs)

        self.meta_data: Optional[Dict[str, str]] = {}
        self.timestamp = timestamp
        self.message_queue = MessageQueue()

        if not self.name:
            logger.error("It's necessary to set the Spider's 'name' attribute.")

        if category:
            self.category = category

        self.meta_data = load_meta(meta_data)

        if search_term:
            self.meta_data["search_term"] = search_term  # type: ignore

        if start_urls:
            if not (type(start_urls) == str or type(start_urls) == list):
                logger.error(
                    "Argument 'start_urls' need to be of type list or (comma-separated) string."
                )
            else:
                self.start_urls = start_urls.split(",") if type(
                    start_urls) == str else start_urls  # type: ignore # noqa

        # By default there will be no limit to the amount of products scraped per page
        self.products_per_page = int(products_per_page) if products_per_page else products_per_page

    def start_requests(self) -> Iterator[SplashRequest]:
        """
        The `Scrapy` framework executes this method.

        Yields:
            Iterator[SplashRequest]: Requests that will be performed
        """
        settings = []
        if self.start_urls:
            for start_url in self.start_urls:
                settings.append(
                    {"start_urls": start_url,
                     "category": self.category,
                     "meta_data": self.meta_data})
        else:
            settings = SETTINGS.get(self.name)

        for setting in settings:
            if self.StartRequestType == ScrapyHttpRequest:
                yield ScrapyHttpRequest(
                    url=setting.get("start_urls"),
                    callback=self.parse_SERP,
                    meta={"category": setting.get("category"),
                          "meta_data": setting.get("meta_data")},
                )
            elif self.StartRequestType == SplashRequest:
                yield SplashRequest(
                    url=setting.get("start_urls"),
                    callback=self.parse_SERP,
                    meta={"category": setting.get("category"),
                          "meta_data": setting.get("meta_data")},
                    endpoint="execute",
                    args={  # passed to Splash HTTP API
                        "wait": self.request_timeout,
                        "lua_source": scroll_end_of_page_script,
                        "timeout": 180,
                    },
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
            merchant=self.name,
            url=response.url,
            html=response.body.decode("utf-8"),
            page_type=PageType.SERP,
            category=response.meta.get("category"),
            meta_information=load_meta(response.meta.get("meta_data")),
        )

        self.message_queue.add_scraping(table_name=self.table_name, scraped_page=scraped_page)

    def parse_PRODUCT(self, response: Union[SplashJsonResponse, ScrapyHttpResponse]) -> None:
        """
        Helper method for child classes. Simply instantiates a `SrapedPage` object
            and enqueues this to the scraping `Queue`.

        Args:
            response (SplashJsonResponse): Response from a performed request
        """
        scraped_page = ScrapedPage(
            timestamp=self.timestamp,
            merchant=self.name,
            url=response.url,
            html=response.body.decode("utf-8"),
            page_type=PageType.PRODUCT,
            category=response.meta.get("category"),
            meta_information=load_meta(response.meta.get("meta_data")),
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
