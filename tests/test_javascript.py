import pytest
from makeweb import JS
from makeweb.html import Doc, script


def test_js_function():
    js = JS()

    @js.function
    def test():
        alert("wut?")

    assert str(js) == 'function test(){alert("wut?");}'


def test_js_with_params():
    js = JS()

    @js.function
    def greet(name, age):
        console.log("Hello " + name + ", you are " + str(age) + " years old!")

    assert (
        str(js)
        == 'function greet(name,age){console.log((((("Hello "+name)+", you are ")+age.toString())+" years old!"));}'
    )


def test_js_multiple_functions():
    js = JS()

    @js.function
    def func1():
        return 42

    @js.function
    def func2():
        return "hello"

    assert str(js) == 'function func1(){return 42;}function func2(){return"hello";}'


def test_js_script():
    js = JS()

    @js.script
    def test():
        alert("wut?")

    assert str(js) == 'alert("wut?");'


def test_js_function_embed():
    js = JS()

    @js.function
    def test():
        alert("wut?")

    doc = Doc()
    with script():
        js.embed()
    assert str(doc) == '<script>function test(){alert("wut?");}</script>'


def test_js_script_embed():
    js = JS()

    @js.script
    def test():
        alert("wut?")

    doc = Doc()
    with script():
        js.embed()
    assert str(doc) == '<script>alert("wut?");</script>'


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


def test_js_no_minify():
    js = JS(minify=False)

    @js.function
    def test():
        x = 1
        y = 2
        return x + y

    assert (
        str(js)
        == """\
function test() {
    var x, y;
    x = 1;
    y = 2;
    return (x + y);
}
"""
    )
