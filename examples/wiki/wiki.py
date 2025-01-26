#!/usr/bin/env python
#
# wiki.py
#
#
# In this example,
# we will build a tiny wiki engine that can perform these functions:
#
#     - Create "topics", each page will be referred to by its topic.
#     - URL structure is: example.com/TOPIC
#     - Topic must be a single word, underscores are okay.
#     - Render content from markdown to html.
#     - Display content if topic exists.
#     - Display creation form if topic does not exist.
#     - Save and redirect to newly created topic.
#     - Search, get results, click-through to topics.
#     - Display topic count in footer.
#
# The structure of the file is highlighted by comments that start with 5 #s.
#
#     - Imports
#     - Defaults
#     - Initialize long-running objects
#     - Define external-api wrappers
#     - Define template functions
#     - Define route handlers
#     - Call run()
#
# Note that there are three sections that define functions of some sort.
# These three layers allow us to keep the code modular and easy to understand.
#
# You may also notice that there is no style defined using Python code
# in this example - as an illustration that when your project either
# needs better tools or you are collaborating with someone
# who speaks CSS natively.
# In such cases you can fallback to the usual methods -
# write/generate a CSS file and serve it through your framework.
#
# If you have not seen `hello-again.py`, now is a good time.
#
# Let's dig in!

##### Imports

# from Python standard library
import os
import re

# Markdown rendering is done by the dead-simple `markdown` library.
# Run `pip install markdown` to install Markdown.
import markdown

# Flask is a brilliantly simple framework that lets us serve the http protocol.
# Run `pip install flask` to install Flask.
from flask import Flask, Response, request, redirect

import sqlite3

# Makeweb, it a me!
#  Run `pip install makeweb` to install MakeWeb.
from makeweb.html import (
    # First, the HTML Document class...
    Doc,
    # Then tags needed to build the `head` section.
    head,
    title,
    meta,
    link,
    # Commonly used tags for the `body` section.
    body,
    nav,
    hr,
    div,
    ul,
    li,
    a,
    # Tags for content.
    h1,
    h3,
    h5,
    p,
    # Tags for forms. Since `input` is a Python built-in name,
    # we can avoid clashes by importing with an underscore before its name.
    form,
    _input,
    textarea,
    button,
)

# And that concludes our imports!
#
# Quick reminder of the three rules for using MakeWeb successfully:
#   - Always work with Doc and tags inside a function.
#   - `doc = Doc()` before calling any tags.
#   - `with` is your friend, so are function calls that look like tags.

##### Defaults

# Get current path as base.
BASE_DIR = os.path.abspath(".")

# Use 'static' directory under base to serve css.
STATIC_DIR = os.path.join(BASE_DIR, "static/")

DB_PATH = os.path.join(BASE_DIR, "wiki.db")

# Setting HTML META tags here, keeps code uncluttered when there are many.
META = {
    "viewport": "width=device-width, initial-scale=1",
}

# Since we need a topic, any topic to begin with,
# let us get creative and use...
TOPIC = "home"

# Also define the navigation urls we want to display.
NAV = {
    "Home": "/",
    "Search": "/search",
}

SEARCH_FRAGMENT_LENGTH = 250

##### Initialize long-running objects

# We are going to need only one each of these Python objects,
# and we need some of them, such as `app`, to build rest of our code.
# Let us define them early.

# A Flask app, that will let us define route handlers
# and run the code as a server.
app = Flask(__name__)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS topics
                 (topic text PRIMARY KEY, content text)"""
    )
    conn.commit()
    conn.close()


# Initialize the database
init_db()


# Helper function to get database connection
def get_db():
    return sqlite3.connect(DB_PATH)


##### Define api wrappers


def count_topics():
    with get_db() as db:
        count = db.execute("SELECT COUNT(*) FROM topics").fetchone()[0]
    return count


def create_topic(topic, content):
    with get_db() as db:
        db.execute(
            "INSERT INTO topics (topic, content) VALUES (?, ?)",
            (topic.lower(), content),
        )
        db.commit()


def fetch_topic(topic):
    with get_db() as db:
        result = db.execute(
            "SELECT topic, content FROM topics WHERE topic = ?", (topic.lower(),)
        ).fetchone()
    return {result[0]: result[1]} if result else {}


def search_topics(query):
    results = {}
    query_words = set(query.lower().split()) - {"and", "or", "the", "a", "an"}

    with get_db() as db:
        for word in query_words:
            word_pattern = f"%{word}%"
            rows = db.execute(
                """SELECT topic, content FROM topics 
                               WHERE topic LIKE ? OR content LIKE ?""",
                (word_pattern, word_pattern),
            ).fetchall()
            for topic, content in rows:
                if topic not in results:
                    content = (
                        content[:SEARCH_FRAGMENT_LENGTH]
                        if len(content) > SEARCH_FRAGMENT_LENGTH
                        else content
                    )
                    results[topic] = content
    return results


def save_topic(topic, content):
    with get_db() as db:
        db.execute(
            """INSERT INTO topics (topic, content) VALUES (?, ?)
                     ON CONFLICT(topic) DO UPDATE SET content = ?""",
            (topic.lower(), content, content),
        )
        db.commit()


def delete_topic(topic):
    with get_db() as db:
        db.execute("DELETE FROM topics WHERE topic = ?", (topic.lower(),))
        db.commit()


##### Define template functions

# Generally you would write a template with some templating language
# helping you glue pieces of html together.
# MakeWeb helps you write html (and even css and js!)
# in a familiar python syntax.
#
# Here we define a render_base() template that will take in a few variables
# and render an html document out of those.
# We will split up specific sections of the template into separate functions.
# For our tiny wiki, a single page is sufficient.


def render_base(topic, content, create, count, results=False):
    # First, define a variable named `doc` as an  instance of `Doc`.
    # (it is important, MakeWeb will fail if you call a tag
    # before defining a doc first).
    doc = Doc("html")
    # With that in place, we can now generate our document structure.
    with head():
        meta(charset="utf-8")  # Define charset first.
        [meta(**{k: v}) for k, v in META.items()]  # Works with comprehensions.
        title(topic)  # Title is required for valid html.

        ## Uncomment the following line to apply a basic style.
        # link(href='/static/normalize.css', _type='text/css', rel='stylesheet')

        ## Try another, richer stylesheet? (source/credit at top of each file)
        ## Uncomment only one of these lines (or normalize.css) at a time.
        # link(href='/static/retro.css', _type='text/css', rel='stylesheet')
        # link(href='/static/air.css', _type='text/css', rel='stylesheet')
        # link(href='/static/ghpandoc.css', _type='text/css', rel='stylesheet')
        # link(href='/static/markdown.css', _type='text/css', rel='stylesheet')

        # Bare-minimum style tweaks.
        link(href="/static/app.css", _type="text/css", rel="stylesheet")
    with body(cls="markdown"):
        # Break apart pieces of template using familiarity of functions.
        # We pass `doc` to a template function that will modify
        # the `doc` we are refering to in render_base(), in place.
        render_nav(doc)
        # Higher-level structure stays within base template.
        with div(id="content-wrap"):
            # Pass in any variables along with doc
            # needed to render the template.
            render_content(doc, topic, content, create, results)
        # And now for something completely different...
        # Let us work with better isolation within the templates.
        # Below, we build a separate `doc` within render_footer()
        # and plug in the generated html straight into a div.
        # Doing so allows greater control over the overall layout from base.
        div(render_footer(count), id="footer")
    # We return rendered html by calling `str(doc)`.
    # `doc` is no longer in scope and will be removed from memory automatically.
    return str(doc)


# Not *too* bad, eh?
# Let us define the three render_... functions required by render_base().


def render_nav(doc):
    with nav():
        [li(a(k, href=v), cls="navli") for k, v in NAV.items()]


def render_content(doc, topic, content, create, results):
    hr()
    if results:  # Don't link "Results for..."
        h1(topic, id="topic")
    elif create:  # When editing, clicking on topic h1 cancels edit operation.
        a(h1(topic, id="topic"), href="/{}".format(topic), cls="topic-h1")
    else:  # When viewing, clicking on topic h1 opens edit form.
        a(h1(topic, id="topic"), href="/{}/edit".format(topic), cls="topic-h1")
    if create:
        div(render_content_form(topic, content), id="content-edit")
    else:
        div(render_markdown(str(content)), id="content-display")


def render_footer(count):
    # Isolated fragments of doc are great for testing!
    doc = Doc()  # Note the missing doctype 'html', we skip it for fragments.
    hr()
    p(
        "{} topic{} in wiki.".format(count, "" if count == 1 else "s"),
        cls="footer-stats",
    )
    return doc


# Almost there, two more template fragment functions
# needed by render_content(), let us define that too.


def render_markdown(content):
    content = re.sub(r"\[\[(\w+)\]\]", r'<a href="/\1">\1<a>', content)
    return markdown.markdown(content)


def render_content_form(topic, content):
    doc = Doc()
    with form(action="/save", method="post"):
        _input(id="topic-box", name="topic", value=topic, hidden=True)
        div(textarea(content, rows=10, cols=35, name="content", id="content-box"))
        button("Save", id="content-save")
    return doc


# Good time to check if we missed something in the features list.
# Oh, a fragment for search results!


def render_search_results(query, results):
    doc = Doc()
    h3(render_search_form(query))
    with ul(id="search-results"):
        for topic, content in results.items():
            with li():
                h5(a(topic, href="/{}".format(topic)))
                p(content)
    return doc


# Aha, one more left, needed by render_search_results().


def render_search_form(query):
    doc = Doc()
    with form(action="/search", method="post"):
        _input(id="query", name="query", value=query)
        button("Search")
    return doc


# Aaaand we're done with the templates.
# Now on to the next section...

##### Define route handlers

# Until now, we were not restricted by any web framework.
# Beyond this point, we use Flask to do something
# with the html that we are now able to generate with MakeWeb.
#
# As a bonus, since we wrote the templates
# without any direct calls to database (or network),
# we get full control over the I/O in the request handler.
#
# Aside:
#   Quart is a superb project that implements the Flask API
#   for python's async/await syntax. If you were to use Quart
#   instead of Flask, you could asynchronously wait,
#   say, on remote database I/O,
#   within the handler before returning the generated html.
#   A single Quart app can handle many simultaneous connections,
#   and it supports http2 and websockets out of the box!


@app.route("/")
def home():
    topic = TOPIC
    content = fetch_topic(topic).get(topic) or ""
    create = False if content else True
    count = count_topics()
    return Response(render_base(topic, content, create, count))


@app.route("/save", methods=["post"])
def save():
    topic = request.form.get("topic")
    content = request.form.get("content")
    save_topic(topic, content)
    return redirect("/{}".format(topic))


@app.route("/<topic>")
def topic_page(topic):
    content = fetch_topic(topic).get(topic) or ""
    create = False if content else True
    count = count_topics()
    return Response(render_base(topic, content, create, count))


@app.route("/<topic>/edit")
def topic_edit(topic):
    content = fetch_topic(topic).get(topic) or ""
    create = True
    count = count_topics()
    return Response(render_base(topic, content, create, count))


@app.route("/search")
def search_form():
    topic = "Search"
    content = render_search_form("")
    create = False
    count = count_topics()
    return Response(render_base(topic, content, create, count, results=True))


@app.route("/search", methods=["post"])
def search_post():
    query = request.form.get("query") or ""
    topic = "Results for {}".format(query)
    results = search_topics(query)
    content = render_search_results(query, results)
    create = False
    count = count_topics()
    return Response(render_base(topic, content, create, count, results=True))


@app.route("/search/<query>")
def search_manual(query):
    topic = "Results for {}".format(query)
    results = search_topics(query)
    content = render_search_results(query, results)
    create = False
    count = count_topics()
    return Response(render_base(topic, content, create, count, results=True))


# Configure Flask's static route handler for css.

app.static_folder = STATIC_DIR
app.static_url_path = "/static"

##### run()

# Hooray, we made it this far!

app.run(debug=True, use_reloader=True)
