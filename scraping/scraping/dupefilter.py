"""
To handle Request meta info properly a custom DupeFilter must be set.
"""
from typing import Union, Optional, Iterable

from scrapy_splash.utils import dict_hash
from scrapy.http.request import Request as ScrapyHttpRequest
from scrapy_splash.request import SplashRequest
from scrapy_splash.dupefilter import SplashAwareDupeFilter, splash_request_fingerprint

META_KEYS_FOR_FINGERPRINT = ["category", "gender", "consumer_lifestage"]


def meta_request_fingerprint(request: Union[ScrapyHttpRequest, SplashRequest],
                             include_headers: Optional[Iterable[Union[bytes, str]]] = None) -> str:
    """
    Combines selected meta information with 'SplashAwareDupeFilter' generated fingerprint and
    returns new fingerprint.

    Args:
    request Union[ScrapyHttpRequest, SplashRequest]: Request object on which to yield a request
    include_headers Optional[Iterable[Union[bytes, str]]]: request headers to consider
    """
    splash_fp = splash_request_fingerprint(request, include_headers=include_headers)
    meta = {k: v for k, v in request.meta.items() if k in META_KEYS_FOR_FINGERPRINT}
    fp_dict = meta | {"splash_fp": splash_fp}
    return dict_hash(fp_dict)


class MetaAwareDupeFilter(SplashAwareDupeFilter):
    """
    DupeFilter that includes selected meta information on top of 'SplashAwareDupeFilter'.
    It should be used with SplashMiddleware.
    """
    def request_fingerprint(self, request):
        return meta_request_fingerprint(request)
