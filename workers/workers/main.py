from argparse import ArgumentParser


def start_extract() -> None:
    """
    This indirection is necessary to "lazy" load the `extract` module.
    """
    from .extract import start

    start()


def start_scraping() -> None:
    """
    This indirection is necessary to "lazy" load the `scraping` module.
    """
    from .scraping import start

    start()


def start() -> None:
    """
    CLI implementation of the `worker` command.
    """
    parser = ArgumentParser(description="CLI to start a RQ-Worker process.")
    subparsers = parser.add_subparsers()

    # scraping
    scraping_parser = subparsers.add_parser("scraping")
    scraping_parser.set_defaults(command_function=start_scraping)

    # extract
    extract_parser = subparsers.add_parser("extract")
    extract_parser.set_defaults(command_function=start_extract)

    args = parser.parse_args()
    args.command_function(
        # call given command function with parameters
        **{
            parameter: value
            for parameter, value in vars(args).items()
            if parameter != "command_function"
        }
    )
