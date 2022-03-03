import json
from datetime import datetime
from enum import Enum
from typing import Type
from pathlib import Path

from core.domain import SustainabilityLabel

SUSTAINABILITY_LABELS_DATA_DIR = Path(__file__).parent / "sustainability_labels_data"
information_from = datetime(2022, 1, 25, 12)
certificate_tag = "certificate:"

# Add special labels (not included in JSON) manually
special_labels = {
    certificate_tag + "OTHER": {
        "languages": {
            "de": {
                "name": "OTHER",
                "description": "Dieses 'Label' ist GreenDB intern. Es wird verwendet, wenn ein Shop das Produkt als nachhaltig listet, unsere Nachhlatigkeitsexpert*innen dies aber nicht nachvollziehen können. Es handelt sich also um falsche oder nicht belastbare Informationen",
                # noqa
            }
        }
    },
    certificate_tag + "UNKNOWN": {
        "languages": {
            "de": {
                "name": "UNKNOWN",
                "description": "Dieses 'Label' ist GreenDB intern. Es wird verwendet, wenn die Angaben des Shops von uns (noch) nicht überprüft wurden.",
                # noqa
            }
        }
    }
}

# Load JSON files with certificate_information and certificate_evaluation
with open(SUSTAINABILITY_LABELS_DATA_DIR / "sustainability-labels.json") as labels_file:
    certificate_information = json.load(labels_file)

with open(SUSTAINABILITY_LABELS_DATA_DIR / "sustainability_labels_evaluation.json") as evaluation_file:
    certificate_evaluation = json.load(evaluation_file)

# Combine the two JSON files
# by adding the sustainability evaluation information to the corresponding certificate
for certificate, evaluation in certificate_evaluation.items():
    certificate_information[certificate].update(evaluation)

# Create a mapping from the full certificate name to its id without the certificate_tag
certificate_information.update(special_labels)
_certificate_2_id = {certificate.replace(certificate_tag, ""): certificate
                     for certificate in certificate_information.keys()}


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


def get_certificate_attribute(certificate_information_dict, attribute, language_preference=["de", "en", "fr"]) -> str:
    """
    Helper function to retrieve an attribute of a certificate_information_dict in one language.
    The language_preference is by default ["de", "en", "fr"].
    """
    for language in language_preference:
        if language in certificate_information_dict["languages"].keys():
            return certificate_information_dict["languages"][language][attribute]


# Create a list of SustainabilityLabels with its information in one language
certificate_information_dense = [
    SustainabilityLabel(
        id=certificate_id,
        timestamp=information_from,
        name=get_certificate_attribute(certificate_information_dict, "name"),
        description=get_certificate_attribute(certificate_information_dict, "description"),
        ecological_evaluation=certificate_information_dict.get("ecological_evaluation", None),
        social_evaluation=certificate_information_dict.get("social_evaluation", None),
        credibility_evaluation=certificate_information_dict.get("social_evaluation", None),
    )
    for certificate_id, certificate_information_dict in certificate_information.items()
]
