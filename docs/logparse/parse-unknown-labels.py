import argparse
import json
import re

import pandas as pd

shop_regex = re.compile("(?<=INFO - extract.utils: unknown sustainability label from ).*(?=:)")


def parse_args():
    argparser = argparse.ArgumentParser(description="process arguments")
    argparser.add_argument("-f", "--file", type=str, help="Absolute path to logfile to parse.")
    return argparser.parse_args()


def main():
    args = parse_args()
    infile = args.file
    print(f"Parsing {infile}")

    with open(infile, encoding="utf-8") as f:
        f = f.readlines()

    shop_labels = []

    for line in f:
        if shop := shop_regex.findall(line):
            shop = shop[0]
            unknown_label = re.findall(f"(?<={shop}: ).*", line)
            shop_labels.append((shop, unknown_label[0]))

    df = pd.DataFrame(shop_labels, columns=["shop", "label"])
    df_stats = pd.DataFrame(df.value_counts()).sort_values(by=["shop", 0], ascending=[False, False])
    summary = (
        df_stats.reset_index()
        .groupby("shop", as_index=False)
        .agg({"shop": "first", "label": lambda x: sorted(list(x))})
        .to_json(orient="records")
    )
    parsed = json.loads(summary)

    outfile = f"{infile.rsplit('.')[0]}-unknown-labels.json"
    print(f"Writing results to: {outfile}")

    with open(outfile, "w", encoding="utf-8") as o:
        o.write(json.dumps(parsed, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
