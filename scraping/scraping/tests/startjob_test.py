import json
from enum import Enum
from typing import Any, Type
from urllib.parse import urlparse

from core.domain import ConsumerLifestageType, GenderType, ProductCategory
from scraping.spiders._base import SETTINGS


def enum_has_value(enum: Type[Enum], value: Any) -> bool:
    try:
        enum(value)
    except ValueError:
        return False
    return True


def assert_is_valid_url(url: str) -> None:
    assert isinstance(url, str)
    assert "," not in url
    result = urlparse(url)
    assert result.scheme is not None and result.netloc is not None


def test_startjob() -> None:
    for merchant, settings in SETTINGS.items():
        for setting in settings:
            assert "start_urls" in setting
            assert "category" in setting

            start_urls = setting["start_urls"]
            category = setting["category"]
            gender = setting.get("gender")
            consumer_lifestage = setting.get("consumer_lifestage")
            meta_data = setting.get("meta_data")

            if isinstance(start_urls, list):
                for start_url in start_urls:
                    assert_is_valid_url(start_urls)
            else:
                assert_is_valid_url(start_urls)

            if isinstance(category, tuple):
                assert len(category) == 2
                category, category_meta_data = category
                assert isinstance(category_meta_data, dict)
            assert enum_has_value(ProductCategory, category)

            if gender is not None:
                assert enum_has_value(GenderType, gender)

            if consumer_lifestage is not None:
                assert enum_has_value(ConsumerLifestageType, consumer_lifestage)

            if meta_data is not None:
                if isinstance(meta_data, str):
                    meta_data = json.loads(meta_data)
                assert isinstance(meta_data, dict)
