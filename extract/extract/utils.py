import re
from logging import getLogger
from typing import Any, Iterable, List, Optional, Union

from core.domain import CertificateType
from core.sustainability_labels import load_and_get_sustainability_labels

SUSTAINABILITY_LABELS = load_and_get_sustainability_labels()
logger = getLogger(__name__)

_certificate_category_names = {
    "LAPTOP": ["LAPTOPS", "NOTEBOOKS", "LAPTOP", "NOTEBOOK"],
    "SMARTPHONE": ["SMARTPHONES", "MOBILE_PHONES", "SMARTPHONE", "MOBILE_PHONE"],
}


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


def check_none_or_alternative(check_value: Any, alternative_value: Any) -> Any:
    """
    Helper function that returns alternative_value if check_value is None, otherwise check_value
    is returned.

    Args:
        check_value (Any): object to check if it is None.
        alternative_value (Any): object to return if check_value is None.

    Returns:
        Any: either check_value or alternative_value.
    """
    if check_value is None:
        return alternative_value
    return check_value


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
    certificate_strings: Iterable[str],
    certificate_mapping: dict,
    product_category: str = "",
) -> Optional[list[str]]:
    """
    Helper function that maps the extracted HTML span texts to certificates.
    1. It tries all known certificates
    2. It uses`certificate_mapping` for shop specific certificates strings
    3. It replaces certificates with category-specific version if possible
    4. If no mapping is found, 'CertificateType.UNKNOWN' is assigned and the unknown
    certificate_string is logged.

    Args:
        certificate_strings (list[str]): Certificate strings from the HTML span tags
        certificate_mapping (dict): Mapping of certificate strings to certificates
        product_category (str): Category of the product, to infer category-specific labels

    Returns:
        Optional[list[str]]: List of parsed certificates or None if certificate_strings is empty
    """

    # Return None if certificate_strings is empty
    if not certificate_strings:
        return None

    result = dict.fromkeys(set(certificate_strings))

    # check all known certificates
    for certificate_id, localized_certificate_infos in SUSTAINABILITY_LABELS.items():
        for certificate_string in result.keys():
            if any(
                _get_certificate_for_any_language(
                    localized_certificate_infos["languages"].values(), certificate_string
                )
            ):
                result.update({certificate_string: CertificateType[certificate_id.split(":")[-1]]})

    # check custom certificate_mappings for unassigned certificate strings
    for certificate_string, certificate in result.items():
        if certificate is None:
            if certificate_string in certificate_mapping.keys():
                result.update({certificate_string: certificate_mapping[certificate_string]})
            else:  # if certificate_string can not be mapped, assign UNKNOWN and create log message
                result.update({certificate_string: CertificateType.UNKNOWN})  # type: ignore[attr-defined] # noqa
                logger.info(f"unknown sustainability label: {certificate_string}")

    # assign (general) extracted certificates to a product category-specific version, if possible
    if product_category in _certificate_category_names.keys():
        # loop over all extracted and stored labels and potential category synonyms
        for certificate_string, certificate in result.items():
            for label in SUSTAINABILITY_LABELS.keys():
                for category_alt_name in _certificate_category_names.get(product_category, []):
                    # check for a product category-specific label
                    if re.search(f"^{certificate.value}.*{category_alt_name}$", label):  # type: ignore # noqa
                        result.update({certificate_string: label})

    return sorted(set(result.values()))  # type: ignore


def _get_certificate_for_any_language(
    localized_certificate_infos: list[dict], certificate_string: str
) -> list[dict]:
    """
    Helper function that checks if a certificate matches in a language with a certificate name.

    Args:
        localized_certificate_infos (list[dict]): List of `dict` objects with each object
            containing the certificate information in a specific language
        certificate_strings (str): Function that is processing the scan result

    Returns:
        list[dict]: `list` with `dict` objects representing the matched certificate information
            in a specific language.
    """
    return [
        localized_certificate_info
        for localized_certificate_info in localized_certificate_infos
        if localized_certificate_info["name"].lower() == certificate_string.lower()
    ]


def check_and_create_attributes_list(
    attributes: Union[str, List[str], None]
) -> Optional[List[str]]:
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

    if isinstance(attributes, str):
        if attributes in attributes_to_remove:
            return None
        return [attributes]
    elif isinstance(attributes, list):
        return list(filter(lambda attr: attr not in attributes_to_remove, attributes))
    return None
