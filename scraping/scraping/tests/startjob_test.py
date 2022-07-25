import json
from enum import Enum
from typing import Any, Type

from core.domain import ConsumerLifestageType, GenderType, ProductCategory

from ..spiders._base import SETTINGS


def enum_has_value(enum: Type[Enum], value: Any) -> bool:
    try:
        enum(value)
    except ValueError:
        return False
    return True


def test_startjob() -> None:
    for merchant, settings in SETTINGS.items():
        for setting in settings:
            assert "start_urls" in setting
            start_urls = setting["start_urls"]
            if isinstance(start_urls, list):
                assert all([isinstance(start_url, str) for start_url in start_urls])
            else:
                assert isinstance(start_urls, str)
            assert "category" in setting
            category = setting["category"]
            if isinstance(category, tuple):
                assert len(category) == 2
                category, category_meta_data = category
                assert isinstance(category_meta_data, dict)
            assert enum_has_value(ProductCategory, category)
            if "gender" in setting:
                enum_has_value(GenderType, setting["gender"])
            if "consumer_lifestage" in setting:
                enum_has_value(ConsumerLifestageType, setting["consumer_lifestage"])
            if "meta_data" in setting:
                meta_data = setting["meta_data"]
                if isinstance(meta_data, str):
                    meta_data = json.loads(meta_data)
                assert isinstance(meta_data, dict)
