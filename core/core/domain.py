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
    country: str
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
    country: str
    category: str
    name: str
    description: str
    brand: str
    sustainability_labels: conlist(CertificateType, min_items=1)  # type: ignore
    price: float
    currency: CurrencyType
    image_urls: List[str]

    colors: Optional[List[str]]
    sizes: Optional[List[str]]

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
    cred_credibility: Optional[conint(ge=0, le=100)]  # type: ignore
    eco_chemicals: Optional[conint(ge=0, le=100)]  # type: ignore
    eco_lifetime: Optional[conint(ge=0, le=100)]  # type: ignore
    eco_water: Optional[conint(ge=0, le=100)]  # type: ignore
    eco_inputs: Optional[conint(ge=0, le=100)]  # type: ignore
    eco_quality: Optional[conint(ge=0, le=100)]  # type: ignore
    eco_energy: Optional[conint(ge=0, le=100)]  # type: ignore
    eco_waste_air: Optional[conint(ge=0, le=100)]  # type: ignore
    eco_environmental_management: Optional[conint(ge=0, le=100)]  # type: ignore
    social_labour_rights: Optional[conint(ge=0, le=100)]  # type: ignore
    social_business_practice: Optional[conint(ge=0, le=100)]  # type: ignore
    social_social_rights: Optional[conint(ge=0, le=100)]  # type: ignore
    social_company_responsibility: Optional[conint(ge=0, le=100)]  # type: ignore
    social_conflict_minerals: Optional[conint(ge=0, le=100)]  # type: ignore

    class Config:
        orm_mode = True
        use_enum_values = True
