from redis import Redis
from rq import Connection, Worker

from core.constants import (
    TABLE_NAME_SCRAPING_OTTO,
    TABLE_NAME_SCRAPING_ZALANDO,
    WORKER_QUEUE_EXTRACT,
)
from core.redis import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_USER
from database.connection import GreenDB, Scraping

green_db_connection = GreenDB()
CONNECTION_FOR_TABLE = {
    TABLE_NAME_SCRAPING_ZALANDO: Scraping(TABLE_NAME_SCRAPING_ZALANDO),
    TABLE_NAME_SCRAPING_OTTO: Scraping(TABLE_NAME_SCRAPING_OTTO),
}


def start() -> None:
    redis_connection = Redis(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, username=REDIS_USER
    )
    with Connection(redis_connection):
        worker = Worker(WORKER_QUEUE_EXTRACT)
        worker.work(with_scheduler=True)


def extract_and_write_to_green_db(table_name: str, row_id: int) -> None:
    scraped_page = CONNECTION_FOR_TABLE[table_name].get_scraped_page(row_id)

    # TODO: what to do when scraping fails? -> "failed" queue?
