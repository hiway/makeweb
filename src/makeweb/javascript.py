import inspect as _inspect
import sys as _sys

from .html import Doc
from .utilities import get_local_variable_from_caller


def _try_minify(js_code, do_minify=True):
    if not do_minify:
        return js_code
    try:
        from jsmin import jsmin

        return jsmin(js_code)
    except ImportError:  # pragma: no cover
        raise ImportError("Please `pip install jsmin` to minify JavaScript code.")


class JS(object):
    def __init__(self, minify=True):
        self.funcs = []
        self.minify = minify

    def __str__(self):
        return "".join([f for f in self.funcs])

    def function(self, func, skip_lines=1):
        try:  # pragma: no cover
            from metapensiero.pj.api import translates as _python_to_javascript
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "Please `pip install javascripthon` " "to use @js.function decorator."
            )
        source = _inspect.getsource(func)
        source = "\n".join(
            [
                l
                for l in source.splitlines()[skip_lines:]
                if not any(l.strip().startswith(b) for b in ["from mkwebpage", "@"])
            ]
        )
        js_code = _python_to_javascript(source)[0]
        self.funcs.append(_try_minify(js_code, self.minify))
        return func

    def script(self, func):
        self.function(func, skip_lines=2)
        return func

    def embed(self):
        doc = get_local_variable_from_caller("doc", Doc)
        doc.elements.append(self)


class JavaScript:
    def __getattr__(self, name):
        if name.startswith("__"):
            return self.__getattribute__(name)
        if name in globals():
            return globals()[name]
        # Import dummy javascript objects
        return object


_sys.modules[__name__] = JavaScript()
