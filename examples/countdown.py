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

from quart import Quart, Response
from datetime import datetime
import asyncio
import json

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
    meta,  # Add meta to imports
)
from makeweb.javascript import TimezZ, EventSource, document, console, JSON

# Initialize app with Quart instead of Flask
app = Quart(__name__)
css = CSS()
js = JS()

# Update CSS styles for modern design
css(
    ":root",
    **{
        "--bg-primary": "#0f172a",
        "--text-primary": "#f8fafc",
        "--accent": "#3b82f6",
        "--glass-bg": "rgba(255, 255, 255, 0.03)",
        "--spacing-base": "1rem",
        "--font-size-base": "16px",
    },
)
css(
    "*",
    **{
        "box-sizing": "border-box",
    },
)

css(
    "body",
    background_color="var(--bg-primary)",
    color="var(--text-primary)",
    font_family=(
        "ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "
        "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    ),
    text_align="center",
    background="linear-gradient(145deg, var(--accent) 0%, var(--bg-primary) 100%)",
    min_height="100vh",
    display="flex",
    align_items="center",
    justify_content="center",
    margin="0",
    padding="var(--spacing-base)",
    font_size="var(--font-size-base)",
)

css(
    ".container",
    display="flex",
    flex_direction="column",
    align_items="center",
    gap="var(--spacing-base)",
    width="100%",
    max_width="400px",
    margin="0 auto",
    padding="var(--spacing-base)",
)

css(
    ".timer",
    background_color="var(--glass-bg)",
    backdrop_filter="blur(8px)",
    border_radius="16px",
    padding="1.5rem 1rem",
    box_shadow="0 4px 16px rgba(0, 0, 0, 0.1)",
    border="1px solid rgba(255, 255, 255, 0.05)",
    width="100%",
    max_width="400px",
)

css(
    ".timer span",
    display="inline-flex",
    flex_direction="column",
    align_items="center",
    margin="0 0.5rem",
    font_size="2rem",  # Base size for mobile
    font_weight="700",
    text_shadow="0 1px 4px rgba(0, 0, 0, 0.2)",
)

css(
    ".timer span i",
    font_size="0.8rem",
    font_weight="500",
    color="var(--text-primary)",
    opacity="0.8",
    font_style="normal",
    margin_top="0.25rem",
    text_transform="uppercase",
    letter_spacing="0.05em",
)

css(
    ".description",
    width="100%",
    padding="1rem",
    background_color="var(--glass-bg)",
    backdrop_filter="blur(8px)",
    border_radius="16px",
    margin_top="1rem",
)

css(
    "a",
    color="var(--text-primary)",
    font_size="1rem",
    text_decoration="none",
    transition="all 0.3s ease",
    display="block",
    touch_action="manipulation",
    width="100%",
    text_align="center",
)
# Update bit visualization CSS to fix mobile centering
css(
    ".bit-viz",
    width="100%",
    max_width="900px",  # Add max-width to match container
    padding="1.5rem 1rem",
    # background_color="var(--glass-bg)",
    backdrop_filter="blur(8px)",
    border_radius="16px",
    # border="1px solid rgba(255, 255, 255, 0.05)",
    margin_top="1rem",
    font_family="monospace",
    display="flex",
    flex_direction="column",
    gap="0.5rem",  # Reduce gap between bytes
    align_items="center",
)

css(
    ".byte-group",
    display="flex",
    gap="1px",  # Reduce gap between bits
    padding="0.25rem",
    justify_content="center",
    width="auto",  # Change from 100% to auto
)

css(
    ".bit",
    width="16px",  # Make bits slightly smaller
    height="16px",
    display="inline-flex",
    align_items="center",
    justify_content="center",
    border_radius="3px",
    font_size="0.7rem",  # Slightly smaller font
    font_weight="bold",
    background_color="rgba(255, 255, 255, 0.05)",
    transition="all 0.3s ease",
    color="rgba(255, 255, 255, 0.5)",
)

# Add CSS for active bits after existing .bit CSS
css(
    ".bit.active",
    background_color="var(--accent)",
    color="var(--text-primary)",  # Make active digits fully visible
    box_shadow="0 0 8px var(--accent)",
)


# Fix keyframes syntax
css(
    "@keyframes pulse",
    **{"from": {"transform": "scale(1)"}, "to": {"transform": "scale(1.03)"}},
)

css(
    "@media (min-width: 640px)",
    **{
        ":root": {"--font-size-base": "18px"},
        ".container": {
            "max-width": "800px",
            "gap": "2rem",
            "padding": "2rem",
        },
        ".timer": {
            "padding": "2rem",
            "border-radius": "24px",
            "max-width": "600px",
        },
        ".timer span": {
            "font-size": "3rem",
            "margin": "0 1rem",
        },
        ".timer span i": {
            "font-size": "1rem",
            "margin-top": "0.5rem",
        },
        ".bit-viz": {
            "flex-direction": "row",
            "justify-content": "center",
            "gap": "1rem",
            "padding": "2rem",
        },
        ".bit": {
            "width": "20px",
            "height": "20px",
            "font-size": "0.8rem",
        },
        ".description": {
            "max-width": "600px",
            "padding": "1.5rem",
        },
        "a": {"padding": "0.75rem 2rem"},
    },
)

css(
    "@media (min-width: 1024px)",
    **{
        ":root": {"--font-size-base": "20px"},
        ".container": {
            "max-width": "1000px",
            "gap": "3rem",
            "padding": "3rem",
        },
        ".timer": {
            "padding": "3rem 2rem",
            "backdrop-filter": "blur(12px)",
        },
        ".timer span": {
            "font-size": "4rem",
        },
        ".bit-viz": {
            "padding": "2.5rem",
            "gap": "1.5rem",
        },
        ".bit": {
            "width": "24px",
            "height": "24px",
            "font-size": "0.9rem",
            "border-radius": "4px",
        },
    },
)

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


# Add new JavaScript function to handle SSE updates
@js.function
def handle_binary_updates():
    source = EventSource("/binary-updates")

    def update_display(event):
        try:
            data = JSON.parse(event.data)
            bits = document.querySelectorAll(".bit")
            binary = data["binary"]  # Use dictionary access syntax
            for i in range(len(bits)):
                bit = bits[i]
                bit.textContent = binary[i]  # Update the text content
                if binary[i] == "1":
                    bit.classList.add("active")
                else:
                    bit.classList.remove("active")
        except Exception as e:
            console.error("Error updating binary display:", e)

    source.onmessage = update_display
    source.onerror = lambda e: console.error("SSE error:", e)


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


def calculate_initial_timer() -> tuple[str, str, str, str]:
    """Calculate the initial timer values without relying on JS."""
    target = datetime(2038, 1, 19, 3, 14, 7)
    now = datetime.now()
    diff = target - now

    days = str(diff.days).zfill(4)
    hours = str((diff.seconds // 3600) % 24).zfill(2)
    minutes = str((diff.seconds // 60) % 60).zfill(2)
    seconds = str(diff.seconds % 60).zfill(2)

    return days, hours, minutes, seconds


# Update bit visualization helper function
def render_binary_visualization(doc, timestamp: int) -> str:
    """Convert timestamp to binary and create visualization."""
    binary = format(timestamp, "032b")  # 32-bit binary representation

    with div(cls="bit-viz"):
        # Group bits into bytes (8 bits each)
        for byte_index in range(4):
            start = byte_index * 8
            end = start + 8
            byte_bits = binary[start:end]

            with div(cls="byte-group"):
                for bit in byte_bits:
                    bit_class = "bit active" if bit == "1" else "bit"
                    div(bit, cls=bit_class)

    return str(doc)


# Finally, we define a single route handler for '/'.
# In the handler, we create a doc, embed css and js in appropriate places,
# and include the external js library.
# While embedding css or js, we use the style() or script() context block.


@app.route("/")
async def index():
    doc = Doc("html")
    with head():
        meta(charset="utf-8")
        meta(name="viewport", content="width=device-width, initial-scale=1.0")
        meta(name="description", content="Countdown to the Unix Timestamp Apocalypse")
        meta(name="theme-color", content="#0f172a")
        title("Year 2038 | Unix Timestamp Apocalypse")
        # Remove Google Fonts link
        with style():
            css.embed()
    with body(
        onload="start_timer(); handle_binary_updates()"
    ):  # Add binary clock start
        days, hours, minutes, seconds = calculate_initial_timer()
        current_timestamp = int(datetime.now().timestamp())
        with div(cls="container"):
            div(
                render_initial_timer(
                    days=days, hours=hours, minutes=minutes, seconds=seconds
                ),
                cls="timer j-timer",
            )
            # Add binary visualization
            render_binary_visualization(doc, current_timestamp)
            with div(cls="description"):
                a(
                    "to January 19, 2038 03:14:07",
                    href="https://en.wikipedia.org/wiki/Year_2038_problem",
                )
        script(src="/static/timezz.js")
        with script():  # You can comment out this block
            js.embed()  # to test render_initial_timer()
    return Response(str(doc))


# Add SSE endpoint with proper Quart streaming response
@app.route("/binary-updates")
async def binary_updates():
    async def stream_updates():
        while True:
            timestamp = int(datetime.now().timestamp())
            binary = format(timestamp, "032b")
            data = json.dumps({"binary": binary})
            yield f"data: {data}\n\n"
            await asyncio.sleep(1)

    return Response(
        stream_updates(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


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

app.run(debug=True, use_reloader=True, port=5000)
