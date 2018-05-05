from flask import Flask, Response
from makeweb import (
    Doc, CSS, JS,
    head, title, style, script,
    body, h1, button,
)

app = Flask(__name__)
css = CSS()
js = JS()

css('*,body',   # <- add CSS to taste.
    font__family='sans-serif',
    text__align='center')
css('h1', color="darkblue")


@js.function  # <- mark say_hello() as a javascript function.
def say_hello():
    hello_box = document.getElementById("hello_box")
    hello_box.innerHTML = "Hello, World Wide Web!"


@app.route('/')
def index():
    doc = Doc('html')  # <-- html generation starts here...
    with head():
        title('Hello')
        with style():
            css.embed()
    with body():
        h1('...', id='hello_box')
        button('Hello', onclick="say_hello()")  # <-- hook up say_hello().
        with script():
            js.embed()
    return Response(str(doc))  # <-- ...and ends here.


app.run(debug=True, use_reloader=True)
