from typing import Union, Iterator

import pandas as pd


def to_df(objects: Union[list, Iterator]) -> pd.DataFrame:
    """Converts a list or iterator to a df.

    :param objects: A list of objects to be converted to a df.
    :return:
        A dataframe from the `objects`.
    """
    return pd.DataFrame([obj.__dict__ for obj in objects])
