import csv
import json
from enum import Enum
from pathlib import Path
from typing import Any

SUSTAINABILITY_LABELS_JSON_FILE_PATH = Path(__file__).parent / "sustainability-labels.json"
SUSTAINABILITY_LABELS_EVALUATION_CSV_FILE_PATH = (
    Path(__file__).parent / "sustainability-labels-evaluation.csv"
)
SPECIAL_LABELS_JSON_FILE_PATH = Path(__file__).parent / "special-labels.json"


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


def _load_csv_file(file_path: Path) -> list:
    """
    Loads the given file at `file_path`.

    Args:
        file_path (Path): path of CSV file to load.

    Returns:
        dict: `dict` representation of `file_path`.
    """
    with open(file_path) as file:
        return list(csv.DictReader(file, delimiter=","))


def load_and_get_sustainability_labels() -> dict:
    """
    Loads all sustainability JSON files and combines them.

    Returns:
        dict: All available sustainability labels.
    """
    # load JSON files
    certificates = _load_json_file(SUSTAINABILITY_LABELS_JSON_FILE_PATH)
    certificate_evaluations = _load_csv_file(SUSTAINABILITY_LABELS_EVALUATION_CSV_FILE_PATH)
    special_labels = _load_json_file(SPECIAL_LABELS_JSON_FILE_PATH)

    for certificate in certificates:
        for evaluation in certificate_evaluations:
            evaluation = {k.replace(":", "_"): v for k, v in evaluation.items()}
            if certificate == evaluation["id"]:
                certificates[certificate].update(evaluation)

    # add special labels
    certificates.update(special_labels)

    return certificates


def create_CertificateType() -> Any:
    """
    Factory function to construct the `Enum` that contains the sustainable certificates

    Returns:
        Any: `CertificateType` `Enum` use for the domain.
    """

    certificates = load_and_get_sustainability_labels()

    _certificate_prefix = "certificate:"
    _certificate_2_id = {
        certificate.replace(_certificate_prefix, ""): certificate
        for certificate in certificates.keys()
    }

    class CertificateHelper(Enum):
        """
        We use the `Enum` Functional API: https://docs.python.org/3/library/enum.html#functional-api
        to construct an Enum based on the sustainability certificates. For this, we need to
        implement `_generate_next_value_`, however, this class is not used any further.
        """

        def _generate_next_value_(name: str, start, count, last_values):  # type: ignore
            return _certificate_2_id[name]

    return CertificateHelper(  # type: ignore
        value="CertificateType",
        names=list(_certificate_2_id.keys()),
        module="core.domain",
        type=str,
    )
