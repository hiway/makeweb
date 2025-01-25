class defaults:
    remove_first_underscore = True
    replace_single_underscore = True
    replace_double_underscore = False
    replace_className = True
    replace_cls = True
    preserve_vendor_prefixes = True  # Add this line
    # https://html.spec.whatwg.org/multipage/syntax.html#the-doctype
    doctypes = {"html"}
    # https://developer.mozilla.org/en-US/docs/Web/HTML/Element
    tags = {
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
        "del",
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
        "input",
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
    }
    void_tags = {
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
    }
    deprecated_tags = {
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
    }
