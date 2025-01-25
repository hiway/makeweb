#!/usr/bin/env python
#
# chat.py
#
#
import asyncio

import websockets
from quart import Quart, Response

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
)

META = {
    "viewport": "width=device-width, initial-scale=1",
}

app = Quart(__name__)
css = CSS()
js = JS()
clients = set()  # Websocket chat clients.

css(
    "*,body",
    margin="0",
    padding="0",
    font__family="roboto,verdana,sans-serif",
    font__size="12pt",
)
css("html, body", height="100%")
css(
    "input",
    box__sizing="border-box",
    __moz__box__sizing="border-box",
    __webkit__box__sizing="border-box",
)
css(
    ".page",
    display="grid",
    grid__template__columns="auto 3em",
    grid__auto__rows="minmax(10px, auto)",
    grid__gap="6px",
    position="relative",
    top="0",
    left="0",
    margin="0.5em",
    margin__bottom="1em",
)
css(
    "#chat_log",
    grid__column="1 / 3",
    grid__row="1",
    width="100%",
    max__height="100%",
    max__width="100%",
    overflow="auto",
)
css(
    "#chat_log li",
    list__style="none",
    font__size="12pt",
    margin__left="1em",
    margin__right="1em",
)
css(
    "#txt_message",
    grid__row="2",
    grid__column="1",
    width="100%",
    padding__left="0.8em",
    padding__right="0.2em",
)
css(
    "#btn_send",
    grid__row="2",
    grid__column="2",
    font__size="1.2em",
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
    ws = WebSocket("ws://127.0.0.1:5001/")
    ws.onmessage = on_message
    document.getElementById("bottom").scrollIntoView()


@app.route("/")
async def index():
    doc = Doc("html")
    with head():
        meta(name="charset", content="utf-8")
        [meta(name=k, content=v) for k, v in META.items()]
        title("Anon?Chat")
        with style():
            css.embed()
    with body():
        with div(cls="page"):
            with div(cls="incoming_wrapper"):
                with ul(id="chat_log"):
                    [li("&nbsp;") for x in range(50)]
                div("", id="bottom")
            _input(id="txt_message", onkeyup="send_message(event)", autofocus=True)
            button("⏎", onclick="send_message(event)", id="btn_send")
        with script():
            js.embed()
    return Response(str(doc))


async def process_command(command):
    return "COMMAND: {}".format(command)


async def chat_server(websocket):  # Removed 'path' parameter
    clients.add(websocket)

    async def send_message(clients, client, message):
        try:
            await client.send(message)  # Simplified send
        except Exception as e:
            print(f"Error sending message: {e}")
            if client in clients:  # Check if client exists before removing
                clients.remove(client)

    try:
        async for message in websocket:
            print(message)
            if message.startswith("/"):
                reply = await process_command(message[1:])
                await websocket.send(reply)
                continue
            # Use gather for concurrent sends
            await asyncio.gather(
                *(send_message(clients, client, message) for client in clients)
            )
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        if websocket in clients:  # Check if client exists before removing
            clients.remove(websocket)


ws_server = None


@app.before_serving
async def startup():
    global ws_server
    ws_server = await websockets.serve(chat_server, "0.0.0.0", 5001)


@app.after_serving
async def shutdown():
    global ws_server
    ws_server.close()
    await ws_server.wait_closed()


app.run()
