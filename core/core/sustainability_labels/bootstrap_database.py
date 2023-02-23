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
        timestamp=datetime(2023, 2, 23),  # NOTE: Change me after updating sustainability labels
        name=_get_localized_certificate_attribute(certificate_information, "name"),
        description=_get_localized_certificate_attribute(certificate_information, "description"),
        cred_credibility=certificate_information.get("cred_credibility", None),
        eco_chemicals=certificate_information.get("eco_chemicals", None),
        eco_lifetime=certificate_information.get("eco_lifetime", None),
        eco_water=certificate_information.get("eco_water", None),
        eco_inputs=certificate_information.get("eco_inputs", None),
        eco_quality=certificate_information.get("eco_quality", None),
        eco_energy=certificate_information.get("eco_energy", None),
        eco_waste_air=certificate_information.get("eco_waste_air", None),
        eco_environmental_management=certificate_information.get(
            "eco_environmental_management", None
        ),
        social_labour_rights=certificate_information.get("social_labour_rights", None),
        social_business_practice=certificate_information.get("social_business_practice", None),
        social_social_rights=certificate_information.get("social_social_rights", None),
        social_company_responsibility=certificate_information.get(
            "social_company_responsibility", None
        ),
        social_conflict_minerals=certificate_information.get("social_conflict_minerals", None),
    )
    for certificate_id, certificate_information in load_and_get_sustainability_labels().items()
]
