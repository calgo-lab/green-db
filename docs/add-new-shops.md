# How to add new shops?


If you want to add another to-be-scraped-shop, there are some files that need to be changed for this. Those are listed and shortly described in the following:

1. [`core.core.constants.py`](../core/core/constants.py):
   - define another `TABLE_NAME_SCRAPING_<shop-name>_<country>` constant to create the single source of truth for the actual table name.
   - add the new table name to ALL_SCRAPING_TABLE_NAMES.
   - `<country>` needs to be in [ISO_3166-1](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements) format.
2. [`database.database.tables.py`](../database/database/tables.py):
   - since the necessary logic is inherited from base-classes, it's enough but still necessary to create the class: `<shop-name><country>ScrapingTable`. (There are examples of existing shops)
   - add the defined class to the mapping: `SCRAPING_TABLE_CLASS_FOR`
3. [`scraping.scraping.spiders.<shop-name>_<country>.py`](../scraping/scraping/spiders):
   - create a new file `<shop-name>_<country>.py`. (Check out others for examples)
   - the most of its functionality is inherited from the [`BaseSpider`](../scraping/scraping/spiders/_base.py) implementation.
   - set the spiders `name` to `TABLE_NAME_SCRAPING_<shop-name>_<country>`.
   - set the spiders `source`, most often it will be equal to `TABLE_NAME_SCRAPING_<shop-name>_<country>` without `<country>` information. 
   - you need to implement `parse_SERP`. It yields `SplashRequest`'s for each product URL and `parse_PRODUCT` (from base-class) as callback.
   - further, it yields `SplashRequest` with the next SERP URL (pagination) and `parse_SERP` as callback.
   - You need to set `meta` of each yielding request (SERP & PRODUCT) by using `create_default_request_meta(response)` from `BaseSpider`. This sets the meta information like category and gender for each request.
4. [`extract.extract.extractors.<shop-name>_<country>.py`](../extract/extract/__init__.py):
   - create a new file `<shop-name>_<country>.py`. (Check out others for examples)
   - implement a function with signature: `def extract_<shop-name>_<country>(parsed_page: ParsedPage) -> Optional[Product]:`
     - it's responsible for parsing the HTML
     - find and extract necessary product attributes
     - find and extract necessary sustainability information
     - return `Product` object or `None`
5. [`extract.extract.__init__.py`](../extract/extract/__init__.py):
   - import the implemented function: `extract_<shop-name>_<country>` from the created file: `extract.extract.extractors.<shop-name>_<country>.py`
   - add the function to the mapping: `EXTRACTOR_FOR_TABLE_NAME`
6. [`scraping.start_scripts.<shop-name>_<country>.py`](../scraping/scraping/start_scripts):
   - create a new file `<shop-name>_<country>.py`. (Check out others for examples)
   - implement a function with signature: `def get_settings() -> List[dict]:`
   - each dict corresponds to one product category. They should have these entries:
     - `'start_urls'` usually a single url pointing to a SERP.
     - `'category'` product category string (eg. `'SHIRT'`, `'SHOES'`, ...)
     - `'gender'` (Optional) product gender group (eg. `'MALE'`, `'FEMALE'`, `'UNISEX'`)
     - `'consumer_lifestage'` (Optional) product age group (eg. `'ADULT'`, `'ALL_AGES'`, ...)
     - `'meta_data'` (Optional) json string containing additional product information.
       - `family` product family (eg. `'FASHION'`)
7. [`scraping.scraping.spiders._base.py`](../scraping/scraping/spiders/_base.py)
   - import the implemented function `get_settings` from the created file `scraping.start_scripts.<shop-name>.py` using an alias like this:
   `from ..start_scripts.<shop-name>_<country> import get_settings as get_<shop-name>_<country>_settings`
   - add a mapping of `TABLE_NAME_SCRAPING_<shop-name>_<country>` and the defined alias to the variable `SETTINGS`
8. [`start-job.scripts.main.py`](../start-job/scripts/main.py):
   - add `TABLE_NAME_SCRAPING_<shop-name>_<country>` to the variable `MERCHANTS`

You'r done. Good job :)
