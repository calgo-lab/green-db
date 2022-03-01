import json
from datetime import datetime

from core.domain import SustainabilityLabel

information_from = datetime(2022, 1, 25, 12)

# flake8: noqa
with open("siegelklarheit.json", "r") as file:
    __label_information = json.load(file)

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
