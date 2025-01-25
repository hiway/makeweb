import sys as _sys
import warnings as _warnings
from functools import partial as _partial

# Suppress specific AST deprecation warnings from javascripthon
_warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="metapensiero.pj"
)
_warnings.filterwarnings("ignore", message="ast.Str is deprecated")
_warnings.filterwarnings("ignore", message="Attribute s is deprecated")

from .defaults import defaults
from .utilities import fix_attribute, get_local_variable_from_caller


class Doc(object):
    def __init__(self, doctype="", lang="en"):
        if doctype and doctype not in defaults.doctypes:
            _warnings.warn("Expected doctype=html.")
        self.lang = lang
        self.elements = []
        self.parent = "<root>"
        self.doctype = doctype

    def __str__(self):
        header = ""
        footer = ""
        if self.doctype:
            header = '<!doctype {}><html lang="{}">'.format(self.doctype, self.lang)
            footer = "</html>"
        return header + "".join([str(e) for e in self.elements]) + footer


class Tag(object):
    def __init__(self, _name, *elements, close=True, **attrs):
        self.name = _name or ""
        self.attrs = {fix_attribute(k): v for k, v in attrs.items()}
        self.elements = [e for e in elements if self.validate(_name, e)]
        self.close = close
        doc = get_local_variable_from_caller("doc", Doc)
        if doc.elements and elements:
            if doc.elements[-1] == elements[0]:
                doc.elements.pop()
        doc.elements.append(self)

    def __str__(self):
        name = self.name
        attrs = "".join(
            [
                ' {}="{}"'.format(k, v)
                for k, v in self.attrs.items()
                if not isinstance(v, bool)
            ]
        )
        # Handle boolean attributes separately.
        attrs += "".join(
            [" {}".format(k) for k, v in self.attrs.items() if isinstance(v, bool)]
        )
        if not self.close:
            _tag = "<{name}{attrs} />".format(name=name, attrs=attrs)
            return _tag
        _begin = "<{name}{attrs}>".format(name=name, attrs=attrs)
        _children = "".join([str(c) for c in self.elements if c])
        _end = "</{name}>".format(name=name)
        return _begin + _children + _end

    def __enter__(self, **elements):
        doc = get_local_variable_from_caller("doc", Doc)
        doc.parent, self.parent = self.name, doc.parent
        self.backup, doc.elements = doc.elements, self.elements

    def __exit__(self, exc_type, exc_val, exc_tb):
        doc = get_local_variable_from_caller("doc", Doc)
        doc.parent = self.parent
        doc.elements, self.elements = self.backup, doc.elements

    def validate(self, _name, element):
        if element is None:
            return False
        elif isinstance(element, (str, Tag, Doc)):
            return True
        raise TypeError(
            "Validation failed for element {!r}: {!r}, "
            "expected str, Tag or Doc.".format(_name, element)
        )


class VoidTag(Tag):
    """
    https://html.spec.whatwg.org/multipage/syntax.html#void-elements
    """

    def __init__(self, _name, *elements, **attrs):
        super(VoidTag, self).__init__(_name, *elements, close=False, **attrs)


class Text(Tag):
    def __init__(self, text):
        self.text = text
        super(Text, self).__init__("text", text)

    def __str__(self):
        return self.text


class MakeWeb(object):
    def __getattr__(self, name):
        if name.startswith("__"):
            return self.__getattribute__(name)
        elif name in {
            "Tag",
            "Doc",
            "Text",
            "CSS",
            "JS",
            "defaults",
            "fix_attribute",
            "get_local_variable_from_caller",
        }:
            return globals()[name]
        # Everything else is treated as HTML Tag.
        name = fix_attribute(name)
        if name.lower() in defaults.void_tags:
            tag = _partial(VoidTag, name)
        else:
            if name in defaults.deprecated_tags:
                _warnings.warn(
                    "The {!r} tag is deprecated. "
                    "See: https://developer.mozilla.org/en-US/docs/Web/HTML/Element"
                )
            if name not in defaults.tags:
                _warnings.warn("Unknown tag {!r}.".format(name))
            tag = _partial(Tag, name)
        return tag


_sys.modules[__name__] = MakeWeb()
