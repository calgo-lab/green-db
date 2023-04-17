import json

import requests

from redis import Redis
from rq import Connection, Worker

from core.constants import WORKER_QUEUE_INFERENCE
from core.domain import Product, ProductClassification
from core.redis import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_USER
from database.connection import GreenDB

# TODO: This is a false positive of mypy
from inference import infer_product_category  # type: ignore

green_db_connection = GreenDB()


def start() -> None:
    """
    Starts the `Worker` process that listens on the `extract` queue.
    """
    redis_connection = Redis(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, username=REDIS_USER
    )
    with Connection(redis_connection):
        worker = Worker(WORKER_QUEUE_INFERENCE)
        worker.work(with_scheduler=True)


def inference_and_write_to_green_db(row_id: int) -> None:
    """
    This function gets executed when a new job is available.
    It simply fetches the given `row_id` from the table `table_name`
        and performs inference, which result is then inserted into the GreenDB.

    Args:
        row_id (int): The id of the to-be-fetched-row
    """
    product = green_db_connection.get_product(id=row_id)
    product_classification = infer_product_category(product=product, row_id=row_id)
    green_db_connection.write(product_classification)


def infer_product_category(product: Product, row_id: int) -> ProductClassification:
    json_post = json.dumps({str(row_id): product.__dict__})
    r = requests.post("http://product-classification:8080", json_post)
    return ProductClassification.parse_obj(eval(r.text)[0])
