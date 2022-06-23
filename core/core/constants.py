WORKER_QUEUE_SCRAPING = "scraping"
WORKER_FUNCTION_SCRAPING = "workers.scraping.write_to_scraping_database"

WORKER_QUEUE_EXTRACT = "extract"
WORKER_FUNCTION_EXTRACT = "workers.extract.extract_and_write_to_green_db"

DATABASE_NAME_SCRAPING = "scraping"

# New table variable and names need to follow the structure:
# TABLE_NAME_SCRAPING_<MERCHANT>_<COUNTRY_CODE> = "<merchant>_<COUNTRY_CODE>"
# where the country code refers to ISO_3166-1
# see: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements

TABLE_NAME_SCRAPING_ZALANDO_DE = "zalando_DE"
TABLE_NAME_SCRAPING_ZALANDO_FR = "zalando_FR"
TABLE_NAME_SCRAPING_ZALANDO_GB = "zalando_GB"
TABLE_NAME_SCRAPING_OTTO_DE = "otto_DE"
TABLE_NAME_SCRAPING_ASOS_FR = "asos_FR"
TABLE_NAME_SCRAPING_HM_FR = "hm_FR"
TABLE_NAME_SCRAPING_AMAZON_DE = "amazon_DE"
TABLE_NAME_SCRAPING_AMAZON_DE = "amazon_DE"
TABLE_NAME_SCRAPING_AMAZON_FR = "amazon_FR"

DATABASE_NAME_GREEN_DB = "green-db"
TABLE_NAME_GREEN_DB = "green-db"
TABLE_NAME_SUSTAINABILITY_LABELS = "sustainability-labels"
