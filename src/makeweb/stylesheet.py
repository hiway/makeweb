from .html import Doc
from .utilities import fix_attribute, get_local_variable_from_caller


class CSS(object):
    def __init__(self):
        self.style = []

    def __str__(self):
        return "".join(self.style)

    def __call__(self, _target, **attrs):
        attrs = ["{}:{}".format(fix_attribute(_a), _v) for _a, _v in attrs.items()]
        style = "%s{%s}" % (_target, ";".join(attrs))
        self.style.append(style)

    def embed(self):
        doc = get_local_variable_from_caller("doc", Doc)
        doc.elements.append(self)
