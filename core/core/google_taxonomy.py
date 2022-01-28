from enum import Enum
from logging import getLogger
from typing import Type
from urllib import request

URL_TAXONOMY_W_IDS = "https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt"

logger = getLogger(__name__)

with request.urlopen(URL_TAXONOMY_W_IDS) as response:
    lines = response.read().decode("utf-8").splitlines()

_version_from = lines[0].split(": ")[-1]
_taxonomy_lines = lines[1:]

logger.info(f"Version of the Google Taxonomy from: {_version_from}")


_id_2_name = {
    int(id): category_string.split(" > ")[-1]
    .upper()
    .replace(",", "")
    .replace(" ", "_")
    .replace("_&_", "_AND_")
    for id, category_string in [taxonomy_line.split(" - ") for taxonomy_line in _taxonomy_lines]
}
_name_2_id = {value: key for key, value in _id_2_name.items()}


class _CategoryTypeBase(int, Enum):
    def _generate_next_value_(name: str, start, count, last_values):  # type: ignore
        return _name_2_id[name]


def get_taxonomy_enum() -> Type[Enum]:
    return _CategoryTypeBase(  # type: ignore
        value="CategoryType",
        names=list(_name_2_id.keys()),
        module=__name__,
    )
