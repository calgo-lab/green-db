import json
from datetime import datetime
from enum import Enum
from typing import List, Optional, Type

from pydantic import BaseModel, conint, conlist

# Parse JSON file with sustainability labels
with open('sustainability-labels.json') as file:
    sustainability_labels = json.load(file)
    tag = "certificate:"

    _certificate_2_id = {certificate.replace(tag, ""): certificate
                         for certificate in sustainability_labels.keys()}

# Add special labels (not included in JSON)
_certificate_2_id["OTHER"] = "certificate:OTHER"
_certificate_2_id["UNKNOWN"] = "certificate:UNKNOWN"


class Certificates(str, Enum):
    """
    We use the `Enum` Functional API: https://docs.python.org/3/library/enum.html#functional-api
    to construct an Enum based on the sustainability certificates.
    This class defines the necessary function to create custom values, here the certificate IDs
    """

    def _generate_next_value_(name: str, start, count, last_values):  # type: ignore
        return _certificate_2_id[name]


def get_certificate_enum() -> Type[Enum]:
    """
    Factory function to construct the `Enum` that contains the sustainability labels
    Returns:
        Type[Enum]: `CertificateType` `Enum` use for the domain.
    """
    return Certificates(  # type: ignore
        value="CertificateType",
        names=list(_certificate_2_id.keys()),
        module=__name__,
    )


class PageType(str, Enum):
    SERP = "SERP"
    PRODUCT = "PRODUCT"


class CurrencyType(str, Enum):
    EUR = "EUR"


class ScrapedPage(BaseModel):
    timestamp: datetime
    merchant: str
    url: str
    html: str
    page_type: PageType
    category: str
    meta_information: dict

    class Config:
        orm_mode = True
        use_enum_values = True


class Product(BaseModel):
    timestamp: datetime
    url: str
    merchant: str
    category: str
    name: str
    description: str
    brand: str
    sustainability_labels: conlist(Certificates, min_items=1)  # type: ignore
    price: float
    currency: CurrencyType
    image_urls: List[str]

    color: Optional[str]
    size: Optional[str]

    # int, source: https://support.google.com/merchants/answer/6219078?hl=en
    gtin: Optional[int]

    # str because alpha numeric
    # source: https://en.wikipedia.org/wiki/Amazon_Standard_Identification_Number
    asin: Optional[str]

    class Config:
        orm_mode = True
        use_enum_values = True


class SustainabilityLabel(BaseModel):
    id: Certificates
    timestamp: datetime
    name: str
    description: str
    ecological_evaluation: Optional[conint(ge=0, le=100)]  # type: ignore
    social_evaluation: Optional[conint(ge=0, le=100)]  # type: ignore
    credibility_evaluation: Optional[conint(ge=0, le=100)]  # type: ignore

    class Config:
        orm_mode = True
        use_enum_values = True
