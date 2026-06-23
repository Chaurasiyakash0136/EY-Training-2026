"""
PULL Architecture Demo — Server
Client must repeatedly ask (poll) this server for new notifications.
Server just waits — it never sends anything on its own.

Run: python server.py
"""

import random
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simulated notification store — new ones appear over time
_all_notifications = [
    "📦 Order #1001 shipped",
    "💰 Invoice #204 paid",
    "🔔 Meeting reminder: Standup at 10AM",
    "📧 New email from Rahul",
    "✅ PR #88 merged to main",
    "⚠️  Disk usage at 90% on prod server",
    "🛒 New signup: user@example.com",
    "📊 Weekly report ready to download",
]

_delivered_index = 0  # tracks how many notifications have been "revealed"


@app.route("/pull/notifications")
def get_notifications():
    """
    PULL endpoint — client must call this repeatedly to get updates.
    Each call reveals one new notification (simulating new data arriving over time).
    Server never sends anything on its own.
    """
    global _delivered_index

    timestamp = datetime.now().strftime("%H:%M:%S")

    if _delivered_index < len(_all_notifications):
        new_notification = _all_notifications[_delivered_index]
        _delivered_index += 1
        print(f"[PULL SERVER] Client asked at {timestamp} → returning new notification")
        return jsonify({
            "timestamp": timestamp,
            "has_new": True,
            "notification": new_notification,
            "total_so_far": _delivered_index,
        })
    else:
        print(f"[PULL SERVER] Client asked at {timestamp} → nothing new")
        return jsonify({
            "timestamp": timestamp,
            "has_new": False,
            "notification": None,
            "total_so_far": _delivered_index,
        })


@app.route("/pull/reset")
def reset():
    global _delivered_index
    _delivered_index = 0
    return jsonify({"status": "reset"})


@app.route("/")
def index():
    return jsonify({
        "architecture": "PULL",
        "mechanism": "HTTP Polling",
        "how_it_works": "Client calls /pull/notifications every 3 seconds to check for updates. Server waits passively.",
        "client_action": "Must keep asking — server never sends anything on its own",
    })


if __name__ == "__main__":
    print("=" * 50)
    print("  PULL Architecture Demo — Server Running")
    print("  Poll endpoint: http://localhost:5002/pull/notifications")
    print("  Now run: python client.py")
    print("=" * 50)
    app.run(port=5002, threaded=True)
