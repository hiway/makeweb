__version__ = '0.1.0'

import sys as _sys
from functools import partial as _partial, reduce
import inspect as _inspect
import os as _os
import warnings as _warnings


class defaults:
    remove_first_underscore = True
    replace_single_underscore = False
    replace_double_underscore = True
    replace_className = True
    replace_cls = True
    # https://html.spec.whatwg.org/multipage/syntax.html#the-doctype
    doctypes = {'html'}
    # https://developer.mozilla.org/en-US/docs/Web/HTML/Element
    tags = {
        'html', 'head', 'link', 'meta', 'style', 'title', 'body',
        'address', 'article', 'aside', 'footer', 'header',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hgroup',
        'nav', 'section',
        'blockquote', 'dd', 'dl', 'dt', 'div',
        'figcaption', 'figure', 'hr', 'ul', 'ol', 'li',
        'main', 'p', 'pre',
        'a', 'abbr', 'b', 'bdi', 'bdo', 'br',
        'cite', 'code', 'data', 'dfn', 'em', 'i', 'kbd', 'mark',
        'q', 'rp', 'rt', 'rtc', 'ruby', 's', 'samp',
        'small', 'span', 'strong', 'sub', 'sup', 'time',
        'u', 'var', 'wbr',
        'area', 'audio', 'img', 'map', 'track', 'video',
        'embed', 'iframe', 'object',
        'param', 'picture', 'source',
        'canvas', 'noscript', 'script',
        'del', 'ins',
        'caption', 'col', 'colgroup', 'table', 'tbody', 'td', 'tfoot',
        'th', 'thead', 'tr',
        'button', 'datalist', 'fieldset', 'form', 'input', 'label',
        'legend', 'meter', 'optgroup', 'option',
        'output', 'progress', 'select', 'textarea',
        'details', 'dialog', 'menu', 'summary',
        'slot', 'template', }
    void_tags = {'area', 'base', 'br', 'col', 'embed', 'hr',
                 'img', 'input', 'link', 'meta', 'param',
                 'source', 'track', 'wbr'}
    deprecated_tags = {
        'acronym', 'applet', 'basefont', 'bgsound', 'big', 'blink', 'center',
        'command', 'content', 'dir', 'element', 'font', 'frame', 'frameset',
        'image', 'isindex', 'keygen', 'listing', 'marquee', 'menuitem',
        'multicol', 'nextid', 'nobr', 'noembed', 'noframes', 'plaintext',
        'shadow', 'spacer', 'strike', 'tt', 'xmp'}


def fix_attribute(attrib: str):
    if not isinstance(attrib, str):
        raise TypeError('Expected attrib to be str, got: {!r}'.format(attrib))
    if attrib == 'cls' and defaults.replace_cls:
        return 'class'
    elif attrib == 'className' and defaults.replace_className:
        return 'class'
    if defaults.replace_double_underscore:
        attrib = attrib.replace('__', '-')
    if attrib.startswith('_') and defaults.remove_first_underscore:
        attrib = attrib[1:]
    if defaults.replace_single_underscore:
        attrib = attrib.replace('_', '-')
    return attrib


def get_local_variable_from_caller(name, _type):
    """
    Heads-up: Python magic ahead.

    This function reaches backwards in the calling stack to extract
    a local variable that is expected to be defined
    in the function that called the function that called this function.
    Extracts the variable `name`, validates its `_type` and returns it.

    Raises:

        LookupError: if variable named `name` is not found.

        TypeError: if variable `name` is not an instance of `_type`.
    """
    assert isinstance(name, str)
    assert _type is not None
    frame = _inspect.currentframe()
    try:
        # Go two frames back, because this function is also on the stack.
        caller_locals = frame.f_back.f_back.f_locals
        if name not in caller_locals:
            # Go one level back to allow calling from VoidTag's __init__()
            caller_locals = frame.f_back.f_back.f_back.f_locals
            if name not in caller_locals:
                # Allow list comprehensions inside second level functions!!
                caller_locals = frame.f_back.f_back.f_back.f_back.f_locals
        if name in caller_locals:
            var = caller_locals[name]
            if not isinstance(var, _type):
                raise TypeError('Expected {!r} to be an instance of ' \
                                '{!r}, got: {!r}.' \
                                ''.format(name, _type, var))
            return var
        else:
            raise LookupError('Expected `{name} = {type}()` to be '
                              'defined before calling a tag.')
    finally:
        del frame


class Doc(object):
    def __init__(self, doctype='', lang='en'):
        if doctype and doctype not in defaults.doctypes:
            _warnings.warn('Expected doctype=html.')
        self.lang = lang
        self.elements = []
        self.parent = '<root>'
        self.doctype = doctype

    def __str__(self):
        header = ''
        footer = ''
        if self.doctype:
            header = '<!doctype {}><html lang="{}">'.format(self.doctype, self.lang)
            footer = '</html>'
        return header + ''.join([str(e) for e in self.elements]) + footer


class Tag(object):
    def __init__(self, _name, *elements, close=True, **attrs):
        self.name = _name or ''
        self.attrs = {fix_attribute(k): v for k, v in attrs.items()}
        self.elements = [e for e in elements if self.validate(_name, e)]
        self.close = close
        doc = get_local_variable_from_caller('doc', Doc)
        if doc.elements and elements:
            if doc.elements[-1] == elements[0]:
                doc.elements.pop()
        doc.elements.append(self)

    def __str__(self):
        name = self.name
        attrs = ''.join([' {}="{}"'.format(k, v)
                         for k, v in self.attrs.items()
                         if not isinstance(v, bool)])
        # Handle boolean attributes separately.
        attrs += ''.join([' {}'.format(k)
                          for k, v in self.attrs.items()
                          if isinstance(v, bool)])
        if not self.close:
            _tag = '<{name}{attrs} />'.format(name=name, attrs=attrs)
            return _tag
        _begin = '<{name}{attrs}>'.format(name=name, attrs=attrs)
        _children = ''.join([str(c) for c in self.elements if c])
        _end = '</{name}>'.format(name=name)
        return _begin + _children + _end

    def __enter__(self, **elements):
        doc = get_local_variable_from_caller('doc', Doc)
        doc.parent, self.parent = self.name, doc.parent
        self.backup, doc.elements = doc.elements, self.elements

    def __exit__(self, exc_type, exc_val, exc_tb):
        doc = get_local_variable_from_caller('doc', Doc)
        doc.parent = self.parent
        doc.elements, self.elements = self.backup, doc.elements

    def validate(self, _name, element):
        if element is None:
            return False
        elif isinstance(element, (str, Tag, Doc)):
            return True
        raise TypeError('Validation failed for element {!r}: {!r}, '
                        'expected str, Tag or Doc.'.format(_name, element))


class VoidTag(Tag):
    """
    https://html.spec.whatwg.org/multipage/syntax.html#void-elements
    """

    def __init__(self, _name, *elements, **attrs):
        super(VoidTag, self).__init__(_name, *elements, close=False, **attrs)


class Text(Tag):
    def __init__(self, text):
        self.text = text
        super(Text, self).__init__('text', text)

    def __str__(self):
        return self.text


class CSS(object):
    def __init__(self):
        self.style = []

    def __str__(self):
        return ''.join(self.style)

    def __call__(self, _target, **attrs):
        attrs = ['{}:{}'.format(fix_attribute(_a), _v)
                 for _a, _v in attrs.items()]
        style = '%s{%s}' % (_target, ';'.join(attrs))
        self.style.append(style)

    def embed(self):
        doc = get_local_variable_from_caller('doc', Doc)
        doc.elements.append(self)


class JS(object):
    def __init__(self):
        self.funcs = []

    def __str__(self):
        return ''.join([f for f in self.funcs])

    def function(self, func, skip_lines=1):
        try:  # pragma: no cover
            from metapensiero.pj.api import translates as _python_to_javascript
        except ImportError as e:  # pragma: no cover
            raise ImportError("Please `pip install javascripthon` "
                              "to use @js.function decorator.")
        try:  # pragma: no cover
            from jsmin import jsmin as _js_minify
        except ImportError as e:  # pragma: no cover
            raise ImportError("Please `pip install jsmin` "
                              "to use @js.function decorator.")

        source = _inspect.getsource(func)
        source = '\n'.join([l for l in source.splitlines()[skip_lines:]
                            if not any(l.strip().startswith(b)
                                       for b in ['from mkwebpage', '@'])])
        self.funcs.append(_js_minify(_python_to_javascript(source)[0]))
        return func

    def script(self, func):
        self.function(func, skip_lines=2)
        return func

    def embed(self):
        doc = get_local_variable_from_caller('doc', Doc)
        doc.elements.append(self)


class MakeWeb(object):
    def __getattr__(self, name):
        if name.startswith('__'):
            return self.__getattribute__(name)
        elif name in {'Tag', 'Doc', 'Text', 'CSS', 'JS', 'defaults', 'fix_attribute',
                      'get_local_variable_from_caller'}:
            return globals()[name]
        # Everything else is treated as HTML Tag.
        name = fix_attribute(name)
        if name.lower() in defaults.void_tags:
            tag = _partial(VoidTag, name)
        else:
            if name in defaults.deprecated_tags:
                _warnings.warn('The {!r} tag is deprecated. '
                               'See: https://developer.mozilla.org/en-US/docs/Web/HTML/Element')
            if name not in defaults.tags:
                _warnings.warn('Unknown tag {!r}.'.format(name))
            tag = _partial(Tag, name)
        return tag


_sys.modules[__name__] = MakeWeb()
