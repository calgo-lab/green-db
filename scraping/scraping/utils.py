import json
import pkgutil
from os.path import join
from typing import Any


def get_json_data(path: str) -> Any:
    # using open here seems too trip up scrapyd-client deploy.
    data = pkgutil.get_data("scraping", join("data", path))
    assert data
    return json.loads(data.decode("utf-8"))
