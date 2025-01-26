"""
Journal App
"""

from quart import Quart, render_template, Response, request
from datetime import datetime
import aiofiles
import asyncio
import json
import uuid
import random
import os

app = Quart(__name__)
subscribers = set()
notification_task = None

SEVERITIES = ["info", "success", "warning", "error"]

# Cache for SVG contents
svg_cache = {}


async def get_svg(name):
    """Load and cache SVG content asynchronously"""
    if name not in svg_cache:
        svg_path = os.path.join(app.static_folder, "icons", f"{name}.svg")
        try:
            async with aiofiles.open(svg_path, "r") as f:
                content = await f.read()
                # Add data-icon attribute to svg element
                svg_cache[name] = content.replace(
                    "<svg ", f'<svg data-icon="{name}" class="icon" ', 1
                )
        except FileNotFoundError:
            return f"<!-- SVG {name} not found -->"
    return svg_cache[name]


# Make async svg loader available to templates
app.jinja_env.globals["get_svg"] = get_svg


async def broadcast_time():
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        severity = random.choice(SEVERITIES)

        for queue in subscribers:
            await queue.put(
                {
                    "id": str(uuid.uuid4()),
                    "severity": severity,
                    "title": "Current Time",
                    "message": f"The server time is {current_time}",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        await asyncio.sleep(5)


@app.before_serving
async def startup():
    global notification_task
    notification_task = asyncio.create_task(broadcast_time())


@app.after_serving
async def cleanup():
    if notification_task:
        notification_task.cancel()
        try:
            await notification_task
        except asyncio.CancelledError:
            pass


@app.route("/")
async def index():
    today = datetime.now().strftime("%B %d, %Y")
    return await render_template("index.html", today=today)


@app.route("/search")
async def search():
    # Will implement search functionality later
    return {"results": []}


@app.route("/notifications/stream")
async def notification_stream():
    async def stream():
        queue = asyncio.Queue()
        subscribers.add(queue)
        try:
            while True:
                message = await queue.get()
                yield f"event: notification\ndata: {json.dumps(message)}\n\n"
        finally:
            subscribers.remove(queue)

    return Response(stream(), mimetype="text/event-stream")


@app.route("/notifications/send", methods=["POST"])
async def send_notification():
    data = await request.get_json()
    for queue in subscribers:
        await queue.put(
            {
                "id": str(uuid.uuid4()),
                "severity": data.get("severity", "info"),
                "title": data["title"],
                "message": data["message"],
                "timestamp": datetime.now().isoformat(),
            }
        )
    return {"status": "sent"}


if __name__ == "__main__":
    app.run(debug=True)
