from typing import Any, List


def safely_return_first_element(list_object: List[Any], else_return: Any = {}) -> Any:

    if type(list_object) != list or len(list_object) == 0:
        return else_return

    else:
        return list_object[0]
