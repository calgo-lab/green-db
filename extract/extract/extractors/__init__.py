import pkgutil

names = __all__ = [module_info.name for module_info in pkgutil.iter_modules(__path__)]  # noqa: 405
# this doesnt import anything.

from . import *  # noqa: 403

# this actually imports the extractors
# for some reason it only finds them when __all__ is set
