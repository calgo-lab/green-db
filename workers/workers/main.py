from argparse import ArgumentParser

from workers.extract import run as run_extract
from workers.scraping import run as run_scraping

if __name__ == "__main__":
    parser = ArgumentParser(description="CLI to start a RQ-Worker process.")
    subparsers = parser.add_subparsers()

    # scraping
    scraping_parser = subparsers.add_parser("scraping")
    scraping_parser.set_defaults(command_function=run_scraping)

    # extract
    extract_parser = subparsers.add_parser("extract")
    extract_parser.set_defaults(command_function=run_extract)

    args = parser.parse_args()
    args.command_function(
        # call given command function with parameters
        **{
            parameter: value
            for parameter, value in vars(args).items()
            if parameter != "command_function"
        }
    )
