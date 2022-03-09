# How to add new shops?


If you want to add another to-be-scraped-shop, unfortunately, there are some files that need to be changed for this. Those are listed and shortly described in the following:

1. [`core.core.constants.py`](../core/core/constants.py):
   - define another `TABLE_NAME_SCRAPING_<shop-name>` constant to create the single source of truth for the actual table name.
2. [`database.database.tables.py`](../database/database/tables.py):
   - since the necessary logic is inherited from base-classes, it's enough but still necessary to create the class: `<shop-name>ScrapingTable`. (There are examples of existing shops)
   - add the defined class to the mapping: `SCRAPING_TABLE_CLASS_FOR`
3. [`scraping.scraping.spiders.<shop-name>.py`](../scraping/scraping/spiders):
   - create a new file `<shop-name>.py`. (Check out others for examples)
   - the most of its functionality is inherited from the [`BaseSpider`](../scraping/scraping/spiders/_base.py) implementation.
   - you need to implement `parse_SERP`. It yields `SplashRequest`'s for each product URL and `parse_PRODUCT` (from base-class) as callback.
   - further, it yields `SplashRequest` with the next SERP URL (pagination) and `parse_SERP` as callback.
4. [`extract.extract.extractors.<shop-name>.py`](../extract/extract/__init__.py):
   - create a new file `<shop-name>.py`. (Check out others for examples)
   - import the Extractor decorator: `from ..utils import Extractor`
     - [`extract_product`](../extract/extract/__init__.py) uses to map a given `TABLE_NAME_SCRAPING_*` to an extractor
   - implement a function with signature: `@Extractor(TABLE_NAME_SCRAPING_<shop-name>) def extract(parsed_page: ParsedPage) -> Optional[Product]:`
     - it's responsible for parsing the HTML
     - find and extract necessary product attributes
     - find and extract necessary sustainability information
     - return `Product` object or `None`
   - add the dictionary `EXTRACTOR_FOR_TABLE_NAME = {TABLE_NAME_SCRAPING_<shop-name>: extract}`
