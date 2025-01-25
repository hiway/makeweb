import pytest
from makeweb import defaults, fix_attribute, get_local_variable_from_caller


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


def test_defaults():
    assert defaults.remove_first_underscore is True
    assert defaults.replace_single_underscore is True
    assert defaults.replace_double_underscore is True
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


def test_fix_attribute():
    assert fix_attribute("cls") == "class"
    assert fix_attribute("className") == "class"
    assert fix_attribute("_class") == "class"
    assert fix_attribute("_input") == "input"
    assert fix_attribute("left__align") == "left-align"
    assert fix_attribute("__moz__column__count") == "-moz-column-count"
    assert fix_attribute("snake_case") == "snake-case"

    defaults.replace_double_underscore = False
    assert fix_attribute("__keep_one") == "-keep-one"

    defaults.replace_double_underscore = True  # reset
    defaults.replace_single_underscore = True
    assert fix_attribute("__example_attr") == "-example-attr"

    defaults.replace_double_underscore = False
    defaults.replace_single_underscore = True
    assert fix_attribute("__example_attr") == "-example-attr"

    defaults.remove_first_underscore = False
    defaults.replace_double_underscore = False
    defaults.replace_single_underscore = True
    assert fix_attribute("__example_attr") == "--example-attr"

    with pytest.raises(TypeError):
        fix_attribute(808)

    # Test single underscore replacement
    defaults.replace_single_underscore = True
    assert fix_attribute("data_type") == "data-type"
    assert fix_attribute("aria_label") == "aria-label"

    defaults.replace_single_underscore = False
    assert fix_attribute("data_type") == "data_type"
    assert fix_attribute("aria_label") == "aria_label"

    # Reset to default
    defaults.replace_single_underscore = True


def test_get_local_variable_from_caller_level_1():
    from makeweb.html import Doc

    def caller_func():
        doc = Doc(doctype="html")
        test_magic()

    def test_magic():
        doc = get_local_variable_from_caller("doc", Doc)
        assert "html" in str(doc)
        with pytest.raises(LookupError):
            get_local_variable_from_caller("zoop", Doc)
        with pytest.raises(TypeError):
            get_local_variable_from_caller("doc", float)

    caller_func()


def test_get_local_variable_from_caller_level_2():
    from makeweb.html import Doc

    def caller_func():
        doc = Doc(doctype="html")
        second_caller()

    def second_caller():
        test_magic()

    def test_magic():
        doc = get_local_variable_from_caller("doc", Doc)
        assert "html" in str(doc)
        with pytest.raises(LookupError):
            get_local_variable_from_caller("zoop", Doc)
        with pytest.raises(TypeError):
            get_local_variable_from_caller("doc", float)

    caller_func()


def test_get_local_variable_from_caller_level_3():
    from makeweb.html import Doc

    def caller_func():
        doc = Doc(doctype="html")
        second_caller()

    def second_caller():
        [test_magic() for x in [0, 1]]

    def test_magic():
        doc = get_local_variable_from_caller("doc", Doc)
        assert "html" in str(doc)

    caller_func()


def test_get_local_variable_from_caller_level_4():
    from makeweb.html import Doc

    def caller_func():
        second_caller()  # Note: doc is not defined here

    def second_caller():
        third_caller()

    def third_caller():
        test_magic()

    def test_magic():
        with pytest.raises(LookupError):
            # This should fail because doc is not defined in any parent frame
            doc = get_local_variable_from_caller("doc", Doc)

    caller_func()


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


def test_css():
    from makeweb import CSS

    css = CSS()
    css("body", background_color="black", color="green")
    assert str(css) == "body{background-color:black;color:green}"
    css(".main li", __webkit__filter="blur(1px)")
    assert (
        str(css)
        == "body{background-color:black;color:green}\
.main li{--webkit--filter:blur(1px)}"
    )


def test_css_embed():
    from makeweb import CSS, Doc
    from makeweb.html import style

    css = CSS()
    css("body", background_color="black", color="green")
    doc = Doc()
    with style():
        css.embed()
    assert str(doc) == "<style>body{background-color:black;color:green}</style>"


def test_js_function():
    from makeweb import JS

    js = JS()

    @js.function
    def test():
        alert("wut?")

    assert str(js) == 'function test(){alert("wut?");}'


def test_js_with_params():
    from makeweb import JS

    js = JS()

    @js.function
    def greet(name, age):
        console.log("Hello " + name + ", you are " + str(age) + " years old!")

    assert (
        str(js)
        == 'function greet(name,age){console.log((((("Hello "+name)+", you are ")+age.toString())+" years old!"));}'
    )


def test_js_multiple_functions():
    from makeweb import JS

    js = JS()

    @js.function
    def func1():
        return 42

    @js.function
    def func2():
        return "hello"

    assert str(js) == 'function func1(){return 42;}function func2(){return"hello";}'


def test_js_script():
    from makeweb import JS

    js = JS()

    @js.script
    def test():
        alert("wut?")

    assert str(js) == 'alert("wut?");'


def test_js_function_embed():
    from makeweb import JS, Doc
    from makeweb.html import script

    js = JS()

    @js.function
    def test():
        alert("wut?")

    doc = Doc()
    with script():
        js.embed()
    assert str(doc) == '<script>function test(){alert("wut?");}</script>'


def test_js_script_embed():
    from makeweb import JS, Doc
    from makeweb.html import script

    js = JS()

    @js.script
    def test():
        alert("wut?")

    doc = Doc()
    with script():
        js.embed()
    assert str(doc) == '<script>alert("wut?");</script>'


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


def test_javascript_dummy_objects():
    from makeweb.javascript import document, WebSocket, window, console

    # Test that dummy JavaScript objects are created on demand
    assert document is not None
    assert isinstance(document, object)
    assert WebSocket is not None
    assert isinstance(WebSocket, object)
    assert window is not None
    assert isinstance(window, object)
    assert console is not None
    assert isinstance(console, object)
