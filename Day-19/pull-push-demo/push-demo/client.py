"""
PUSH Architecture Demo — Client
Connects to the server ONCE and receives notifications as the server pushes them.
The client does NOT ask repeatedly — server drives everything.

Run: python client.py  (while server.py is running)
"""

import requests


def listen_for_push_notifications():
    url = "http://localhost:5001/push/stream"

    print("=" * 50)
    print("  PUSH CLIENT — Connected to server")
    print("  Waiting for server to push notifications...")
    print("  (Press Ctrl+C to stop)")
    print("=" * 50)

    # Single connection — server streams events to us
    with requests.get(url, stream=True) as response:
        for line in response.iter_lines():
            if line:
                decoded = line.decode("utf-8")
                if decoded.startswith("data:"):
                    message = decoded[len("data:"):].strip()
                    print(f"[PUSH RECEIVED] {message}")


if __name__ == "__main__":
    try:
        listen_for_push_notifications()
    except KeyboardInterrupt:
        print("\n[PUSH CLIENT] Disconnected.")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect. Is server.py running on port 5001?")
