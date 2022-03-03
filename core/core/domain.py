from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, conlist

from core.sustainability_labels import Certificate


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
    sustainability_labels: conlist(Certificate, min_items=1)  # type: ignore
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
