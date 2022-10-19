from core import log
from core.constants import ALL_SCRAPING_TABLE_NAMES
from database.connection import Scraping

log.setup_logger(__name__)

CONNECTION_FOR_TABLE = {name: Scraping(name) for name in ALL_SCRAPING_TABLE_NAMES}
