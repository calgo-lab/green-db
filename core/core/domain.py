from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, conint, conlist

from .sustainability_labels import create_CertificateType

CertificateType = create_CertificateType()


class PageType(str, Enum):
    SERP = "SERP"
    PRODUCT = "PRODUCT"


class CurrencyType(str, Enum):
    EUR = "EUR"
    GBP = "GBP"


class ScrapedPage(BaseModel):
    timestamp: datetime
    merchant: str
    country_code: str
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
    country_code: str
    category: str
    name: str
    description: str
    brand: str
    sustainability_labels: conlist(CertificateType, min_items=1)  # type: ignore
    price: float
    currency: CurrencyType
    image_urls: List[str]

    color: Optional[List[str]]
    size: Optional[List[str]]

    # int, source: https://support.google.com/merchants/answer/6219078?hl=en
    gtin: Optional[int]

    # str because alpha numeric
    # source: https://en.wikipedia.org/wiki/Amazon_Standard_Identification_Number
    asin: Optional[str]

    class Config:
        orm_mode = True
        use_enum_values = True


class SustainabilityLabel(BaseModel):
    id: CertificateType  # type: ignore
    timestamp: datetime
    name: str
    description: str
    ecological_evaluation: Optional[conint(ge=0, le=100)]  # type: ignore
    social_evaluation: Optional[conint(ge=0, le=100)]  # type: ignore
    credibility_evaluation: Optional[conint(ge=0, le=100)]  # type: ignore

    class Config:
        orm_mode = True
        use_enum_values = True
