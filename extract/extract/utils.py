from typing import Any, List


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
