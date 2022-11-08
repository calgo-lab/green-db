import json
import pkgutil
from os.path import join
from typing import Any, Set
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def get_json_data(path: str) -> Any:
    # using open here seems too trip up scrapyd-client deploy.
    data = pkgutil.get_data("scraping", join("data", path))
    assert data
    return json.loads(data.decode("utf-8"))


def strip_url(url: str, strip_keys: Set[str] = None) -> str:
    scheme, netloc, path, params, query, fragment = urlparse(url)
    if strip_keys:
        query = urlencode([(key, val) for key, val in parse_qsl(query) if key not in strip_keys])

    else:
        query = ""

    return urlunparse((scheme, netloc, path, params, query, ""))
