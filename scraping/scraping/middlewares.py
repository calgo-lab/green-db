from logging import getLogger
from random import random
from time import monotonic
from typing import Any

from twisted.internet import reactor
from twisted.internet.defer import Deferred

logger = getLogger(__name__)

amazon_request_counter = 0
amazon_end_of_break_time = 0.0


class AmazonSchedulerMiddleware(object):
    def process_request(self, request: Any, spider: Any) -> Any:
        global amazon_request_counter, amazon_end_of_break_time
        amazon_request_counter += 1
        current_time = monotonic()
        if amazon_request_counter >= 250:
            amazon_end_of_break_time = current_time + 60**2 * 12 * (random() + 0.5)
            amazon_request_counter = 0
        if current_time < amazon_end_of_break_time:
            delay = amazon_end_of_break_time - current_time
            logger.info(f"Delaying {request} by {delay} seconds")
            d: Any = Deferred()
            reactor.callLater(delay, d.callback, None)  # type: ignore[attr-defined]
            return d
