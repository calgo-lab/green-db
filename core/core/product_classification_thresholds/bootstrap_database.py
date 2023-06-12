import json
from datetime import datetime
from pathlib import Path

from core.constants import PRODUCT_CLASSIFICATION_MODEL

from ..domain import ProductClassificationThreshold

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
        timestamp=datetime(2023, 6, 12),  # NOTE: Change me after updating thresholds
        source=source,
        merchant=merchant,
        predicted_category=category,
        threshold=threshold,
    )
    for source, merchants in _load_json_file(THRESHOLDS_JSON_FILE_PATH).items()
    for merchant, values in merchants.items()
    for category, threshold in values.items()
]
