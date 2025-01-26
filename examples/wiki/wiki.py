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
from makeweb import Doc
from makeweb.html import *
from makeweb import CSS

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
}

SEARCH_FRAGMENT_LENGTH = 250

css = CSS()

# Add modern styling
css(
    "*,body",
    margin="0",
    padding="0",
    font_family=(
        "-apple-system, BlinkMacSystemFont, 'Segoe UI', "
        "Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', "
        "'Helvetica Neue', sans-serif"
    ),
    font_size="18px",
    box_sizing="border-box",
    color="#2c3e50",
)

css("html, body", height="100%", background_color="#f5f6fa")

css(
    ".page",
    display="flex",
    flex_direction="column",
    min_height="100vh",
    # Remove max-width
    background_color="white",
    box_shadow="none",  # Remove shadow since it's full width
)

# Add new container class for content
css(
    ".container",
    width="100%",
    max_width="1200px",  # Wider content area
    margin="0 auto",
    padding="0 2rem",  # Add horizontal padding
)

css(
    "nav",
    padding="1rem 0",  # Remove horizontal padding (will be handled by container)
    background_color="white",
    border_bottom="1px solid #eee",
    display="flex",
    justify_content="space_between",
    align_items="center",
)

css(
    "nav .container",
    display="flex",
    justify_content="space-between",
    align_items="center",
    width="100%",
)

css(
    ".nav-left",
    display="flex",
    align_items="center",
)

css(
    ".nav-right",
    margin_left="auto",  # This ensures the search stays on the right
)

css(
    ".navli",
    display="inline-block",
    margin_right="1rem",
)

css(
    "nav a",
    color="#3498db",
    text_decoration="none",
)

css(
    "nav form",
    display="inline-block",
    margin_left="auto",  # This pushes the form to the right
)

css(
    "nav input[type='text']",
    padding="0.5rem",
    border="1px solid #e1e1e1",
    border_radius="0.5rem",
    font_size="0.9rem",
    width="200px",
)

css(
    "nav button",
    padding="0.5rem 1rem",
    background_color="#3498db",
    color="white",
    border="none",
    border_radius="0.5rem",
    margin_left="0.5rem",
    cursor="pointer",
)

css(
    "nav button:hover",
    background_color="#2980b9",
)

css(
    "#content-wrap",
    flex_grow="1",
    padding="2rem 0",  # Remove horizontal padding (will be handled by container)
    animation="fadeIn 0.3s ease-in",
)

css(
    "#topic",
    margin="0 0 1.5rem 0",
    color="#2c3e50",
    font_size="2rem",
)

css(
    ".topic-h1",
    text_decoration="none",
    color="#2c3e50",
)

css(
    "#content-display",
    line_height="1.6",
)

css(
    "#content-box",
    width="100%",
    padding="1rem",
    border="1px solid #e1e1e1",
    border_radius="0.5rem",
    margin_bottom="1rem",
    font_family="inherit",
    resize="vertical",
)

css(
    "#content-save",
    background_color="#3498db",
    color="white",
    border="none",
    padding="0.8rem 1.5rem",
    border_radius="0.5rem",
    cursor="pointer",
    transition="background-color 0.2s ease",
)

css(
    "#content-save:hover",
    background_color="#2980b9",
)

css(
    "#search-results li",
    list_style="none",
    padding="1rem",
    margin_bottom="1rem",
    border_radius="0.5rem",
    background_color="#f8f9fa",
    transition="transform 0.2s ease",
)

css(
    "#search-results li:hover",
    transform="translateX(5px)",
)

css(
    "#query",
    padding="0.8rem 1rem",
    border="1px solid #e1e1e1",
    border_radius="0.5rem",
    margin_right="0.5rem",
    width="300px",
)

css(
    "#footer",
    padding="1rem",
    text_align="center",
    background_color="white",
    border_top="1px solid #eee",
)

css(
    "@keyframes fadeIn",
    _from={"opacity": "0", "transform": "translateY(10px)"},
    _to={"opacity": "1", "transform": "translateY(0)"},
)

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


def render_base(topic, content, create, count, results=False, query=""):
    doc = Doc("html")
    with head():
        meta(charset="utf-8")
        meta(name="viewport", content="width=device-width, initial-scale=1")
        [meta(**{k: v}) for k, v in META.items()]
        title(topic)
        with style():
            css.embed()
    with body():
        with div(cls="page"):
            render_nav(doc, query)  # Pass query to render_nav
            with div(cls="container"):  # Add container
                with div(id="content-wrap"):
                    render_content(doc, topic, content, create, results)
            render_footer(doc, count)
    return str(doc)


# Not *too* bad, eh?
# Let us define the three render_... functions required by render_base().


def render_nav(doc, query=""):  # Add query parameter
    with nav():
        with div(cls="container"):  # Add container
            with div(cls="nav-left"):
                [li(a(k, href=v), cls="navli") for k, v in NAV.items()]
            with div(cls="nav-right"):
                with form(action="/search", method="post"):
                    _input(
                        type="text", name="query", value=query, placeholder="Search..."
                    )


def render_content(doc, topic, content, create, results):
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


def render_footer(doc, count):
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
    return Response(
        render_base(topic, content, create, count, results=True, query=query)
    )


@app.route("/search/<query>")
def search_manual(query):
    topic = "Results for {}".format(query)
    results = search_topics(query)
    content = render_search_results(query, results)
    create = False
    count = count_topics()
    return Response(
        render_base(topic, content, create, count, results=True, query=query)
    )


# Configure Flask's static route handler for css.

app.static_folder = STATIC_DIR
app.static_url_path = "/static"

##### run()

# Hooray, we made it this far!

app.run(debug=True, use_reloader=True)
