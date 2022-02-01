# `core` Package

The `core` package offers some often used functionalities or constants:
- [`constants`](./core/constants.py) used for configuration
- [`domain`](./core/domain.py) implementation uses [`pydantic`](https://pydantic-docs.helpmanual.io) to validate the data
- [`log`](./core/log.py) setup
- database configurations for
  - [`postgres`](./core/postgres.py) and
  - [`redis`](./core/redis.py)