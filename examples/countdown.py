#!/usr/bin/env python
#
# countdown.py
#
#
# If you checked out hello.py (and hopefully hello-again.py),
# and liked what you saw,
# then it is time to exercise our new-found MakeWeb muscles!
#
# Btw, have you read about the Year 2038 problem?
#
# If not, now is a great moment to check it out:
#   - https://en.wikipedia.org/wiki/Year_2038_problem
#
# Here's an excerpt from the Wikipedia page:
#
# > The latest time that can be represented in Unix's signed 32-bit integer
# > time format is 03:14:07 UTC on Tuesday, 19 January 2038
# > (231-1 = 2,147,483,647 seconds after 1 January 1970).
# > Times beyond that will wrap around and be stored internally
# > as a negative number, which these systems will interpret as having occurred
# > on 13 December 1901 rather than 19 January 2038.
# > This is caused by integer overflow.
# > The counter runs out of usable digit bits, flips the sign bit instead,
# > and reports a maximally negative number (continuing to count up,
# > toward zero).
# > Resulting erroneous calculations on such systems are
# > likely to cause problems for users and other relying parties.
#
# > Programs that work with future dates will begin to run into problems sooner;
# > for example a program that works with dates 20 years in the future
# > would have to have been fixed no later than 19 January 2018.
#
# Since this is being written in 2018,
# how about we make a countdown timer to this event to demonstrate MakeWeb's
# CSS and JavaScript abilities?
#
# CSS support is built-in to MakeWeb, and lets you write
# css stylesheets as simply as html (as shown in previous examples).
#
# MakeWeb uses the ridiculously straightforward
# python-to-javascript translation library Javascripthon
# to support writing JS functions in Python syntax,
# inline with your server-side python code.
# In this beginner-level example, we will keep the js limited
# to a single library initialization call.
#
# Watch this!
#

from flask import Flask, Response

# Import Doc, CSS, JS along with the tags.
from makeweb import (
    Doc,
    CSS,
    JS,
)
from makeweb.html import (
    head,
    title,
    style,
    script,
    body,
    div,
    a,
    span,
    i,
)
from makeweb.javascript import TimezZ

# Initialize app, css and js.
app = Flask(__name__)
css = CSS()
js = JS()

# Let us define some style for our page and clock.
#
# If you know css, this should look familiar.
# Note that we use double-underscore where a hyphen is expected,
# since python does not allow hyphens in identifiers.
#
# Internals: MakeWeb's css support works with python's __call__() feature.


css(
    "body",
    background__color="#102719",
    color="#93ff45",
    font__family="roboto-mono,monospace",
    text__align="center",
    background="repeating-linear-gradient(0deg,#102719,\
    #100019 3px,\
    #0f1009 3px,\
    #0a2019 3px,\
    #0f1f09 3px,\
    #102719 10px);",
    background__size="100% 50px",
)

css(
    ".timer",
    width="100%",
    font__size="3.4em",
    margin__top="3em",
    __webkit__filter="blur(0.6px)",
    filter="blur(0.6px)",
)

css(".timer span i", color="#93aa22")

css(
    ".legend-wrap",
    width="100%",
    margin__top="1em",
    __webkit__filter="blur(0.2px)",
    filter="blur(0.2px)",
)

css("a", color="#93cc45", font__size="1.3em", text__decoration="none")


# We are going to cheat a little and use an existing library
# for the countdown timer.
# However, the function defined below is translated to javascript
# and called through `body(onload='start_timer()')` further down.
#
# Check out TimezZ library that powers the timer:
#   - https://github.com/BrooonS/TimezZ


@js.function
def start_timer():
    TimezZ(
        ".j-timer",
        {
            "date": "January 19, 2038 03:14:07",
            "daysName": "days",
            "hoursName": "h",
            "minutesName": "m",
            "secondsName": "s",
            "isStop": False,
            "template": "<span>NUMBER<i>LETTER</i></span> ",
        },
    )


# Render the initial timer widget as TimezZ does once it is initialized.


def render_initial_timer(days, hours, minutes, seconds):
    doc = Doc()
    with span(days):
        i("days ")
    with span(hours):
        i("h ")
    with span(minutes):
        i("m ")
    with span(seconds):
        i("s ")
    return str(doc)


# Finally, we define a single route handler for '/'.
# In the handler, we create a doc, embed css and js in appropriate places,
# and include the external js library.
# While embedding css or js, we use the style() or script() context block.


@app.route("/")
def index():
    doc = Doc("html")
    with head():
        title("Year 2038 problem")
        with style():
            css.embed()
    with body(onload="start_timer()"):
        # Exercise: calculate these numbers in advance, in Python,
        # and fill them in, letting the page be useful
        # even if a user has disabled JS
        # (with adtech giving us many good reasons to do so!).
        # As a rule, even in 2018, do not assume JS is available by default.
        div(
            render_initial_timer(days="0000", hours="00", minutes="00", seconds="00"),
            cls="timer j-timer",
        )
        div(
            a(
                "to January 19, 2038 03:14:07",
                href="https://en.wikipedia.org/wiki/Year_2038_problem",
            ),
            cls="legend-wrap",
        )
        script(src="/static/timezz.js")
        with script():  # You can comment out this block
            js.embed()  # to test render_initial_timer()
    return Response(str(doc))


# Alright, we can now run this app and watch time ticking by to clock-doom!
#
# Psst, if you missed it on the Wikipedia page, here's some good news:
#
# > Most operating systems designed to run on 64-bit hardware already use
# > signed 64-bit time_t integers. Using a signed 64-bit value introduces
# > a new wraparound date that is over twenty times greater than
# > the estimated age of the universe:
# > approximately 292 billion years from now,
# > at 15:30:08 UTC on Sunday, 4 December 292,277,026,596.

# Let's get this started!

app.run(debug=True, use_reloader=True)
