from core import log
from core.constants import (
    TABLE_NAME_SCRAPING_AMAZON_DE,
    TABLE_NAME_SCRAPING_AMAZON_FR,
    TABLE_NAME_SCRAPING_ASOS_FR,
    TABLE_NAME_SCRAPING_HM_FR,
    TABLE_NAME_SCRAPING_OTTO_DE,
    TABLE_NAME_SCRAPING_ZALANDO_DE,
    TABLE_NAME_SCRAPING_ZALANDO_FR,
    TABLE_NAME_SCRAPING_ZALANDO_UK,
)
from database.connection import Scraping

log.setup_logger(__name__)

CONNECTION_FOR_TABLE = {
<<<<<<< HEAD
    TABLE_NAME_SCRAPING_AMAZON_DE: Scraping(TABLE_NAME_SCRAPING_AMAZON_DE),
    TABLE_NAME_SCRAPING_ASOS_FR: Scraping(TABLE_NAME_SCRAPING_ASOS_FR),
    TABLE_NAME_SCRAPING_OTTO_DE: Scraping(TABLE_NAME_SCRAPING_OTTO_DE),
=======
    TABLE_NAME_SCRAPING_AMAZON: Scraping(TABLE_NAME_SCRAPING_AMAZON),
    TABLE_NAME_SCRAPING_AMAZON_FR: Scraping(TABLE_NAME_SCRAPING_AMAZON_FR),
    TABLE_NAME_SCRAPING_ASOS: Scraping(TABLE_NAME_SCRAPING_ASOS),
    TABLE_NAME_SCRAPING_OTTO: Scraping(TABLE_NAME_SCRAPING_OTTO),
>>>>>>> main
    TABLE_NAME_SCRAPING_ZALANDO_DE: Scraping(TABLE_NAME_SCRAPING_ZALANDO_DE),
    TABLE_NAME_SCRAPING_ZALANDO_FR: Scraping(TABLE_NAME_SCRAPING_ZALANDO_FR),
    TABLE_NAME_SCRAPING_ZALANDO_UK: Scraping(TABLE_NAME_SCRAPING_ZALANDO_UK),
    TABLE_NAME_SCRAPING_HM: Scraping(TABLE_NAME_SCRAPING_HM),
}
