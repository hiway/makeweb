# MakeWeb

Make interactive web apps using good ol' HTML, CSS
and a sprinkling of JavaScript — in Python.

## Examples

### HyperText Markup Lnguage

If we run this script:

```python
# 00-generate-html.py

from makeweb import Doc, body, h1

def generate_html():
    doc = Doc('html', lang='mr')
    with body():
        h1('हा!')
    return str(doc)

print(generate_html())
```

We should see this output on the screen:

```html
<!doctype html>
<html lang="mr">
<body>
  <h1>हा!</h1>
</body>
</html>
```

*(Whitespace added for clarity.)*

Ha! HTML was easy, let us generate CSS from Python code.

### Cascading Style Sheets

```python
# 01-generate-css.py

from makeweb import CSS

css = CSS()

css('body', background='white', color='#222')
css('h1', color='darkorange', margin__top='1em')

print(str(css))
```

Running the above example we see...

```css
body{
  background:white;
  color:#222
}
h1{
  color:darkorange;
  margin-top:1em
}
```

*(Whitespace added for clarity.)*

Notice that the double underscore in `css('h1', margin__top='1em')`
gets converted to hyphen in CSS as `h1{margin-top:1em}`.
This pattern is used throughout the library for HTML and CSS attributes.

So... CSS is even easier?!
How about something more ambitious?

### JavaScript

```python
# 02-generate-js.py

from makeweb import JS

js = JS()

@js.function
def say_hello():
    hello_box = document.getElementById("hello_box")
    hello_box.innerHTML = "Hello, World Wide Web!"

print(str(js))
```

And we get a JavaScript function out!

```javascript
function say_hello(){
  var hello_box;
  hello_box=document.getElementById("hello_box");
  hello_box.innerHTML="Hello, World Wide Web!";
}
```

*(Whitespace added for clarity.)*

Now let us use these capabilities together!

### App

```python
# hello-readme.py

from flask import Flask, Response
from makeweb import (
    Doc, CSS, JS,
    head, title, style, script,
    body, h1, button,
)

# We'll use Flask to serve, you could use any other framework 
# or save as static files, or anything else 
# that you wish to do with generated html.
app = Flask(__name__)  
css = CSS()
js = JS()

css('*,body',   # <-- Add CSS to taste.
    font__family='sans-serif',
    text__align='center')
css('h1', color="darkblue")  


@js.function  # <-- A sprinkling of JavaScript. Look ma, no braces!
def say_hello():
    hello_box = document.getElementById("hello_box")
    hello_box.innerHTML = "Hello, World Wide Web!"


@app.route('/')
def index():
    doc = Doc('html')  # <-- Generate all the HTML your app (really) needs.
    with head():
        title('Hello')
        with style():  # Embed CSS.
            css.embed()
    with body():
        h1('...', id='hello_box')  # Set attributes. 
        button('Hello', onclick="say_hello()")  # <-- hook up say_hello().
        with script():  # Embed JavaScript.
            js.embed()
    return Response(str(doc))  # <-- Serve all the awesome your users desire!


app.run()  # <-- It is time! 
```

This app transfers ~550 bytes over the network in order to run successfully,
that is including the HTTP headers overhead.
You read that right, not even one kilobyte!
The web technologies are quite simple and straightforward for general use,
and very flexible, robust and powerful too!

You might not need (or want the baggage of) complex tooling
for a small project.
It could be a one time make-and-forget tool at work
or a weekend hobby project,
or maybe something even larger if you really like this way of working.
MakeWeb can come in handy because it makes it almost trivial
to build the web like it was intended,
straight from your Python code.

Wait, somebody mentioned single-page-apps?
How about single source-file apps
that don't download half the internet to work? 😂
Kidding, this is a very, very barebones system,
and therefore you can use any existing stylesheets
or JS libraries alongside MakeWeb.

> Check out examples for more demos!

## Install

### Using Poetry (Recommended)

```shell
# Clone the repository
git clone https://github.com/hiway/makeweb.git
cd makeweb

# Install poetry if you haven't already
pip install poetry

# Install makeweb with JS support
poetry install --with js

# For development
poetry install --with dev

# For running examples
poetry install --with examples

# For everything
poetry install --with dev,js,examples
```

### Using pip (Legacy)

#### Stable

```shell
python3 -m venv makeweb
source makeweb/bin/activate
pip install makeweb[js]
```

#### Current

```shell
python3 -m venv makeweb
source makeweb/bin/activate
git clone https://github.com/hiway/makeweb.git
cd makeweb
pip install -e .[examples]
```

#### Development

```shell
python3 -m venv makeweb
source makeweb/bin/activate
git clone https://github.com/hiway/makeweb.git
cd makeweb
pip install -e .[dev]
```

- libtidy-dev

#### Test

```console
pytest tests.py
```

With coverage:

```console
pytest --cov=makeweb --cov-report=term tests.py
```
