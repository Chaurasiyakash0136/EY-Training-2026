# Pull vs Push Notification Architecture

Practical working demo of both architectures with pros/cons analysis.

---

## What is Push Architecture?

The **server sends data to the client** whenever something happens.  
Client connects once and just listens. Server is in control.

**Real world examples:** WhatsApp messages, Firebase FCM, stock price tickers, live sports scores.

### Pros
- **Real-time** — client gets data the instant it's available, zero delay
- **Efficient** — no wasted requests; server only sends when there's something to send
- **Lower client load** — client doesn't need to run a polling loop
- **Scales well for event-driven systems** — one event → one delivery

### Cons
- **Persistent connection required** — server must maintain an open connection per client
- **Harder to implement** — needs WebSockets or SSE, not plain HTTP
- **Firewall/proxy issues** — long-lived connections are sometimes blocked by corporate networks
- **Server resource cost** — 10,000 connected clients = 10,000 open connections

---

## What is Pull Architecture?

The **client repeatedly asks the server** "is there anything new?"  
Server just waits and responds. Client is in control.

**Real world examples:** Email clients checking for mail, RSS feed readers, REST API polling.

### Pros
- **Simple to implement** — plain HTTP GET, works everywhere
- **Client controls the pace** — poll fast or slow depending on need
- **Stateless server** — no persistent connections to manage
- **Easy to debug** — every poll is a standard HTTP request you can inspect

### Cons
- **Not real-time** — you only know about new data after the next poll
- **Wasted requests** — most polls return "nothing new", burning bandwidth and CPU
- **Latency** — if you poll every 10s, average delay is 5s
- **Doesn't scale well** — 10,000 clients polling every second = 10,000 req/sec constant load

---

## When to Use Which?

| Scenario | Use |
|---|---|
| Chat app, live notifications | **Push** |
| Dashboard that updates every minute | **Pull** |
| Stock ticker, live scores | **Push** |
| Syncing emails in background | **Pull** |
| IoT sensor streaming data | **Push** |
| Checking order status occasionally | **Pull** |

---

## Project Structure

```
pull-push-demo/
├── push-demo/
│   ├── server.py          ← Flask SSE server (pushes every 3s)
│   ├── client.py          ← Connects once, receives pushed events
│   └── requirements.txt
├── pull-demo/
│   ├── server.py          ← Flask REST server (waits passively)
│   ├── client.py          ← Polls server every 3 seconds
│   └── requirements.txt
└── README.md
```

---

## How to Run

### Prerequisites
```bash
pip install flask flask-cors requests
```

---

### Run the PUSH Demo

**Terminal 1 — start the server:**
```bash
cd push-demo
python server.py
```

**Terminal 2 — start the client:**
```bash
cd push-demo
python client.py
```

**What you'll see:**
```
[PUSH CLIENT] Connected to server — waiting for notifications...
[PUSH RECEIVED] [10:01:03] #1 🚨 Payment received: ₹5,000 from Arjun
[PUSH RECEIVED] [10:01:06] #2 ✅ Deployment to production succeeded
[PUSH RECEIVED] [10:01:09] #3 📦 Stock low: iPhone 15 (3 units left)
```
→ Client made **ONE connection**. Server pushed all 3 events automatically.

---

### Run the PULL Demo

**Terminal 1 — start the server:**
```bash
cd pull-demo
python server.py
```

**Terminal 2 — start the client:**
```bash
cd pull-demo
python client.py
```

**What you'll see:**
```
[PULL CLIENT] Poll #1 → asking server...
[PULL RECEIVED] 📦 Order #1001 shipped

[PULL CLIENT] Poll #2 → asking server...
[PULL RECEIVED] 💰 Invoice #204 paid

[PULL CLIENT] Poll #3 → asking server...
[PULL CLIENT]  → No new notifications. Wasted request.
```
→ Client made a **new HTTP request every 3 seconds**. Most return nothing.

---

## Key Difference — Visible in the Code

| | Push (`push-demo/client.py`) | Pull (`pull-demo/client.py`) |
|---|---|---|
| **Connections made** | 1 (stays open) | 1 per poll (repeated) |
| **Who controls timing** | Server | Client |
| **Wasted requests** | None | Yes — polls with no data |
| **Latency** | Instant | Up to 3 seconds |
