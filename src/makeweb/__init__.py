__version__ = "0.1.0"

from .defaults import defaults
from .html import Doc, Tag, Text
from .javascript import JS
from .stylesheet import CSS
from .utilities import fix_attribute, get_local_variable_from_caller


__all__ = [
    "Tag",
    "Doc",
    "Text",
    "CSS",
    "JS",
    "defaults",
    "fix_attribute",
    "get_local_variable_from_caller",
    "html",
    "javascript",
    "stylesheet",
    "utilities",
]

__all__ += list(defaults.tags) + list(defaults.void_tags)
