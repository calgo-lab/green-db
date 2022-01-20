from core.constants import (
    TABLE_NAME_SCRAPING_OTTO,
    TABLE_NAME_SCRAPING_ZALANDO,
    WORKER_QUEUE_SCRAPING,
)
from core.domain import ScrapedPage
from core.redis import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_USER
from database.connection import Scraping
from message_queue import MessageQueue
from redis import Redis
from rq import Connection, Worker

CONNECTION_FOR_TABLE = {
    TABLE_NAME_SCRAPING_ZALANDO: Scraping(TABLE_NAME_SCRAPING_ZALANDO),
    TABLE_NAME_SCRAPING_OTTO: Scraping(TABLE_NAME_SCRAPING_OTTO),
}

redis_connection = Redis(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, username=REDIS_USER
)

message_queue = MessageQueue()


def run() -> None:
    with Connection(redis_connection):
        worker = Worker(WORKER_QUEUE_SCRAPING)
        worker.work(with_scheduler=True)


def write_to_scraping_database(table_name: str, scraped_page: ScrapedPage) -> None:

    row = CONNECTION_FOR_TABLE[table_name].write_scraped_page(scraped_page)

    message_queue.add_extract(table_name=table_name, row_id=row.id)
