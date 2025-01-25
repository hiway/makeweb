import inspect as _inspect


from .defaults import defaults


def fix_attribute(attrib: str):
    if not isinstance(attrib, str):
        raise TypeError("Expected attrib to be str, got: {!r}".format(attrib))
    if attrib == "cls" and defaults.replace_cls:
        return "class"
    elif attrib == "className" and defaults.replace_className:
        return "class"
    if defaults.replace_double_underscore:
        attrib = attrib.replace("__", "-")
    if attrib.startswith("_") and defaults.remove_first_underscore:
        attrib = attrib[1:]
    if defaults.replace_single_underscore:
        attrib = attrib.replace("_", "-")
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
                raise TypeError(
                    "Expected {!r} to be an instance of "
                    "{!r}, got: {!r}."
                    "".format(name, _type, var)
                )
            return var
        else:
            raise LookupError(
                "Expected `{name} = {type}()` to be " "defined before calling a tag."
            )
    finally:
        del frame
