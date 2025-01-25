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
            _warnings.warn("Expected doctype in:" + ",".join(defaults.doctypes))
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
        if _name in defaults.deprecated_tags:
            _warnings.warn(f"The {_name} tag is deprecated.")
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


html = _partial(Tag, "html")
head = _partial(Tag, "head")
link = _partial(Tag, "link")
meta = _partial(Tag, "meta")
style = _partial(Tag, "style")
title = _partial(Tag, "title")
body = _partial(Tag, "body")
address = _partial(Tag, "address")
article = _partial(Tag, "article")
aside = _partial(Tag, "aside")
footer = _partial(Tag, "footer")
header = _partial(Tag, "header")
h1 = _partial(Tag, "h1")
h2 = _partial(Tag, "h2")
h3 = _partial(Tag, "h3")
h4 = _partial(Tag, "h4")
h5 = _partial(Tag, "h5")
h6 = _partial(Tag, "h6")
hgroup = _partial(Tag, "hgroup")
nav = _partial(Tag, "nav")
section = _partial(Tag, "section")
blockquote = _partial(Tag, "blockquote")
dd = _partial(Tag, "dd")
dl = _partial(Tag, "dl")
dt = _partial(Tag, "dt")
div = _partial(Tag, "div")
figcaption = _partial(Tag, "figcaption")
figure = _partial(Tag, "figure")
hr = _partial(Tag, "hr")
ul = _partial(Tag, "ul")
ol = _partial(Tag, "ol")
li = _partial(Tag, "li")
main = _partial(Tag, "main")
p = _partial(Tag, "p")
pre = _partial(Tag, "pre")
a = _partial(Tag, "a")
abbr = _partial(Tag, "abbr")
b = _partial(Tag, "b")
bdi = _partial(Tag, "bdi")
bdo = _partial(Tag, "bdo")
br = _partial(Tag, "br")
cite = _partial(Tag, "cite")
code = _partial(Tag, "code")
data = _partial(Tag, "data")
dfn = _partial(Tag, "dfn")
em = _partial(Tag, "em")
i = _partial(Tag, "i")
kbd = _partial(Tag, "kbd")
mark = _partial(Tag, "mark")
q = _partial(Tag, "q")
rp = _partial(Tag, "rp")
rt = _partial(Tag, "rt")
rtc = _partial(Tag, "rtc")
ruby = _partial(Tag, "ruby")
s = _partial(Tag, "s")
samp = _partial(Tag, "samp")
small = _partial(Tag, "small")
span = _partial(Tag, "span")
strong = _partial(Tag, "strong")
sub = _partial(Tag, "sub")
sup = _partial(Tag, "sup")
time = _partial(Tag, "time")
u = _partial(Tag, "u")
var = _partial(Tag, "var")
wbr = _partial(Tag, "wbr")
area = _partial(Tag, "area")
audio = _partial(Tag, "audio")
img = _partial(Tag, "img")
map = _partial(Tag, "map")
track = _partial(Tag, "track")
video = _partial(Tag, "video")
embed = _partial(Tag, "embed")
iframe = _partial(Tag, "iframe")
object = _partial(Tag, "object")
param = _partial(Tag, "param")
picture = _partial(Tag, "picture")
source = _partial(Tag, "source")
canvas = _partial(Tag, "canvas")
noscript = _partial(Tag, "noscript")
script = _partial(Tag, "script")
_del = _partial(Tag, "del")
ins = _partial(Tag, "ins")
caption = _partial(Tag, "caption")
col = _partial(Tag, "col")
colgroup = _partial(Tag, "colgroup")
table = _partial(Tag, "table")
tbody = _partial(Tag, "tbody")
td = _partial(Tag, "td")
tfoot = _partial(Tag, "tfoot")
th = _partial(Tag, "th")
thead = _partial(Tag, "thead")
tr = _partial(Tag, "tr")
button = _partial(Tag, "button")
datalist = _partial(Tag, "datalist")
fieldset = _partial(Tag, "fieldset")
form = _partial(Tag, "form")
label = _partial(Tag, "label")
legend = _partial(Tag, "legend")
meter = _partial(Tag, "meter")
optgroup = _partial(Tag, "optgroup")
option = _partial(Tag, "option")
output = _partial(Tag, "output")
progress = _partial(Tag, "progress")
select = _partial(Tag, "select")
textarea = _partial(Tag, "textarea")
details = _partial(Tag, "details")
dialog = _partial(Tag, "dialog")
menu = _partial(Tag, "menu")
summary = _partial(Tag, "summary")
slot = _partial(Tag, "slot")
template = _partial(Tag, "template")
# Void Tags
area = _partial(VoidTag, "area")
base = _partial(VoidTag, "base")
br = _partial(VoidTag, "br")
col = _partial(VoidTag, "col")
embed = _partial(VoidTag, "embed")
hr = _partial(VoidTag, "hr")
img = _partial(VoidTag, "img")
_input = _partial(VoidTag, "input")
link = _partial(VoidTag, "link")
meta = _partial(VoidTag, "meta")
param = _partial(VoidTag, "param")
source = _partial(VoidTag, "source")
track = _partial(VoidTag, "track")
wbr = _partial(VoidTag, "wbr")
# Deprecated Tags
acronym = _partial(Tag, "acronym")
applet = _partial(Tag, "applet")
basefont = _partial(Tag, "basefont")
bgsound = _partial(Tag, "bgsound")
big = _partial(Tag, "big")
blink = _partial(Tag, "blink")
center = _partial(Tag, "center")
command = _partial(Tag, "command")
content = _partial(Tag, "content")
dir = _partial(Tag, "dir")
element = _partial(Tag, "element")
font = _partial(Tag, "font")
frame = _partial(Tag, "frame")
frameset = _partial(Tag, "frameset")
image = _partial(Tag, "image")
isindex = _partial(Tag, "isindex")
keygen = _partial(Tag, "keygen")
listing = _partial(Tag, "listing")
marquee = _partial(Tag, "marquee")
menuitem = _partial(Tag, "menuitem")
multicol = _partial(Tag, "multicol")
nextid = _partial(Tag, "nextid")
nobr = _partial(Tag, "nobr")
noembed = _partial(Tag, "noembed")
noframes = _partial(Tag, "noframes")
plaintext = _partial(Tag, "plaintext")
shadow = _partial(Tag, "shadow")
spacer = _partial(Tag, "spacer")
strike = _partial(Tag, "strike")
tt = _partial(Tag, "tt")
xmp = _partial(Tag, "xmp")

__all__ = [
    # Tags
    "html",
    "head",
    "link",
    "meta",
    "style",
    "title",
    "body",
    "address",
    "article",
    "aside",
    "footer",
    "header",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hgroup",
    "nav",
    "section",
    "blockquote",
    "dd",
    "dl",
    "dt",
    "div",
    "figcaption",
    "figure",
    "hr",
    "ul",
    "ol",
    "li",
    "main",
    "p",
    "pre",
    "a",
    "abbr",
    "b",
    "bdi",
    "bdo",
    "br",
    "cite",
    "code",
    "data",
    "dfn",
    "em",
    "i",
    "kbd",
    "mark",
    "q",
    "rp",
    "rt",
    "rtc",
    "ruby",
    "s",
    "samp",
    "small",
    "span",
    "strong",
    "sub",
    "sup",
    "time",
    "u",
    "var",
    "wbr",
    "area",
    "audio",
    "img",
    "map",
    "track",
    "video",
    "embed",
    "iframe",
    "object",
    "param",
    "picture",
    "source",
    "canvas",
    "noscript",
    "script",
    "_del",
    "ins",
    "caption",
    "col",
    "colgroup",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "button",
    "datalist",
    "fieldset",
    "form",
    "_input",
    "label",
    "legend",
    "meter",
    "optgroup",
    "option",
    "output",
    "progress",
    "select",
    "textarea",
    "details",
    "dialog",
    "menu",
    "summary",
    "slot",
    "template",
    # VoidTags
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
    # Deprecated Tags
    "acronym",
    "applet",
    "basefont",
    "bgsound",
    "big",
    "blink",
    "center",
    "command",
    "content",
    "dir",
    "element",
    "font",
    "frame",
    "frameset",
    "image",
    "isindex",
    "keygen",
    "listing",
    "marquee",
    "menuitem",
    "multicol",
    "nextid",
    "nobr",
    "noembed",
    "noframes",
    "plaintext",
    "shadow",
    "spacer",
    "strike",
    "tt",
    "xmp",
]
