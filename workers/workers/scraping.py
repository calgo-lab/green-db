from core.constants import (
    RQ_QUEUE_EXTRACT,
    RQ_QUEUE_SCRAPING,
    TABLE_NAME_SCRAPING_OTTO,
    TABLE_NAME_SCRAPING_ZALANDO,
)
from database.connection import Scraping
from database.domain import ScrapedPage
from redis import Redis
from rq import Connection, Queue, Retry, Worker

from .config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_USER

CONNECTION_FOR_TABLE = {
    TABLE_NAME_SCRAPING_ZALANDO: Scraping(TABLE_NAME_SCRAPING_ZALANDO),
    TABLE_NAME_SCRAPING_OTTO: Scraping(TABLE_NAME_SCRAPING_OTTO),
}

redis_connection = Redis(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, username=REDIS_USER
)

extract_queue = Queue(RQ_QUEUE_EXTRACT, connection=redis_connection)


def run() -> None:
    with Connection(redis_connection):
        worker = Worker(RQ_QUEUE_SCRAPING)
        worker.work(with_scheduler=True)


def write_to_scraping_database(table: str, **kwargs) -> None:

    scraped_page = ScrapedPage(**kwargs)
    row = CONNECTION_FOR_TABLE[table].write_scraped_page(scraped_page)

    extract_queue.enqueue(
        "workers.extraction.extract_and_write_to_green_db",
        args=(table, row.id),
        job_timeout=10,
        result_ttl=1,
        retry=Retry(max=5, interval=30),
    )
