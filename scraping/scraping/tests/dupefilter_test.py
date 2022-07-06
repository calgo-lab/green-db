from itertools import combinations
from typing import List

from core.domain import ConsumerLifestageType, GenderType
from scrapy import Request

from ..dupefilter import MetaAwareDupeFilter

dupefilter = MetaAwareDupeFilter()


def create_test_requests() -> List:
    url = "https://www.otto.de/p/gerry-weber-klassische-bluse-blusenshirt-aus-leinen-leger-S003T0S8#variationId=S003T0S889OC"  # noqa
    categories = ["BLOUSE", "SHIRT"]

    def create_request(
        category: str, gender: GenderType, consumer_lifestage: ConsumerLifestageType, url: str = url
    ) -> Request:
        return Request(
            url=url,
            meta={
                "category": category,
                "gender": gender,
                "consumer_lifestage": consumer_lifestage,
            },
        )

    return [
        create_request(category, gender.value, age.value)
        for gender in GenderType
        for age in ConsumerLifestageType
        for category in categories
    ]


def test_requests_fingerprint_inequality() -> None:
    requests = create_test_requests()
    for request1, request2 in combinations(requests, r=2):
        assert dupefilter.request_fingerprint(request1) != dupefilter.request_fingerprint(request2)


def test_requests_fingerprint_equality() -> None:
    requests = create_test_requests()
    for request in requests:
        request2 = request
        assert dupefilter.request_fingerprint(request) == dupefilter.request_fingerprint(request2)
