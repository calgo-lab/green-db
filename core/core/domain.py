from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, conint, conlist


class LabelIDType(str, Enum):
    # These two are special "labels"
    OTHER = "certificate:OTHER"
    UNKNOWN = "certificate:UNKNOWN"

    # The following are real labels
    AISE_G = "certificate:AISE_GREEN"
    AISE_NG = "certificate:AISE_NON_GREEN"
    ASC = "certificate:AQUACULTURE_STEWARDSHIP_COUNCIL"
    BCI = "certificate:BETTER_COTTON_INITIATIVE"
    BCORP = "certificate:B_CORPORATION"
    BE = "certificate:BLUE_ANGEL"
    BE_L_CO = "certificate:BLUE_ANGEL_LAPTOPS"
    BE_LE = "certificate:BLUE_ANGEL_LEATHER"
    BE_P = "certificate:BLUE_ANGEL_PAPER"
    BE_T = "certificate:BLUE_ANGEL_TEXTILES"
    BE_WR = "certificate:BLUE_ANGEL_DETERGENTS"
    BIO = "certificate:BIO_SIEGEL"
    BIOLAND = "certificate:BIOLAND"
    BIOPARK = "certificate:BIOPARK"
    BIORE = "certificate:BIORE"
    BK = "certificate:BIOKREIS"
    BK_RF = "certificate:BIOKREIS_REGIONAL_FAIR"
    BLUES_P = "certificate:BLUESIGN_PRODUCT"
    BLUES_A = "certificate:BLUESIGN_APPROVED"
    BONSUCRO = "certificate:BONSUCRO"
    BSCI = "certificate:BUSINESS_SOCIAL_COMPLIANCE_INITIATIVE"
    BVA = "certificate:BIOCYCLIC_VEGAN_AGRICULTURE"
    CCCC = "certificate:COMMON_CODE_COFFEE_COMMUNITY"
    CCS = "certificate:CONTENT_CLAIM_STANDARD"
    CA_BC = "certificate:CA_BIOCOTTON"
    CMIA = "certificate:COTTON_MADE_IN_AFRICA"
    CNI = "certificate:CLIMATE_NEUTRAL_STANDARD"
    CP = "certificate:CLIMATE_PARTNER"
    CSE = "certificate:CERTIFIED_SUSTAINABLE_ECONOMICS"
    CTC_T_BRONZE = "certificate:CRADLE_TO_CRADLE_BRONZE"
    CTC_T_SILVER = "certificate:CRADLE_TO_CRADLE_SILVER"
    CTC_T_GOLD = "certificate:CRADLE_TO_CRADLE_GOLD"
    CTC_T_PLATIN = "certificate:CRADLE_TO_CRADLE_PLATINUM"
    CTC_WR = "certificate:CRADLE_TO_CRADLE_DETERGENTS"
    CTFL = "certificate:CARBON_TRUST_FOOTPRINT"
    DEMETER = "certificate:DEMETER"
    ECOCERT = "certificate:ECOCERT"
    ECOVIN = "certificate:ECOVIN"
    ECO_GARANTIE = "certificate:ECOGARANTIE"
    ECO_INSTITUTE = "certificate:ECO_INSTITUTE"
    ECO_PP_OEKO_TEX = "certificate:ECO_PASSPORT_OEKO_TEX"
    ECO_VEG = "certificate:ECOVEG"
    ENERGY_STAR = "certificate:ENERGY_STAR"
    EPEAT_MP = "certificate:EPEAT_MOBILE_PHONES"
    EPEAT_L_CO = "certificate:EPEAT_LAPTOPS"
    EU_BIO = "certificate:EU_BIO"
    EU_ECO = "certificate:EU_ECOLABEL"  # new
    EU_ECO_H = "certificate:EU_ECOLABEL_HARD_SURFACES"
    EU_ECO_L_CO = "certificate:EU_ECOLABEL_LAPTOPS"
    EU_ECO_WR = "certificate:EU_ECOLABEL_DETERGENTS"
    EU_ECO_P = "certificate:EU_ECOLABEL_PAPER"
    EU_ECO_T = "certificate:EU_ECOLABEL_TEXTILES"
    ETI = "certificate:ETHICAL_TRADING_INITIATIVE"
    FC = "certificate:FAIRCHOICE"
    FFL = "certificate:FAIR_FOR_LIFE"
    FLA = "certificate:FAIR_LABOR_ASSOCIATION"
    FNG = "certificate:FAIR_N_GREEN"
    FR = "certificate:FLUSTIX_RECYCLED"
    FS = "certificate:FAIR_STONE"
    FSC = "certificate:FOREST_STEWARDSHIP_COUNCIL"
    FSC_M = "certificate:FOREST_STEWARDSHIP_COUNCIL_MIX"
    FSC_R = "certificate:FOREST_STEWARDSHIP_COUNCIL_RECYCLED"
    FT = "certificate:FAIRTRADE"
    FT_B = "certificate:FAIRTRADE_COTTON"
    FT_CP = "certificate:FAIRTRADE_COTTON_PROGRAM"
    FT_TP = "certificate:FAIRTRADE_TEXTILE_PRODUCTION"
    FWF = "certificate:FAIR_WEAR_FOUNDATION"
    G_IT = "certificate:FUJITSU_GREEN_IT"
    GAEA = "certificate:GAEA_ECOLOGICAL_AGRICULTURE"
    GCS = "certificate:GOOD_CASHMERE_STANDARD"
    GEPA = "certificate:GEPA"
    GGN = "certificate:GGN"
    GK = "certificate:GREEN_BUTTON"
    GOTS_ORGANIC = "certificate:GLOBAL_ORGANIC_TEXTILE_STANDARD_95"
    GOTS_MWOM = "certificate:GLOBAL_ORGANIC_TEXTILE_STANDARD_70"
    GREEN_BRANDS = "certificate:GREEN_BRANDS"
    GRS = "certificate:GLOBAL_RECYCLED_STANDARD"
    HIGG = "certificate:HIGG_INDEX_MATERIALS"
    HIH = "certificate:HAND_IN_HAND_RAPUNZEL"
    HM_C = "certificate:HM_CONSCIOUS"
    HVH = "certificate:HOLZ_VON_HIER"
    IR = "certificate:IFIXIT_REPARABILITY_INDEX"
    IGEP = "certificate:IGEP"
    ISCC = "certificate:INTERNATIONAL_SUSTAINABILITY_AND_CARBON_CERTIFICATION"
    IVN_NL = "certificate:IVN_NATURLEDER"
    IVN_NT_BEST = "certificate:IVN_NATURTEXTIL"
    LEVEL = "certificate:LEVEL"
    KLIMANEUTRAL = "certificate:KLIMANEUTRAL_NATUREOFFICE"
    LP = "certificate:LEAPING_BUNNY"
    LS_OEKO_TEX = "certificate:LEATHER_STANDARD_OEKO_TEX"
    LWG = "certificate:LEATHER_WORKING_GROUP"
    MSC = "certificate:MARINE_STEWARDSHIP_COUNCIL"
    MYCLIMATE = "certificate:MYCLIMATE"
    NATUREPLUS = "certificate:NATUREPLUS"
    NCP = "certificate:NATURE_CARE_PRODUCTS_STANDARD"
    NE_WR = "certificate:NORDIC_ECOLABEL_DETERGENTS"
    NE_L = "certificate:NORDIC_ECOLABEL_LEATHER"
    NE_T = "certificate:NORDIC_ECOLABEL_TEXTILES"
    NL_T = "certificate:NATURLAND_TEXTILES"
    NL_L = "certificate:NATURLAND_FOOD"
    NL_W = "certificate:NATURLAND_WILD_FISH"
    NLF_L = "certificate:NATURLAND_FAIR_FOOD"
    # OCS = "certificate:OCS"  # not used anywhere
    OCS_100 = "certificate:ORGANIC_CONTENT_STANDARD_100"
    OCS_BLENDED = "certificate:ORGANIC_CONTENT_STANDARD_BLENDED"
    MIG_OEKO_TEX = "certificate:MADE_IN_GREEN_OEKO_TEX"
    OEKOPAPLUS = "certificate:OEKOPAPLUS"
    OE_UZ = "certificate:AUSTRIAN_ECOLABEL"
    OE_UZ_WR = "certificate:AUSTRIAN_ECOLABEL_DETERGENTS"
    PEFC = "certificate:PROGRAMME_FOR_ENDORSEMENT_OF_FOREST_CERTIFICATION"
    PEFC_R = "certificate:PROGRAMME_FOR_ENDORSEMENT_OF_FOREST_CERTIFICATION_RECYCELED"
    PEFC_Z = "certificate:PROGRAMME_FOR_ENDORSEMENT_OF_FOREST_CERTIFICATION_CERTIFIED"
    PETA = "certificate:PETA_APPROVED"
    PP = "certificate:PRO_PLANET"
    PROVEG = "certificate:PROVEG"
    QUL = "certificate:QUL"
    RA = "certificate:RAINFOREST_ALLIANCE"
    RAL = "certificate:RAL"
    RCS_BLENDED = "certificate:RECYCLED_CLAIM_STANDARD_BLENDED"
    RCS_100 = "certificate:RECYCLED_CLAIM_STANDARD_100"
    RDS = "certificate:RESPONSIBLE_DOWN_STANDARD"
    RSB = "certificate:ROUNDTABLE_ON_SUSTAINABLE_BIOMATERIALS"
    RSPO = "certificate:ROUNDTABLE_ON_SUSTAINABLE_PALM_OIL"
    RWS = "certificate:RESPONSIBLE_WOOL_STANDARD"
    SA8000 = "certificate:SA8000"
    S100_OEKO_TEX = "certificate:OEKO_TEX_100"
    SOILA = "certificate:SOIL_ASSOCIATION"
    SGS = "certificate:SGS_INSTITUT_FRESENIUS"
    STEP_OEKO_TEX = "certificate:STEP_OEKO_TEX"
    TCO_N = "certificate:TCO_8_NOTEBOOKS"
    TCO_S = "certificate:TCO_8_SMARTPHONES"
    TUEV_GP_L = "certificate:TUEV_RHEINLAND_GREEN_PRODUCT_MARK_LAPTOPS"
    TUEV_GP_S = "certificate:TUEV_RHEINLAND_GREEN_PRODUCT_MARK_SMARTPHONES"
    UTZ = "certificate:UTZ_RAINFOREST_ALLIANCE"
    VFI = "certificate:VFI_SOZIAL_FAIR"
    VGS = "certificate:VAUDE_GREEN_SHAPE"
    VEGANBLUME = "certificate:VEGANBLUME"
    WFTO = "certificate:WORLD_FAIR_TRADE_ORGANIZATION"
    WRAP = "certificate:WORLDWIDE_RESPONSIBLE_ACCREDITED_PRODUCTION"
    XX_PLUS = "certificate:XERTIFIX_PLUS"
    XX = "certificate:XERTIFIX"


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
    sustainability_labels: conlist(LabelIDType, min_items=1)  # type: ignore
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
    id: LabelIDType
    timestamp: datetime
    name: str
    description: str
    ecological_evaluation: Optional[conint(ge=0, le=100)]  # type: ignore
    social_evaluation: Optional[conint(ge=0, le=100)]  # type: ignore
    credibility_evaluation: Optional[conint(ge=0, le=100)]  # type: ignore

    class Config:
        orm_mode = True
        use_enum_values = True
