from argparse import ArgumentParser

from workers.extract import start as start_extract
from workers.scraping import start as start_scraping


def start() -> None:
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
