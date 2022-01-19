from core.constants import RQ_QUEUE_EXTRACT, TABLE_NAME_SCRAPING_OTTO, TABLE_NAME_SCRAPING_ZALANDO
from database.connection import GreenDB, Scraping
from redis import Redis
from rq import Connection, Worker

from .config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_USER

green_db_connection = GreenDB()
CONNECTION_FOR_TABLE = {
    TABLE_NAME_SCRAPING_ZALANDO: Scraping(TABLE_NAME_SCRAPING_ZALANDO),
    TABLE_NAME_SCRAPING_OTTO: Scraping(TABLE_NAME_SCRAPING_OTTO),
}

redis_connection = Redis(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, username=REDIS_USER
)


def run() -> None:
    with Connection(redis_connection):
        worker = Worker(RQ_QUEUE_EXTRACT)
        worker.work(with_scheduler=True)


def extract_and_write_to_green_db(table: str, id: int) -> None:
    scraped_page = CONNECTION_FOR_TABLE[table].get_scraped_page(id)

    # TODO: what to do when scraping fails? -> "failed" queue?
