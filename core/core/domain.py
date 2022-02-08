from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, conint, conlist


class LabelIDType(str, Enum):
    # These two are special "labels"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"

    # The following are real labels
    AISE_G = "AISE_G"
    AISE_NG = "AISE_NG"
    ASC = "ASC"
    BCI = "BCI"
    BCORP = "BCORP"
    BE = "BE"
    BE_L_CO = "BE_L_CO"
    BE_LE = "BE_LE"
    BE_P = "BE_P"
    BE_T = "BE_T"
    BE_WR = "BE_WR"
    BIO = "BIO"
    BIOLAND = "BIOLAND"
    BIOPARK = "BIOPARK"
    BIORE = "BIORE"
    BK = "BK"
    BK_RF = "BK_RF"
    BLUES_P = "BLUES_P"
    BLUES_A = "BLUES_A"
    BONSUCRO = "BONSUCRO"
    BSCI = "BSCI"
    BVA = "BVA"
    CCCC = "CCCC"
    CCS = "CCS"
    CA_BC = "CA_BC"
    CMIA = "CMIA"
    CNI = "CNI"
    CP = "CP"
    CSE = "CSE"
    CTC_T_BRONZE = "CTC_T_BRONZE"
    CTC_T_SILVER = "CTC_T_SILVER"
    CTC_T_GOLD = "CTC_T_GOLD"
    CTC_T_PLATIN = "CTC_T_PLATIN"
    CTC_WR = "CTC_WR"
    CTFL = "CTFL"
    DEMETER = "DEMETER"
    ECOCERT = "ECOCERT"
    ECOVIN = "ECOVIN"
    ECO_GARANTIE = "ECO_GARANTIE"
    ECO_INSTITUTE = "ECO_INSTITUTE"
    ECO_PP_OEKO_TEX = "ECO_PP_OEKO_TEX"
    ECO_VEG = "ECO_VEG"
    ENERGY_STAR = "ENERGY_STAR"
    EPEAT_MP = "EPEAT_MP"
    EPEAT_L_CO = "EPEAT_L_CO"
    EU_BIO = "EU_BIO"
    EU_ECO_H = "EU_ECO_H"
    EU_ECO_L_CO = "EU_ECO_L_CO"
    EU_ECO_WR = "EU_ECO_WR"
    EU_ECO_P = "EU_ECO_P"
    EU_ECO_T = "EU_ECO_T"
    ETI = "ETI"
    FC = "FC"
    FFL = "FFL"
    FLA = "FLA"
    FNG = "FNG"
    FR = "FR"
    FS = "FS"
    FSC = "FSC"
    FSC_M = "FSC_M"
    FSC_R = "FSC_R"
    FT = "FT"
    FT_B = "FT_B"
    FT_CP = "FT_CP"
    FT_TP = "FT_TP"
    FWF = "FWF"
    G_IT = "G_IT"
    GAEA = "GAEA"
    GCS = "GCS"
    GEPA = "GEPA"
    GGN = "GGN"
    GK = "GK"
    GOTS = "GOTS"
    GOTS_ORGANIC = "GOTS_ORGANIC"
    GOTS_MWOM = "GOTS_MWOM"
    GREEN_BRANDS = "GREEN_BRANDS"
    GRS = "GRS"
    HIGG = "HIGG"
    HIH = "HIH"
    HM_C = "HM_C"
    HVH = "HVH"
    IR = "IR"
    IGEP = "IGEP"
    ISCC = "ISCC"
    IVN_NL = "IVN_NL"
    IVN_NT_BEST = "IVN_NT_BEST"
    LEVEL = "LEVEL"
    KLIMANEUTRAL = "KLIMANEUTRAL"
    LP = "LP"
    LS_OEKO_TEX = "LS_OEKO_TEX"
    LWG = "LWG"
    MSC = "MSC"
    MYCLIMATE = "MYCLIMATE"
    NATUREPLUS = "NATUREPLUS"
    NCP = "NCP"
    NE_WR = "NE_WR"
    NE_L = "NE_L"
    NE_T = "NE_T"
    NL_T = "NL_T"
    NL_L = "NL_L"
    NL_W = "NL_W"
    NLF_L = "NLF_L"
    OCS = "OCS"
    OCS_100 = "OCS_100"
    OCS_BLENDED = "OCS_BLENDED"
    MIG_OEKO_TEX = "MIG_OEKO_TEX"
    OEKOPAPLUS = "OEKOPAPLUS"
    OE_UZ = "OE_UZ"
    OE_UZ_WR = "OE_UZ_WR"
    PEFC = "PEFC"
    PEFC_R = "PEFC_R"
    PEFC_Z = "PEFC_Z"
    PETA = "PETA"
    PP = "PP"
    PROVEG = "PROVEG"
    QUL = "QUL"
    RA = "RA"
    RAL = "RAL"
    RCS_BLENDED = "RCS_BLENDED"
    RCS_100 = "RCS_100"
    RDS = "RDS"
    RSB = "RSB"
    RSPO = "RSPO"
    RWS = "RWS"
    SA8000 = "SA8000"
    S100_OEKO_TEX = "S100_OEKO_TEX"
    SOILA = "SOILA"
    SGS = "SGS"
    STEP_OEKO_TEX = "STEP_OEKO_TEX"
    TCO_N = "TCO_N"
    TCO_S = "TCO_S"
    TUEV_GP_L = "TUEV_GP_L"
    TUEV_GP_S = "TUEV_GP_S"
    UTZ = "UTZ"
    VFI = "VFI"
    VGS = "VGS"
    VEGANBLUME = "VEGANBLUME"
    WFTO = "WFTO"
    WRAP = "WRAP"
    XX_PLUS = "XX_PLUS"
    XX = "XX"


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
