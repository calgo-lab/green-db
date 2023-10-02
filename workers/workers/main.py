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


def start_inference() -> None:
    """
    This indirection is necessary to "lazy" load the `inference` module.
    """
    from .inference import start

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

    # inference
    inference_parser = subparsers.add_parser("inference")
    inference_parser.set_defaults(command_function=start_inference)

    args = parser.parse_args()

    parsed_args = {
        parameter: value
        for parameter, value in vars(args).items()
        if parameter != "command_function"
    }

    args.command_function(
        # call given command function with parameters
        **parsed_args
    )
