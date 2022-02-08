from datetime import datetime
from typing import Dict

from core.domain import LabelIDType, SustainabilityLabel

information_from = datetime(2022, 1, 25, 12)

__label_information: Dict[str, Dict[str, str]] = {
    LabelIDType.BCORP.name: {
        "name": "B Corporation",
        "description": "",
    },
    LabelIDType.CTC_T_SILVER.name: {
        "name": "Cradle to Cradle - Silver Level",
        "description": "",
    },
    LabelIDType.CTC_T_GOLD.name: {
        "name": "Cradle to Cradle - Gold Level",
        "description": "",
    },
    LabelIDType.GK.name: {
        "name": "Grüner Knopf",
        "description": "",
    },
    LabelIDType.HIGG.name: {
        "name": "Higg Index",
        "description": "",
    },
    LabelIDType.OCS.name: {
        "name": "Organic Content Standard",
        "description": "",
    },
    LabelIDType.OCS_100.name: {
        "name": "Organic Content Standard - 100",
        "description": "",
    },
    LabelIDType.OCS_BLENDED.name: {
        "name": "Organic Content Standard - Blended",
        "description": "",
    },
    LabelIDType.PETA.name: {
        "name": "PETA-approved",
        "description": "",
    },
    LabelIDType.RCS_BLENDED.name: {
        "name": "Recycled Claim Standard - Blended",
        "description": "",
    },
    LabelIDType.RCS_100.name: {
        "name": "Recycled Claim Standard - 100",
        "description": "",
    },
    LabelIDType.RWS.name: {
        "name": "Responsible Wool Standard",
        "description": "",
    },
    LabelIDType.SOILA.name: {
        "name": "Soil Association",
        "description": "",
    },
    LabelIDType.BLUES_A.name: {
        "name": "bluesign® APPROVED",
        "description": "",
    },
    LabelIDType.CTC_T_BRONZE.name: {
        "name": "Cradle to Cradle Certified™ Platinum",
        "description": "",
    },
    LabelIDType.GCS.name: {
        "name": "The Good Cashmere Standard®",
        "description": "Mit der Entwicklung des Good Cashmere Standards hat die Aid by Trade Foundation einen neuen Maßstab für die Produktion von nachhaltigem Kaschmir definiert. Der Standard beinhaltet die vom Farm Animal Welfare Council festgelegten Fünf Freiheiten. Der Good Cashmere Standard folgt drei Hauptprinzipien: Förderung des Tierwohls in der Kaschmirproduktion, Unterstützung der Kaschmirfarmer zur Sicherung einer nachhaltigen Einkommensquelle, sowie Umweltschutz.",  # noqa
    },
    LabelIDType.GOTS_ORGANIC.name: {
        "name": "GOTS - organic",
        "description": "Der Global Organic Textile Standard ist eine der führenden und vertrauensvollsten Zertifizierungen für Textilien aus Biofasern. Produkte mit diesem Label bestehen zu mindestens 95% aus biologischem Material. Jeder Partner in der Zulieferkette wird überprüft, um eine umweltbewusste und sozial verantwortungsvolle Herstellung zu garantieren.",  # noqa
    },
    LabelIDType.GOTS_MWOM.name: {
        "name": "GOTS - made with organic materials",
        "description": "Der Global Organic Textile Standard ist eine der führenden und vertrauensvollsten Zertifizierungen für Textilien aus Biofasern. Produkte mit GOTS-Zertifikat bestehen zu mindestens 70% aus organischem Material. Jeder Partner in der Zulieferkette wird überprüft, um eine umweltbewusste und sozial verantwortungsvolle Herstellung zu garantieren.",  # noqa
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
