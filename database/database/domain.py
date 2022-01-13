from typing import Any, List, Optional

from pydantic import BaseModel, conlist


class ScrapedPage(BaseModel):
    shop: str
    start_timestamp: str
    url: str
    html: str
    page_type: str
    category: str
    meta_information: dict

    class Config:
        orm_mode = True


class Product(BaseModel):
    url: str
    shop: str
    categories: List[str]
    name: str
    description: str
    brand: str
    sustainability_labels: conlist(str, min_items=1)
    price: float
    currency: str
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
