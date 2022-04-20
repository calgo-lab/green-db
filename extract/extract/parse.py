import html
from dataclasses import dataclass

import extruct
from bs4 import BeautifulSoup

from core.domain import ScrapedPage


@dataclass
class ParsedPage:
    """
    Helper representation that bundles the original domain object `ScrapedPage`,
    the parsed HTML of it, and the extracted schema.org information.
    """

    scraped_page: ScrapedPage
    beautiful_soup: BeautifulSoup
    schema_org: dict


def parse_page(scraped_page: ScrapedPage) -> ParsedPage:
    """
    Parses the given `scraped_page` and extract its schema.org information.

    Args:
        scraped_page (ScrapedPage): Domain object `ScrapedPage`

    Returns:
        ParsedPage: Representation that bundles the `scraped_page` with intermediate representations
    """
    beautiful_soup = BeautifulSoup(scraped_page.html, "html.parser")
    schema_org = extract_schema_org(scraped_page.html)
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


def extract_schema_org(page_html: str) -> dict:
    """
    Extract schema.org information form `page_html`.

    Args:
        page_html (str): HTML of the page

    Returns:
        dict: Schema.org information found in `page_html`
    """
    unescaped_html = html.unescape(page_html)
    schema_org = extruct.extract(unescaped_html, syntaxes=_SYNTAXES, errors="ignore")
    return schema_org if schema_org else {}
