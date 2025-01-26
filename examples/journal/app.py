"""
Journal App
"""

from quart import Quart, render_template, Response, request
from datetime import datetime
import asyncio
import json
import uuid
import random

app = Quart(__name__)
subscribers = set()
notification_task = None

SEVERITIES = ["info", "success", "warning", "error"]


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
