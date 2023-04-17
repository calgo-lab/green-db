from message_queue import MessageQueue
from redis import Redis
from rq import Connection, Worker

from core.constants import WORKER_QUEUE_SCRAPING, ALL_SCRAPING_TABLE_NAMES
from core.domain import PageType, ScrapedPage
from core.redis import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_USER
from database.connection import Scraping

CONNECTION_FOR_TABLE = {name: Scraping(name) for name in ALL_SCRAPING_TABLE_NAMES}


redis_connection = Redis(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, username=REDIS_USER
)

message_queue = MessageQueue()


def start() -> None:
    """
    Starts the `Worker` process that listens on the `scraping` queue.
    """
    with Connection(redis_connection):
        worker = Worker(WORKER_QUEUE_SCRAPING)
        worker.work(with_scheduler=True)


def write_to_scraping_database(table_name: str, scraped_page: ScrapedPage) -> None:
    """
    This function gets executed when a new job is available.
    It simply inserts the `scraped_page` into the table `table_name`.

    Args:
        table_name (str): The table the `scraped_page` should be inserted into
        scraped_page (ScrapedPage): Tht actual domain object to insert into `table_name`
    """
    row = CONNECTION_FOR_TABLE[table_name].write(scraped_page)

    if scraped_page.page_type == PageType.PRODUCT.value:
        message_queue.add_extract(table_name=table_name, row_id=row.id)
