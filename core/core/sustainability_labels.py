import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, conint

SUSTAINABILITY_LABELS_DATA_DIR = Path(__file__).parent / "sustainability_labels_data"
certificate_prefix = "certificate:"

# Add special labels (not included in JSON) manually
special_labels = {
    f"{certificate_prefix}OTHER": {
        "languages": {
            "de": {
                "name": "OTHER",
                "description": "Dieses 'Label' ist GreenDB intern. Es wird verwendet, wenn ein Shop das Produkt als nachhaltig listet, unsere Nachhlatigkeitsexpert*innen dies aber nicht nachvollziehen können. Es handelt sich also um falsche oder nicht belastbare Informationen",  # noqa
            }
        }
    },
    f"{certificate_prefix}UNKNOWN": {
        "languages": {
            "de": {
                "name": "UNKNOWN",
                "description": "Dieses 'Label' ist GreenDB intern. Es wird verwendet, wenn die Angaben des Shops von uns (noch) nicht überprüft wurden.",  # noqa
            }
        }
    },
}

# Load JSON files with certificate_information and certificate_evaluation
with open(SUSTAINABILITY_LABELS_DATA_DIR / "sustainability-labels.json") as certificates_file:
    certificate_information = json.load(certificates_file)

with open(
    SUSTAINABILITY_LABELS_DATA_DIR / "sustainability_labels_evaluation.json"
) as evaluations_file:
    certificate_evaluation = json.load(evaluations_file)

# Combine the two JSON files
# by adding the sustainability evaluation information to the corresponding certificate
for certificate, evaluation in certificate_evaluation.items():
    certificate_information[certificate].update(evaluation)

certificate_information.update(special_labels)

# Create a mapping from the full certificate name to its id without the certificate_tag
_certificate_2_id = {
    certificate.replace(certificate_prefix, ""): certificate
    for certificate in certificate_information.keys()
}


class _Certificate(str, Enum):
    """
    We use the `Enum` Functional API: https://docs.python.org/3/library/enum.html#functional-api
    to construct an Enum based on the sustainable certificates.
    This class defines the necessary function to create custom values, here the certificate IDs
    """

    def _generate_next_value_(name: str, start, count, last_values):  # type: ignore
        return _certificate_2_id[name]


def get_certificate_class() -> Type[Enum]:
    """
    Factory function to construct the `Enum` that contains the sustainable certificates
    Returns:
        Type[Enum]: `CertificateType` `Enum` use for the domain.
    """
    return _Certificate(  # type: ignore
        value="CertificateType",
        names=list(_certificate_2_id.keys()),
        module=__name__,
    )




def _get_certificate_attribute(
    certificate_information_dict: Dict[str, Dict[str, Any]],
    attribute: str,
    language_preference: List[str] = ["de", "en", "fr"],
) -> str:
    """
    Helper function to retrieve an attribute of a certificate_information_dict in one language.
    Args:
        certificate_information_dict (Dict[str, Dict[str, Any]]): Dictionary that holds the
            sustainability label information.
        attribute (str): `attribute` to get.
        language_preference (List[str], optional): Order of language priorities.
            Defaults to ["de", "en", "fr"].

    Returns:
       str: of the corresponding attribute in one language.
    """
    for language in language_preference:
        if language in certificate_information_dict["languages"].keys():
            return certificate_information_dict["languages"][language][attribute]
    return ""


# Create a list of SustainabilityLabel with its information in one language
certificate_information_dense = [
    SustainabilityLabel(
        id=certificate_id,
        timestamp=datetime(2022, 3, 3, 19),  # NOTE: Change me after updating sustainability labels
        name=_get_certificate_attribute(certificate_information_dict, "name"),
        description=_get_certificate_attribute(certificate_information_dict, "description"),
        ecological_evaluation=certificate_information_dict.get("ecological_evaluation", None),
        social_evaluation=certificate_information_dict.get("social_evaluation", None),
        credibility_evaluation=certificate_information_dict.get("social_evaluation", None),
    )
    for certificate_id, certificate_information_dict in certificate_information.items()
]
