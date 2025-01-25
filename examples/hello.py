#!/usr/bin/env python
#
# hello.py
#
#
# !!! See hello-again.py for the commented version.
#
from flask import Flask, Response
from makeweb.html import Doc, body, h1

app = Flask(__name__)


@app.route("/")
def index():
    doc = Doc("html")
    with body():
        h1("Hello, World Wide Web!")
    return Response(str(doc))


app.run(debug=True, use_reloader=True)
