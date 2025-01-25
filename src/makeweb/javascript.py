import inspect as _inspect

from .html import Doc
from .utilities import get_local_variable_from_caller


class JS(object):
    def __init__(self):
        self.funcs = []

    def __str__(self):
        return "".join([f for f in self.funcs])

    def function(self, func, skip_lines=1):
        try:  # pragma: no cover
            from metapensiero.pj.api import translates as _python_to_javascript
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "Please `pip install javascripthon` " "to use @js.function decorator."
            )
        try:  # pragma: no cover
            from jsmin import jsmin as _js_minify
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "Please `pip install jsmin` " "to use @js.function decorator."
            )

        source = _inspect.getsource(func)
        source = "\n".join(
            [
                l
                for l in source.splitlines()[skip_lines:]
                if not any(l.strip().startswith(b) for b in ["from mkwebpage", "@"])
            ]
        )
        self.funcs.append(_js_minify(_python_to_javascript(source)[0]))
        return func

    def script(self, func):
        self.function(func, skip_lines=2)
        return func

    def embed(self):
        doc = get_local_variable_from_caller("doc", Doc)
        doc.elements.append(self)
