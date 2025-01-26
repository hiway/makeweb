#!/usr/bin/env python

import asyncio
from quart import Quart, Response, websocket

from makeweb import Doc, CSS, JS
from makeweb.javascript import document, WebSocket, ws
from makeweb.html import (
    head,
    title,
    style,
    script,
    body,
    button,
    _input,
    ul,
    li,
    div,
    meta,
    link,
)

META = {
    "viewport": "width=device-width, initial-scale=1",
}

app = Quart(__name__)
css = CSS()
js = JS()
clients = set()

css(
    "*,body",
    margin="0",
    padding="0",
    font_family=(
        "-apple-system, BlinkMacSystemFont, 'Segoe UI', "
        "Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', "
        "'Helvetica Neue', sans-serif"
    ),
    font_size="14px",
    box_sizing="border-box",
    color="#2c3e50",
)

css("html, body", height="100%", background_color="#f5f6fa")

css(
    ".page",
    display="flex",
    flex_direction="column",
    height="100vh",
    max_width="800px",
    margin="0 auto",
    background_color="white",
    box_shadow="0 0 20px rgba(0,0,0,0.05)",
)

css(
    ".incoming_wrapper",
    flex_grow="1",
    overflow_y="auto",
    padding="1rem",
    scroll_behavior="smooth",
)

css(
    "#chat_log",
    list_style="none",
    padding="0",
    margin="0",
)

css(
    "#chat_log li",
    background_color="#f1f2f6",
    padding="0.8rem 1rem",
    border_radius="1rem",
    margin_bottom="0.5rem",
    max_width="80%",
    word_wrap="break-word",
    animation="fadeIn 0.3s ease-in",
)

css(
    ".input_area",
    display="flex",
    padding="1rem",
    gap="0.5rem",
    background_color="white",
    border_top="1px solid #eee",
)

css(
    "#txt_message",
    flex_grow="1",
    padding="0.8rem 1rem",
    border="1px solid #e1e1e1",
    border_radius="1.5rem",
    outline="none",
    transition="border-color 0.2s ease",
)

css(
    "#txt_message:focus",
    border_color="#3498db",
)

css(
    "#btn_send",
    background_color="#3498db",
    color="white",
    border="none",
    border_radius="1.5rem",
    width="3rem",
    height="3rem",
    cursor="pointer",
    transition="background-color 0.2s ease",
)

css(
    "#btn_send:hover",
    background_color="#2980b9",
)

css(
    "@keyframes fadeIn",
    _from={"opacity": "0", "transform": "translateY(10px)"},
    _to={"opacity": "1", "transform": "translateY(0)"},
)


@js.function
def send_message(event):
    if event.target.id != "btn_send" and event.code != "Enter":
        return
    txt_message = document.getElementById("txt_message").value
    if not txt_message:
        return
    ws.send(txt_message)
    document.getElementById("txt_message").value = ""
    document.getElementById("txt_message").focus()


@js.function
def on_message(event):
    _li = document.createElement("li")
    _txt = document.createTextNode(event.data)
    _li.appendChild(_txt)
    chat_log = document.getElementById("chat_log")
    chat_log.appendChild(_li)
    document.getElementById("bottom").scrollIntoView()


@js.script
def connect_websocket():
    ws = WebSocket("ws://127.0.0.1:5000/ws")
    ws.onmessage = on_message
    document.getElementById("bottom").scrollIntoView()


@app.route("/")
async def index():
    doc = Doc("html")
    with head():
        meta(name="charset", content="utf-8")
        [meta(name=k, content=v) for k, v in META.items()]
        meta(
            name="description",
            content="A minimal real-time chat application",
        )
        title("Chat")
        with style():
            css.embed()
    with body():
        with div(cls="page"):
            with div(cls="incoming_wrapper"):
                ul(id="chat_log")
                div("", id="bottom")
            with div(cls="input_area"):
                _input(
                    id="txt_message",
                    onkeyup="send_message(event)",
                    placeholder="Type a message...",
                    autofocus=True,
                )
                button("→", onclick="send_message(event)", id="btn_send")
        with script():
            js.embed()
    return Response(str(doc))


async def process_command(command):
    return "COMMAND: {}".format(command)


async def broadcast(message):
    """Broadcast message to all connected clients."""
    for queue in clients:
        try:
            await queue.put(message)
        except Exception as e:
            print(f"Error broadcasting message: {e}")
            if queue in clients:
                clients.remove(queue)


@app.websocket("/ws")
async def chat_websocket():
    """WebSocket endpoint for chat."""
    queue = asyncio.Queue()
    clients.add(queue)

    try:
        # Create producer task
        async def producer():
            while True:
                message = await queue.get()
                await websocket.send(message)

        # Create consumer task
        async def consumer():
            while True:
                message = await websocket.receive()
                if message.startswith("/"):
                    reply = await process_command(message[1:])
                    await queue.put(reply)
                else:
                    await broadcast(message)

        # Run both producer and consumer
        producer_task = asyncio.create_task(producer())
        consumer_task = asyncio.create_task(consumer())

        await asyncio.gather(producer_task, consumer_task)

    finally:
        clients.remove(queue)


if __name__ == "__main__":
    app.run()
