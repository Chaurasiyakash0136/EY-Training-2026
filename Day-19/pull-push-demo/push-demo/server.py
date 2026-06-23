"""
PUSH Architecture Demo — Server
Uses Server-Sent Events (SSE) to PUSH notifications to the client.
The server sends data whenever it wants — client just listens.

Run: python server.py
"""

import time
import random
from datetime import datetime
from flask import Flask, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ALERTS = [
    "🚨 Payment received: ₹5,000 from Arjun",
    "🔔 New order #1042 placed",
    "⚠️  Server CPU usage above 80%",
    "✅ Deployment to production succeeded",
    "📦 Stock low: iPhone 15 (3 units left)",
    "💬 New support ticket from Priya",
]


@app.route("/push/stream")
def stream():
    """
    SSE endpoint — server PUSHES a new notification every 3 seconds.
    Client connects once and keeps receiving events without polling.
    """
    def event_generator():
        print("[PUSH SERVER] Client connected — starting push stream")
        count = 0
        while True:
            alert = random.choice(ALERTS)
            timestamp = datetime.now().strftime("%H:%M:%S")
            count += 1
            payload = f"[{timestamp}] #{count} {alert}"

            # SSE format: data: <message>\n\n
            yield f"data: {payload}\n\n"
            print(f"[PUSH SERVER] Pushed → {payload}")
            time.sleep(3)

    return Response(
        event_generator(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.route("/")
def index():
    return jsonify({
        "architecture": "PUSH",
        "mechanism": "Server-Sent Events (SSE)",
        "how_it_works": "Client connects once to /push/stream. Server pushes a new notification every 3 seconds automatically.",
        "client_action": "Just listen — no repeated requests needed",
    })


if __name__ == "__main__":
    print("=" * 50)
    print("  PUSH Architecture Demo — Server Running")
    print("  Stream endpoint: http://localhost:5001/push/stream")
    print("  Now run: python client.py")
    print("=" * 50)
    app.run(port=5001, threaded=True)
