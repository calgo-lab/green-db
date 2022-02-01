# `extract` Package

The `extract` package:
- exposes the function [`extract_product`](./extract/__init__.py) that uses the right extractor for the given `ScrapedPage`
- parses `ScrapedPage`s and uses [`ParsedPage`](./extract/parse.py) objects to bundle multiple intermediate parsed representations, such as:
  - the original `ScrapedPage` to access its HTML
  - a parsed representation of its HTML as a [`BeautifulSoup`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) object
  - the extracted `schema_org` information that is embedded in its HTML
- implements for each scraped webpage/shop/merchant an extractor, see [`extractors`](./extract/extractors)