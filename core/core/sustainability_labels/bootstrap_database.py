from datetime import datetime
from typing import Any, Dict, List

from ..domain import SustainabilityLabel
from . import load_and_get_sustainability_labels

certificates = load_and_get_sustainability_labels()


def _get_localized_certificate_attribute(
    certificate_information: Dict[str, Dict[str, Any]],
    attribute: str,
    language_order: List[str] = ["de", "en", "fr"],
) -> str:
    """
    Helper function to retrieve an `attribute` from `certificate_information`
        in the given `language_order`

    Args:
        certificate_information (Dict[str, Dict[str, Any]]): Dictionary that holds the
            sustainability label information.
        attribute (str): `attribute` to get.
        language_order (List[str], optional): Order of language priorities.
            Defaults to ["de", "en", "fr"].

    Returns:
       str: of the corresponding attribute in one language.
    """
    for language in language_order:
        if language in certificate_information["languages"].keys():
            return certificate_information["languages"][language][attribute]
    return ""


# List of `SustainabilityLabel` objects used to bootstrap database table
sustainability_labels = [
    SustainabilityLabel(
        id=certificate_id,
        timestamp=datetime(2022, 3, 3, 19),  # NOTE: Change me after updating sustainability labels
        name=_get_localized_certificate_attribute(certificate_information, "name"),
        description=_get_localized_certificate_attribute(certificate_information, "description"),
        ecological_evaluation=certificate_information.get("ecological_evaluation", None),
        social_evaluation=certificate_information.get("social_evaluation", None),
        credibility_evaluation=certificate_information.get("social_evaluation", None),
    )
    for certificate_id, certificate_information in load_and_get_sustainability_labels().items()
]
