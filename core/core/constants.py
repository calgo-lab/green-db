WORKER_QUEUE_SCRAPING = "scraping"
WORKER_FUNCTION_SCRAPING = "workers.scraping.write_to_scraping_database"

WORKER_QUEUE_EXTRACT = "extract"
WORKER_FUNCTION_EXTRACT = "workers.extract.extract_and_write_to_green_db"

WORKER_QUEUE_INFERENCE = "inference"
WORKER_FUNCTION_INFERENCE = "workers.inference.inference_and_write_to_green_db"

DATABASE_NAME_SCRAPING = "scraping"

# New table variable and names need to follow the structure:
# TABLE_NAME_SCRAPING_<MERCHANT>_<COUNTRY> = "<merchant>_<COUNTRY>"
# where the country refers to ISO_3166-1
# see: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements

TABLE_NAME_SCRAPING_ZALANDO_DE = "zalando_DE"
TABLE_NAME_SCRAPING_ZALANDO_FR = "zalando_FR"
TABLE_NAME_SCRAPING_ZALANDO_GB = "zalando_GB"
TABLE_NAME_SCRAPING_OTTO_DE = "otto_DE"
TABLE_NAME_SCRAPING_ASOS_FR = "asos_FR"
TABLE_NAME_SCRAPING_HM_FR = "hm_FR"
TABLE_NAME_SCRAPING_AMAZON_DE = "amazon_DE"
TABLE_NAME_SCRAPING_AMAZON_FR = "amazon_FR"
TABLE_NAME_SCRAPING_AMAZON_GB = "amazon_GB"

ALL_SCRAPING_TABLE_NAMES = [
    TABLE_NAME_SCRAPING_ZALANDO_DE,
    TABLE_NAME_SCRAPING_ZALANDO_FR,
    TABLE_NAME_SCRAPING_ZALANDO_GB,
    TABLE_NAME_SCRAPING_OTTO_DE,
    TABLE_NAME_SCRAPING_ASOS_FR,
    TABLE_NAME_SCRAPING_HM_FR,
    TABLE_NAME_SCRAPING_AMAZON_DE,
    TABLE_NAME_SCRAPING_AMAZON_FR,
    TABLE_NAME_SCRAPING_AMAZON_GB,
]

DATABASE_NAME_GREEN_DB = "green-db"
TABLE_NAME_GREEN_DB = "green-db"
TABLE_NAME_SUSTAINABILITY_LABELS = "sustainability-labels"
TABLE_NAME_PRODUCT_CLASSIFICATION = "product-classification"

PRODUCT_CLASSIFICATION_MODEL = "copper-armadillo-279"
