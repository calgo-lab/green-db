from logging import getLogger

from redis import Redis
from rq import Queue, Retry

from core import log
from core.constants import (
    WORKER_FUNCTION_EXTRACT,
    WORKER_FUNCTION_SCRAPING,
    WORKER_FUNCTION_INFERENCE,
    WORKER_QUEUE_EXTRACT,
    WORKER_QUEUE_SCRAPING,
    WORKER_QUEUE_INFERENCE, TABLE_NAME_GREEN_DB
)
from core.domain import ScrapedPage
from core.redis import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_USER

log.setup_logger(__name__)
logger = getLogger(__name__)


class MessageQueue:
    def __init__(self) -> None:
        """
        This `class` is for convenience and to avoid duplicated implementations of the same thing.
        It offers simple access to enqueue jobs.
        """
        self.__redis_connection = Redis(
            host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, username=REDIS_USER
        )

        self.__scraping_queue = Queue(WORKER_QUEUE_SCRAPING, connection=self.__redis_connection)
        self.__extract_queue = Queue(WORKER_QUEUE_EXTRACT, connection=self.__redis_connection)
        self.__inference_queue = Queue(WORKER_QUEUE_INFERENCE, connection=self.__inference_queue)

        logger.info("Redis connection established and message queues initialized.")

    def add_scraping(self, table_name: str, scraped_page: ScrapedPage) -> None:
        """
        Enqueue job to "scraping" `Queue`.

        Args:
            table_name (str): Table name to insert the given `scraped_page`
            scraped_page (ScrapedPage): Domain object representation to add to scraping table
        """
        self.__scraping_queue.enqueue(
            WORKER_FUNCTION_SCRAPING,
            args=(table_name, scraped_page),
            job_timeout=10,
            result_ttl=1,
            retry=Retry(max=5, interval=30),
        )

    def add_extract(self, table_name: str, row_id: int) -> None:
        """
        Enqueue job to "extract" `Queue`.

        Args:
            table_name (str): Table name to fetch the `ScrapedPage` from
            row_id (int): id of the to-be-extracted-row
        """
        self.__extract_queue.enqueue(
            WORKER_FUNCTION_EXTRACT,
            args=(table_name, row_id),
            job_timeout=10,
            result_ttl=1,
            retry=Retry(max=5, interval=30),
        )

    def add_inference(self, row_id: int) -> None:
        """
        Enqueue job to "inference" `Queue`.

        Args:
            row_id (int): id of the row used for inference
        """
        self.__extract_queue.enqueue(
            WORKER_FUNCTION_INFERENCE,
            args=row_id,
            job_timeout=10,
            result_ttl=1,
            retry=Retry(max=5, interval=30),
        )

