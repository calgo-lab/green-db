import html
from dataclasses import dataclass

import extruct
from bs4 import BeautifulSoup

from core.domain import ScrapedPage


@dataclass
class ParsedPage:
    scraped_page: ScrapedPage
    beautiful_soup: BeautifulSoup
    schema_org: dict


def parse_page(scraped_page: ScrapedPage) -> ParsedPage:
    beautiful_soup = BeautifulSoup(scraped_page.html, "html.parser")
    schema_org = extract_meta_data(scraped_page.html)
    return ParsedPage(
        scraped_page=scraped_page, beautiful_soup=beautiful_soup, schema_org=schema_org
    )


DUBLINCORE = "dublincore"
JSON_LD = "json-ld"
MICRODATA = "microdata"
# MICROFORMAT = "microformat"
# OPENGRAPH = "opengraph"
# RDFA = "rdfa"

_SYNTAXES = [DUBLINCORE, JSON_LD, MICRODATA]


def extract_meta_data(page_html: str) -> dict:
    unescaped_html = html.unescape(page_html)
    meta_data = extruct.extract(unescaped_html, syntaxes=_SYNTAXES)
    return meta_data if meta_data else {}
