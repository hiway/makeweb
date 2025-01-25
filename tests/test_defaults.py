from makeweb import defaults


def test_defaults():
    assert defaults.remove_first_underscore is True
    assert defaults.replace_single_underscore is True
    assert defaults.replace_double_underscore is False
    assert defaults.replace_className is True
    assert defaults.replace_cls is True
    assert defaults.void_tags == {
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
    for dtag in defaults.deprecated_tags:
        assert dtag not in defaults.tags
        assert dtag not in defaults.void_tags
