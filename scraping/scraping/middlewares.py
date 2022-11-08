from logging import getLogger
from random import choice, random
from time import monotonic
from typing import Any

from twisted.internet import reactor
from twisted.internet.defer import Deferred

from .utils import get_json_data

logger = getLogger(__name__)
user_agents = get_json_data("user_agents.json")


class RandomUserAgentMiddleware(object):
    """set a random user-agent on every request"""

    def process_request(self, request: Any, spider: Any) -> Any:
        request.headers["User-Agent"] = choice(user_agents)["useragent"]


class AmazonSchedulerMiddleware(object):
    """wait a few hours every 250 requests"""

    request_counter = 0
    end_of_break_time = 0.0

    def process_request(self, request: Any, spider: Any) -> Any:
        self.request_counter += 1
        current_time = monotonic()

        if self.request_counter >= 250:
            self.end_of_break_time = current_time + 60**2 * 12 * (random() + 0.5)
            self.request_counter = 0

        if current_time < self.end_of_break_time:
            delay = self.end_of_break_time - current_time
            logger.info(f"Delaying {request} by {delay} seconds")
            d: Deferred = Deferred()

            reactor.callLater(delay, d.callback, None)  # type: ignore[attr-defined]

            return d
