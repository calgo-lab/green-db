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
   - implement a function with signature: `def extract_<shop-name>(parsed_page: ParsedPage) -> Optional[Product]:`
     - it's responsible for parsing the HTML
     - find and extract necessary product attributes
     - find and extract necessary sustainability information
     - return `Product` object or `None`
5. [`extract.extract.__init__.py`](../extract/extract/__init__.py):
   - import the implemented function: `extract_<shop-name>` from the created file: `extract.extract.extractors.<shop-name>.py`
   - add the function to the mapping: `EXTRACTOR_FOR_TABLE_NAME`
6. [`workers.workers.__init__.py`](../workers/workers/__init__.py):
   - add connection for `<shop-name>` to the mapping `CONNECTION_FOR_TABLE`
7. [`start-job.scripts.<shop-name>.py`](../start-job/scripts/):
   - create a new file `<shop-name>.py`. (Check out others for examples)
   - implement a function with signature: `def get_settings() -> List[Dict[str, str]]:`
   - each dict corresponds to one scrapy job. they should have these entries:
     - `'start_urls'` usually a single url pointing to a SERP.
     - `'category'` product category string (eg. `'SHIRT'`, `'SHOES'`, ...)
     - `'meta_data'` json formatted string containing additional product information.
       - `family` product family (eg. `'FASHION'`)
       - `sex` gender (eg. `'MALE'`, `'FEMALE'`, ...)
8. [`start-job.scripts.main.py`](../start-job/scripts/main.py):
   - import your `get_settings` and add it to `SETTINGS`.

your done. good job :)
