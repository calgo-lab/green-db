from typing import Any, List

from core.domain import CertificateType
from core.sustainability_labels import load_and_get_sustainability_labels


def safely_return_first_element(list_object: List[Any], else_return: Any = {}) -> Any:
    """
    Helper function to safely return the first element of `list_object` if it exists.
    If not return `else_return`.

    Args:
        list_object (List[Any]): `list` of objects to return first element if it exists
        else_return (Any, optional): Return value if `list_object` is empty. Defaults to {}.

    Returns:
        Any: First object in `list_object` or `else_return`
    """
    if type(list_object) != list or len(list_object) == 0:
        return else_return

    else:
        return list_object[0]


def sustainability_labels_to_certificates(labels: list[str], label_mapping: dict) -> list[str]:
    """
    Helper function that maps the extracted HTML span texts to certificates.

    Args:
        labels list[str]: Label strings from the HTML span tags
        label_mapping (dict): Mapping of label strings to certificates

    Returns:
        list[str]: List of parsed certificates
    """
    sustainability_labels = load_and_get_sustainability_labels()

    result = [
        CertificateType[certificate.split(":")[-1]]
        for certificate, description in sustainability_labels.items()
        if any(_get_matching_languages(description["languages"].values(), labels))
    ]

    for label, certificate in label_mapping.items():
        if label in labels:
            result.append(certificate)

    return sorted(result) or [CertificateType.UNKNOWN]  # type: ignore[attr-defined]


def _get_matching_languages(languages: list[dict], labels: list[str]) -> list[dict]:
    """
    Helper function that checks if a label from `load_and_get_sustainability_labels`
    matches in a language with a label name.

    Args:
        languages (list[dict]): List of `dict` objects with each object containing the
            label information in a specific language
        labels (list[str]): Function that is processing the scan result

    Returns:
        list[dict]: `list` with `dict` objects representing the matched label information
            in a specific language.
    """
    return [language for language in languages if language["name"] in labels]
