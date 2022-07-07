"""
To handle Request meta info properly a custom DupeFilter must be set.
"""
from typing import Iterable, Optional, Union

from scrapy.http.request import Request as ScrapyHttpRequest
from scrapy_splash.dupefilter import SplashAwareDupeFilter, splash_request_fingerprint
from scrapy_splash.request import SplashRequest
from scrapy_splash.utils import dict_hash

META_KEYS_FOR_FINGERPRINT = ["category", "gender", "consumer_lifestage"]


class MetaAwareDupeFilter(SplashAwareDupeFilter):
    """
    DupeFilter that includes selected meta information on top of 'SplashAwareDupeFilter'.
    It should be used with SplashMiddleware.

    Considering the meta information is important if products (with the same url) are assigned to
    multiple product categories or genders. Scraping an url again with a different category/ gender
    allows us to write another entry to the GreenDB with those meta information, which would
    be normally filtered by 'SplashAwareDupeFilter'.
    """

    @staticmethod
    def meta_request_fingerprint(
        request: Union[ScrapyHttpRequest, SplashRequest],
        include_headers: Optional[Iterable[Union[bytes, str]]] = None,
    ) -> str:
        """
        Combines selected meta information with 'SplashAwareDupeFilter' generated fingerprint and
        returns new fingerprint.

        Args:
            request (Union[ScrapyHttpRequest, SplashRequest]): Request object on which to yield a
            request.
            include_headers (Optional[Iterable[Union[bytes, str]]], optional): Request headers to
            consider. Defaults to None.

        Returns:
            str: Request fingerprint, which is a hash that uniquely identifies the resource.
        """
        splash_fp = splash_request_fingerprint(request, include_headers=include_headers)
        meta = {k: v for k, v in request.meta.items() if k in META_KEYS_FOR_FINGERPRINT}
        fp_dict = meta | {"splash_fp": splash_fp}
        return dict_hash(fp_dict)

    def request_fingerprint(self, request: Union[ScrapyHttpRequest, SplashRequest]) -> str:
        """
        Return the request fingerprint. The request fingerprint is a hash that uniquely identifies
        the resource the request points to. This overrides the 'request_fingerprint' method in
        'SplashAwareDupeFilter'.
        """
        return self.meta_request_fingerprint(request)
