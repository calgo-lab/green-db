from logging import getLogger
from random import choice, random
from time import monotonic
from typing import Any, Optional

from twisted.internet import reactor
from twisted.internet.defer import Deferred

from .utils import get_json_data

logger = getLogger(__name__)
user_agents = get_json_data("user_agents.json")

AMAZON_MAX_REQUESTS_BEFORE_BREAK = 250
AMAZON_MINIMUM_BREAK_TIME = 60**2 * 8  # 8 hours


class AmazonSchedulerMiddleware(object):
    """
    Stop scraping pages for `AMAZON_MINIMUM_BREAK_TIME` to `2*AMAZON_MINIMUM_BREAK_TIME` seconds
    once every `AMAZON_MAX_REQUESTS_BEFORE_BREAK` requests.
    """

    request_counter = 0
    end_of_break_time = 0.0

    def process_request(self, request: Any, spider: Any) -> Optional[Deferred]:
        self.request_counter += 1
        current_time = monotonic()

        if self.request_counter >= AMAZON_MAX_REQUESTS_BEFORE_BREAK:
            # trigger break and reset counter
            self.end_of_break_time = current_time + AMAZON_MINIMUM_BREAK_TIME * (random() + 1)
            self.request_counter = 0

        if current_time < self.end_of_break_time:
            # delay the request until the break ends
            d: Deferred = Deferred()
            delay = self.end_of_break_time - current_time
            reactor.callLater(delay, d.callback, None)  # type: ignore[attr-defined]

            logger.info(f"Delaying {request} by {delay} seconds")
            return d

        return None


class RandomUserAgentMiddleware(object):
    """
    Set a random user-agent on every request.
    """

    def process_request(self, request: Any, spider: Any) -> None:
        request.headers["User-Agent"] = choice(user_agents)["useragent"]
