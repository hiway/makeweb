import pytest


def validate_html(html: str):
    from tidylib import Tidy

    tidy = Tidy()
    document, errors = tidy.tidy_document(html)
    if errors:
        raise TypeError(errors)


def test_validate_html():
    html = """<!doctype html><html><head><title>Test</title></head><body>This is a test.</body></html>"""
    validate_html(html)

    with pytest.raises(TypeError):
        validate_html("nonsense")


def test_doc():
    """
    https://html.spec.whatwg.org/multipage/syntax.html#the-doctype
    """
    # doctype must be included in generated html,
    # however, we allow Doc to generate fragments as well.
    # Therefore, doctype must be supplied at Doc init for a "full" document.
    from makeweb.html import Doc

    doc = Doc()
    assert str(doc) == ""

    fulldoc = str(Doc("html"))
    assert "<!doctype html>" in fulldoc
    assert '<html lang="en">' in fulldoc
    assert "</html>" in fulldoc

    with pytest.warns(UserWarning):
        Doc(doctype="zing")

    # Language can be supplied as well, default is 'en'.
    mrdoc = str(Doc("html", lang="mr"))
    assert "<!doctype html>" in mrdoc
    assert '<html lang="mr">' in mrdoc


def test_tag_side_by_side():
    from makeweb.html import Doc, h1, div

    doc = Doc()
    h1("Hello, Test")
    div(id="atest")
    assert str(doc) == '<h1>Hello, Test</h1><div id="atest"></div>'


def test_tag_nested():
    from makeweb.html import Doc, h1, div

    doc = Doc()
    div(h1("Hello, Test"), id="atest")
    assert str(doc) == '<div id="atest"><h1>Hello, Test</h1></div>'


def test_tag_validation():
    from makeweb.html import Doc, h1, div

    doc = Doc()
    with pytest.raises(TypeError):
        div(35.2, id="atest")
    div(None)  # is ok, it is skipped from the Doc tree.


def test_tag_context():
    from makeweb.html import Doc, h1, div

    doc = Doc()
    with div(id="atest"):
        h1("Hello, Test")
    assert str(doc) == '<div id="atest"><h1>Hello, Test</h1></div>'


def test_tag_context_2():
    from makeweb.html import Doc, h1, div

    doc = Doc()
    with div(id="atest"):
        h1("Hello, Test")
    h1("Hello, Test")
    assert str(doc) == '<div id="atest"><h1>Hello, Test</h1></div><h1>Hello, Test</h1>'


def test_tag_context_3():
    from makeweb.html import Doc, h1, div

    doc = Doc()
    with div(id="atest"):
        h1("Hello, Test")
    h1("Hello, Test")
    with div():
        h1("Ohai")
    assert (
        str(doc)
        == '<div id="atest"><h1>Hello, Test</h1></div>\
<h1>Hello, Test</h1><div><h1>Ohai</h1></div>'
    )


def test_void_tag():
    from makeweb.html import Doc, img

    doc = Doc()
    img(alt="test")
    assert str(doc) == '<img alt="test" />'


def test_text_tag():
    from makeweb.html import Doc, Text

    doc = Doc()
    Text("Namaskaar!")
    assert str(doc) == "Namaskaar!"


def test_import_deprecated_tag_warning():
    from makeweb.html import Doc, blink

    doc = Doc()

    with pytest.warns(UserWarning):
        blink("this")


def test_import_unknown_tag_warning():
    with pytest.raises(ImportError):
        from makeweb.html import meh


def test_text_escaping():
    pass


def test_html_is_valid():
    pass
