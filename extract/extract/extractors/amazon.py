import json
import re
from logging import getLogger
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product
from ..parse import ParsedPage
from ..utils import safely_return_first_element

logger = getLogger(__name__)

def extract_amazon(parsed_page: ParsedPage) -> Optional[Product]:
    microdata = parsed_page.schema_org.get(MICRODATA, [{}])
    print(microdata)
    # HTML object:
    #name = response.css('#productTitle::text').getall()
    #description = response.css('#productDescription span::text').getall()
    #brand = response.css('li:nth-child(3) .a-text-bold+ span::text').getall()
    #sustainability_labels = response.css('[id*=Certificate-Name] span::text').getall()
    # TODO Review cases with more than one certificate
    #price = response.css('.apexPriceToPay span::text').getall()
    # TODO How to solve range of prices?
    #currency =
    #image_urls =
    #color = response.css('img.imgSwatch::attr(alt)').getall()
    #size = response.css('[id*=native_size_name]::text').getall()
    #asin
    #category = response.css('a.a-link-normal.a-color-tertiary::text').getall()
