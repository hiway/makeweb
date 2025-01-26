from .html import Doc
from .utilities import fix_attribute, get_local_variable_from_caller


class CSS(object):
    def __init__(self):
        self.style = []

    def __str__(self):
        return "".join(self.style)

    def __call__(self, _target, **attrs):
        # Special handling for @keyframes and @media queries
        if _target.startswith("@keyframes") or _target.startswith("@media"):
            rules = []
            for selector, properties in attrs.items():
                if isinstance(properties, dict):
                    formatted_props = [
                        f"{fix_attribute(k)}:{v}" for k, v in properties.items()
                    ]
                    rules.append(f"{selector}{{{';'.join(formatted_props)}}}")
            style = f"{_target}{{{';'.join(rules)}}}"
        else:
            # Regular CSS rules
            attrs = [f"{fix_attribute(k)}:{v}" for k, v in attrs.items()]
            style = f"{_target}{{{';'.join(attrs)}}}"

        self.style.append(style)

    def embed(self):
        doc = get_local_variable_from_caller("doc", Doc)
        doc.elements.append(self)
