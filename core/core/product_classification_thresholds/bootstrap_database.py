import json
from datetime import datetime
from pathlib import Path

from ..domain import ProductClassificationThreshold
from core.constants import PRODUCT_CLASSIFICATION_MODEL

THRESHOLDS_JSON_FILE_PATH = Path(__file__).parent / "thresholds.json"


def _load_json_file(file_path: Path) -> dict:
    """
    Loads the given file at `file_path`.

    Args:
        file_path (Path): path of JSON file to load.

    Returns:
        dict: `dict` representation of `file_path`.
    """
    with open(file_path, "r") as file:
        return json.load(file)


thresholds = [
    ProductClassificationThreshold(
        ml_model_name=PRODUCT_CLASSIFICATION_MODEL,
        timestamp=datetime(2023, 4, 28),  # NOTE: Change me after updating thresholds
        category=category,
        threshold=threshold)
    for category, threshold in _load_json_file(THRESHOLDS_JSON_FILE_PATH).items()
]


