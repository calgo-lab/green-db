from datetime import datetime
from typing import Dict

from core.domain import LabelIDType, SustainabilityLabel

information_from = datetime(2022, 1, 25, 12)

__label_information: Dict[str, Dict[str, str]] = {
    LabelIDType.OTHER.name: {
        "name": "OTHER",
        "description": "Dieses 'Label' ist GreenDB intern. Es wird verwendet, wenn ein Shop das Produkt als nachhaltig listet, unsere Nachhlatigkeitsexpert*innen dies aber nicht nachvollziehen können. Es handelt sich also um falsche oder nicht belastbare Informationen",  # noqa
    },
    LabelIDType.UNKNOWN.name: {
        "name": "UNKNOWN",
        "description": "Dieses 'Label' ist GreenDB intern. Es wird verwendet, wenn die Angaben des Shops von uns (noch) nicht überprüft wurden.",  # noqa
    },
}

sustainability_labels = [
    SustainabilityLabel(
        id=label_id,
        timestamp=information_from,
        name=label_information_dict["name"],
        description=label_information_dict["description"],
        ecological_evaluation=label_information_dict.get("ecological_evaluation", None),
        social_evaluation=label_information_dict.get("social_evaluation", None),
        credibility_evaluation=label_information_dict.get("social_evaluation", None),
    )
    for label_id, label_information_dict in __label_information.items()
]
