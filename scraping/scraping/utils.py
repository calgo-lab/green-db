import json
from os.path import dirname, join
from typing import Any


def get_json_data(path: str) -> Any:
    path = join(dirname(__file__), "data", path)
    return json.loads(open(path, encoding="utf-8").read())
