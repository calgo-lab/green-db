from typing import Any, List, Union

from core.domain import CertificateType
from core.sustainability_labels import load_and_get_sustainability_labels

SUSTAINABILITY_LABELS = load_and_get_sustainability_labels()


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


def get_product_from_JSON_LD(json_ld: List[Any], else_return: Any = {}) -> Any:
    """
    Helper function to return the product element of a `JSON_LD` object if it exists.
    If not return `else_return`.

    Args:
        json_ld (List[Any]): `list` of objects to return product element if it exists
        else_return (Any, optional): Return value if `list_object` is empty. Defaults to {}.

    Returns:
        Any: product object in `json_ld` or `else_return`
    """
    if isinstance(json_ld, list):
        for element in json_ld:
            if element.get("@type") == "Product":
                return element
    else:
        return else_return


def sustainability_labels_to_certificates(
    certificate_strings: list[str], certificate_mapping: dict
) -> list[str]:
    """
    Helper function that maps the extracted HTML span texts to certificates.
    1. It tries all known certificates
    2. It uses`certificate_mapping` for shop specific certificates strings

    Args:
        certificate_strings list[str]: Certificate strings from the HTML span tags
        certificate_mapping (dict): Mapping of certificate strings to certificates

    Returns:
        list[str]: List of parsed certificates
    """

    result = [
        CertificateType[certificate_id.split(":")[-1]]
        for certificate_id, localized_certificate_infos in SUSTAINABILITY_LABELS.items()
        if any(
            _get_certificate_for_any_language(
                localized_certificate_infos["languages"].values(), certificate_strings
            )
        )
    ]

    for certificate_string, certificate in certificate_mapping.items():
        if certificate_string in certificate_strings:
            result.append(certificate)

    return sorted(set(result)) or [CertificateType.UNKNOWN]  # type: ignore[attr-defined]


def _get_certificate_for_any_language(
    localized_certificate_infos: list[dict], certificate_strings: list[str]
) -> list[dict]:
    """
    Helper function that checks if a certificate matches in a language with a certificate name.

    Args:
        localized_certificate_infos (list[dict]): List of `dict` objects with each object
            containing the certificate information in a specific language
        certificate_strings (list[str]): Function that is processing the scan result

    Returns:
        list[dict]: `list` with `dict` objects representing the matched certificate information
            in a specific language.
    """
    return [
        localized_certificate_info
        for localized_certificate_info in localized_certificate_infos
        if localized_certificate_info["name"].lower() in [x.lower() for x in certificate_strings]
    ]


def safely_convert_attribute_to_array(attribute: Union[str, List[str]]) -> List[str]:
    """
    Helper function to convert an attribute to a list. If it's already a list `None` elements are
    removed.

    Args:
        attribute (Union[str, List[str]]): single attribute as `str` or List of `str` objects with
        each object containing for example a color or size.

    Returns:
        list[str]: `list` with `str` objects holding the attribute information.
    """
    attributes_to_remove = [None, "None"]

    if isinstance(attribute, str):
        if attribute in attributes_to_remove:
            return None
        return [attribute]
    elif isinstance(attribute, List):
        return list(filter(lambda attr: attr not in attributes_to_remove, attribute))
    return None
