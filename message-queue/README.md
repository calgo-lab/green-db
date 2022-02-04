# `message-queue` Package

The `message-queue` package implements a single class that connects to Redis and offers a simple API to enqueue jobs. We use [`Redis Queue`](https://python-rq.org) for this functionality, since it is simple but powerful.