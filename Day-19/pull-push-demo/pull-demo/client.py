"""
PULL Architecture Demo — Client
Must repeatedly ask the server every 3 seconds: "Is there anything new?"
This is polling — the client drives everything, server just responds.

Run: python client.py  (while server.py is running)
"""

import time
import requests

POLL_INTERVAL_SECONDS = 3


def poll_for_notifications():
    url = "http://localhost:5002/pull/notifications"
    poll_count = 0

    print("=" * 50)
    print("  PULL CLIENT — Starting to poll server")
    print(f"  Asking server every {POLL_INTERVAL_SECONDS} seconds...")
    print("  (Press Ctrl+C to stop)")
    print("=" * 50)

    while True:
        poll_count += 1
        print(f"\n[PULL CLIENT] Poll #{poll_count} → asking server...")

        try:
            response = requests.get(url)
            data = response.json()

            if data["has_new"]:
                print(f"[PULL RECEIVED] {data['notification']}")
                print(f"  (Total received so far: {data['total_so_far']})")
            else:
                print(f"[PULL CLIENT]  → No new notifications. Wasted request.")

        except requests.exceptions.ConnectionError:
            print("[ERROR] Could not connect. Is server.py running on port 5002?")
            break

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        poll_for_notifications()
    except KeyboardInterrupt:
        print("\n[PULL CLIENT] Stopped polling.")
