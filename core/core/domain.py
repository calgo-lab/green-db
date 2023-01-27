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


class CountryType(str, Enum):
    DE = "DE"
    GB = "GB"
    FR = "FR"


class GenderType(str, Enum):
    FEMALE = "FEMALE"
    MALE = "MALE"
    UNISEX = "UNISEX"
    UNIDENTIFIED = "UNIDENTIFIED"
    UNCLASSIFIED = "UNCLASSIFIED"


class ConsumerLifestageType(str, Enum):
    ADULT = "ADULT"
    ALL_AGES = "ALL AGES"
    BABY_INFANT = "BABY/INFANT"
    CHILD_1_to_2_YEARS = "CHILD 1-2 YEARS"
    CHILD_2_YEARS_ONWARDS = "CHILD 2 YEARS ONWARDS"
    UNIDENTIFIED = "UNIDENTIFIED"
    UNCLASSIFIED = "UNCLASSIFIED"


class ScrapedPage(BaseModel):
    timestamp: datetime
    source: str
    merchant: str
    country: CountryType
    url: str
    html: str
    category: str
    gender: Optional[GenderType]
    consumer_lifestage: Optional[ConsumerLifestageType]

    page_type: PageType
    meta_information: Optional[dict]
    original_URL: Optional[str]

    class Config:
        orm_mode = True
        use_enum_values = True


class Product(BaseModel):
    timestamp: datetime
    url: str
    source: str
    merchant: str
    country: CountryType
    category: str
    name: str
    description: str
    brand: str
    sustainability_labels: conlist(CertificateType, min_items=1)  # type: ignore
    price: float
    currency: CurrencyType
    image_urls: List[str]

    gender: Optional[GenderType]
    consumer_lifestage: Optional[ConsumerLifestageType]
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


# if you make an edge case decision, please document it here.
class ProductCategory(str, Enum):

    # bags
    BACKPACK = "BACKPACK"
    BAG = "BAG"

    # fashion
    SKIRT = "SKIRT"
    SHOES = "SHOES"  # includes slippers.

    # casual or all purpose athletic shoes
    # dont include shoes if theyre only used for one specific sport
    # eg. football/soccer boots
    SNEAKERS = "SNEAKERS"

    SOCKS = "SOCKS"  # does not include tights/pantyhoses or leggings
    UNDERWEAR = "UNDERWEAR"  # includes tights/pantyhoses
    PANTS = "PANTS"  # includes leggings
    JEANS = "JEANS"
    SHORTS = "SHORTS"

    TOP = "TOP"
    SHIRT = "SHIRT"  # as opposed to TSHIRT.
    TSHIRT = "TSHIRT"  # as opposed to SHIRT.
    BLOUSE = "BLOUSE"
    SWEATER = "SWEATER"
    JACKET = "JACKET"  # includes vests

    SUIT = "SUIT"  # for suit sets. no individual pants/jackets/shirts
    TRACKSUIT = "TRACKSUIT"
    DRESS = "DRESS"
    OVERALL = "OVERALL"
    NIGHTWEAR = "NIGHTWEAR"  # includes bathrobes
    SWIMWEAR = "SWIMWEAR"

    # electronics
    GAMECONSOLE = "GAMECONSOLE"  # Playstations and the like. No video games.
    HEADPHONES = "HEADPHONES"  # no speakers, no headsets, just headphones.
    HEADSET = "HEADSET"
    LAPTOP = "LAPTOP"  # no tablets. For hybrids/convertibles like the Chromebook use LAPTOP.
    PRINTER = "PRINTER"  # it can be a fax but it also has to be able to print.
    SMARTPHONE = "SMARTPHONE"
    SMARTWATCH = "SMARTWATCH"
    TABLET = "TABLET"  # see also LAPTOP.
    TV = "TV"

    # household
    COOKER_HOOD = "COOKER_HOOD"
    DISHWASHER = "DISHWASHER"
    DRYER = "DRYER"  # only standalone dryers. washer-dryers are in WASHER
    FREEZER = "FREEZER"  # only standalone freezers.
    FRIDGE = "FRIDGE"  # includes Fridge-Freezers
    LINEN = "LINEN"  # bed sheets.
    OVEN = "OVEN"
    STOVE = "STOVE"
    TOWEL = "TOWEL"  # for drying yourself. No kitchen towels.
    WASHER = "WASHER"  # includes Washer-Dryers
