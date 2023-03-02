import argparse
import json
import re
from argparse import Namespace

import pandas as pd

shop_regex = re.compile("(?<=INFO - extract.utils: unknown sustainability label from ).*(?=:)")


def parse_args() -> Namespace:
    """
    Parses the cmd arguments.

    Returns:
        argparse.ArgumentParser: Object containing the parsed arguments.
    """
    argparser = argparse.ArgumentParser(description="process arguments")
    argparser.add_argument("-f", "--file", type=str, help="Absolute path to logfile to parse.")
    return argparser.parse_args()


def main() -> None:
    """
    Main method to parse an extractor logfile for unknown sustainability labels.
    """
    args = parse_args()
    infile = args.file
    print(f"Parsing {infile}")

    with open(infile, encoding="utf-8") as f:
        file = f.readlines()

    shop_labels = []

    for line in file:
        if shop := shop_regex.findall(line):
            shop = shop[0]
            unknown_label = re.findall(f"(?<={shop}: ).*", line)
            shop_labels.append((shop, unknown_label[0]))

    df = pd.DataFrame(shop_labels, columns=["shop", "label"])
    # create a json with a list of unknown labels per shop
    unknown_labels_per_shop = (
        df.groupby("shop", as_index=False)
        .agg({"shop": "first", "label": lambda x: sorted(set(x))})
        .to_json(orient="records", force_ascii=False)
    )

    outfile = f"{infile.rsplit('.')[0]}-unknown-labels.json"
    print(f"Writing results to: {outfile}")

    with open(outfile, "w", encoding="utf-8") as o:
        o.write(json.dumps(unknown_labels_per_shop, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
