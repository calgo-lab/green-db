import json
from enum import Enum
from typing import Any

from core.domain import ProductCategory

from ..spiders._base import SETTINGS


def enum_has_value(enum: Enum, value: Any):
    try:
        enum(value)
    except:
        return False
    return True


def test_startjob() -> None:
    for merchant, settings in SETTINGS:
        for setting in settings:
            assert "start_urls" in setting
            start_urls = setting["start_urls"]
            if isinstance(start_urls, list):
                assert all([isinstance(start_url, str) for start_url in start_urls])
            else:
                assert isinstance(start_urls, str)
            assert "category" in setting
            assert enum_has_value(ProductCategory, setting["category"])
            if "gender" in setting:
                enum_has_value(GenderType, setting["gender"])
            if "consumer_lifestage" in setting:
                enum_has_value(ConsumerLifestageType, setting["consumer_lifestage"])
            if "meta_data" in setting:
                meta_data = setting["meta_data"]
                if isinstance(meta_data, str):
                    meta_data = json.loads(meta_data)
                assert isinstance(meta_data, dict)