import json
import pkgutil
from os.path import join
from random import randrange
from typing import Any
from urllib.parse import urlparse, urlunparse


def get_json_data(path: str) -> Any:
    # using open here seems too trip up scrapyd-client deploy.
    data = pkgutil.get_data("scraping", join("data", path))
    assert data
    return json.loads(data.decode("utf-8"))


def strip_url(url: str) -> str:
    scheme, netloc, path, params, query, fragment = urlparse(url)
    return urlunparse((scheme, netloc, path, params, "", ""))


def random_user_agent() -> str:
    os = [
        "Macintosh; Intel Mac OS X 10_15_7",
        "Macintosh; Intel Mac OS X 10_15_5",
        "Macintosh; Intel Mac OS X 10_11_6",
        "Macintosh; Intel Mac OS X 10_6_6",
        "Macintosh; Intel Mac OS X 10_9_5",
        "Macintosh; Intel Mac OS X 10_10_5",
        "Macintosh; Intel Mac OS X 10_7_5",
        "Macintosh; Intel Mac OS X 10_11_3",
        "Macintosh; Intel Mac OS X 10_10_3",
        "Macintosh; Intel Mac OS X 10_6_8",
        "Macintosh; Intel Mac OS X 10_10_2",
        "Macintosh; Intel Mac OS X 10_10_3",
        "Macintosh; Intel Mac OS X 10_11_5",
        "Windows NT 10.0; Win64; x64",
        "Windows NT 10.0; WOW64",
        "Windows NT 10.0",
    ]
    a = os[randrange(len(os))]
    b = randrange(4) + 100
    c = randrange(190) + 4100
    d = randrange(50) + 140
    return f"Mozilla/5.0 ({a}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{b}.0.{c}.{d} Safari/537.36"  # noqa
