from message_queue import MessageQueue
from redis import Redis
from rq import Connection, Worker

from core.constants import WORKER_QUEUE_EXTRACT, TABLE_NAME_GREEN_DB
from core.redis import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_USER
from database.connection import GreenDB

# TODO: This is a false positive of mypy
from extract import extract_product  # type: ignore

from . import CONNECTION_FOR_TABLE

green_db_connection = GreenDB()
message_queue = MessageQueue()


def start() -> None:
    """
    Starts the `Worker` process that listens on the `extract` queue.
    """
    redis_connection = Redis(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, username=REDIS_USER
    )
    with Connection(redis_connection):
        worker = Worker(WORKER_QUEUE_EXTRACT)
        worker.work(with_scheduler=True)


def extract_and_write_to_green_db(table_name: str, row_id: int) -> None:
    """
    This function gets executed when a new job is available.
    It simply fetches the given `row_id` from the table `table_name`
        and extracts a new `Product` object from its HTML, which is then inserted into the GreenDB.

    Args:
        table_name (str): The table where the `ScrapedPage` should be fetched from
        row_id (int): The id of the to-be-fetched-row
    """
    scraped_page = CONNECTION_FOR_TABLE[table_name].get_scraped_page(id=row_id)

    if product := extract_product(table_name=table_name, scraped_page=scraped_page):
        row = green_db_connection.write(product)
        message_queue.add_extract(table_name=TABLE_NAME_GREEN_DB, row_id=row.id)

    else:
        # TODO: what to do when extract fails? -> "failed" queue?
        pass
