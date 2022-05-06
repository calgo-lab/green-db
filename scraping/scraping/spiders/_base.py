import json
from abc import abstractmethod
from datetime import datetime
from logging import getLogger
from typing import Any, Dict, Iterator, List, Optional, Union

from message_queue import MessageQueue
from scrapy import Spider
from scrapy.http.response import Response as ScrapyHttpResponse
from scrapy_splash import SplashJsonResponse, SplashRequest

from core.domain import PageType, ScrapedPage

from ..splash import scroll_end_of_page_script

logger = getLogger(__name__)


class BaseSpider(Spider):
    def __init__(
        self,
        start_urls: Union[str, List[str]],
        category: str,
        timestamp: datetime,
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

        super().__init__(name=self.name, **kwargs)

        self.meta_data: Optional[Dict[str, str]] = {}
        self.timestamp = timestamp
        self.category = category
        self.message_queue = MessageQueue()

        if not self.name:
            logger.error("It's necessary to set the Spider's 'name' attribute.")

        if meta_data:
            meta_data = json.loads(meta_data) if type(meta_data) == str else meta_data

            if type(meta_data) == dict:
                self.meta_data = meta_data
                #if response.meta is not None:
                    #self.meta_data = meta_data.update(response.meta)
            else:
                logger.error(
                    "Argument 'meta_data' need to be of type dict or serialized JSON string."
                )

        if search_term:
            self.meta_data["search_term"] = search_term  # type: ignore

        self.meta_data = self.meta_data if self.meta_data else None  # type: ignore

        if not (type(start_urls) == str or type(start_urls) == list):
            logger.error(
                "Argument 'start_urls' need to be of type list or (comma-separated) string."
            )

        self.start_urls = start_urls.split(",") if type(start_urls) == str else start_urls  # type: ignore # noqa

        # By default there will be no limit to the amount of products scraped per page
        self.products_per_page = int(products_per_page) if products_per_page else products_per_page

    def start_requests(self) -> Iterator[SplashRequest]:
        """
        The `Scrapy` framework executes this method.

        Yields:
            Iterator[SplashRequest]: Requests that will be performed
        """
        for start_url in self.start_urls:
            yield SplashRequest(
                url=start_url,
                callback=self.parse_SERP,
                meta={"original_URL": start_url},
                endpoint="execute",
                args={  # passed to Splash HTTP API
                    "wait": self.request_timeout,
                    "lua_source": scroll_end_of_page_script,
                    "timeout": 180,
                },
            )

    def _save_SERP(self, response: Union[SplashJsonResponse, ScrapyHttpResponse]) -> None:
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
            category=self.category,
            meta_information=self.meta_data,
        )

        self.message_queue.add_scraping(table_name=self.table_name, scraped_page=scraped_page)

    def parse_PRODUCT(self, response: Union[SplashJsonResponse, ScrapyHttpResponse]) -> None:
        """
        Helper method for child classes. Simply instantiates a `SrapedPage` object
            and enqueues this to the scraping `Queue`.

        Args:
            response (SplashJsonResponse): Response from a performed request
        """
        if response.meta['add_meta']:
            self.meta_data.update({"price": response.meta['add_meta']})
        scraped_page = ScrapedPage(
            timestamp=self.timestamp,
            merchant=self.name,
            url=response.url,
            html=response.body.decode("utf-8"),
            page_type=PageType.PRODUCT,
            category=self.category,
            meta_information=self.meta_data,
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
