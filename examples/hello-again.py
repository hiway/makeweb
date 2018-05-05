#!/usr/bin/env python
#
# hello-again.py
#
#
# We will use Flask, a brilliantly simple web framework
# to serve our generated html.
from flask import Flask, Response

# Import Doc and two html elements from makeweb.
from makeweb import Doc, body, h1

# MakeWeb uses Python's dynamic capabilities
# to perform interesting tricks.
#
# First trick is that none of these tags actually
# exist as defined objects in the library,
# they are created as partial functions**
# to initialize Tag class with the name of the tag set.
# Part two of first trick is when you call the function
# such as h1(), it actually initiaizes the class
# at this point with your text and attributes set.
#
# Second trick is during the initialization of Tag,
# it reaches backwards in the call-stack
# and retrieves the `doc` variable set in the caller (your) function.
# This allows us to write h1("awesome") instead of doc.h1("awesome").
#
# Third trick is using the `with` context blocks
# to automatically enclose tags defined within the context.
# The context manager uses the second trick as well.
#
# Fourth is that there is no doc.render() function to call.
# Python gives us useful primitives such as __str__() methods,
# we abuse this feature enthusiastically in the library.
#
# ** partial function is a feature that allows us
#   to prepare a function with some of its arguments set in advance
#   and call it later with rest of the arguments.
#   see: https://docs.python.org/3/library/functools.html

# Create an instance of Flask app.
app = Flask(__name__)


# Three rules for using MakeWeb successfully:
#   - Always work with Doc and tags inside a function.
#   - `doc = Doc()` before calling any tags.
#   - `with` is your friend, so are function calls that look like tags.

# Set up a route
@app.route('/')
def index():
    # First, define a variable named `doc` as an  instance of `Doc`.
    # (it is important, MakeWeb will fail if you call a tag
    # before defining a doc first).
    doc = Doc('html')
    # We also pass doctype='html' to tell Doc that
    # this is a complete html document
    # and we expect <!doctype html> and <html>, </html> tags
    # around the tags we define.
    # Omitting doctype will give us an html fragment,
    # more on it in later examples.

    # Create an h1 tag inside body.
    with body():
        h1('Hello, World Wide Web!')

    # Render the doc by calling str() on it
    # and return the generated html to browser.
    return Response(str(doc))


# Run our app in debug mode.
app.run(debug=True, use_reloader=True)
