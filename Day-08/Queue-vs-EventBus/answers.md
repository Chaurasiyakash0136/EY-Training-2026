# Queue vs Event Bus — Final Classification Answers

# Problem Statement

The PayStream payment platform contains multiple microservices communicating through asynchronous messaging patterns.

The task was to classify each integration as either:

* Queue
  or
* Event Bus

based on how messages are consumed and distributed across services.

---

# Final Answers

| ID | Integration                     | Classification | Justification                                                                                                                            |
| -- | ------------------------------- | -------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| A  | Settlement command              | Queue          | The settlement task must be processed exactly once by a single consumer with retry support to prevent message duplication or loss.       |
| B  | Payment received broadcast      | Event Bus      | Multiple independent services such as Notifications, Analytics, and Fraud systems must react to the same event simultaneously.           |
| C  | SMS / Push notifications        | Queue          | Notification tasks must be distributed across worker pools where each message is processed only once to avoid duplicate customer alerts. |
| D  | Fraud score request             | Queue          | This is a request/reply workflow involving a dedicated processing service and controlled task execution.                                 |
| E  | Account state change events     | Event Bus      | Multiple systems must independently react to account status changes, and future subscribers may be added without modifying the producer. |
| F  | End-of-day reconciliation batch | Queue          | Reconciliation jobs require worker distribution, retry handling, and guaranteed task execution by a single worker.                       |

---

# Queue-Based Integrations

## A — Settlement Command

### Why Queue?

* Exactly-once processing required
* Retry handling needed
* Single consumer model

### Flow Diagram

```text
Payment Core
      │
      ▼
 Settlement Queue
      │
      ▼
 Ledger Service
```

---

## C — SMS / Push Notifications

### Why Queue?

* One worker per notification
* Load balancing required
* Prevent duplicate SMS delivery

### Flow Diagram

```text
Notification Hub
        │
        ▼
 Notification Queue
    │       │       │
    ▼       ▼       ▼
Worker1 Worker2 Worker3
```

---

## D — Fraud Score Request

### Why Queue?

* Dedicated consumer processing
* Controlled request/reply workflow
* Synchronous processing model

### Flow Diagram

```text
Payment Core
      │
      ▼
 Fraud Request Queue
      │
      ▼
 Fraud Engine
```

---

## F — End-of-Day Reconciliation

### Why Queue?

* Worker pool processing
* Retry support required
* High-throughput batch execution

### Flow Diagram

```text
Reconciliation Jobs
         │
         ▼
 Batch Queue
    │      │      │
    ▼      ▼      ▼
Worker Worker Worker
```

---

# Event Bus-Based Integrations

## B — Payment Received Broadcast

### Why Event Bus?

* Multiple independent subscribers
* Fan-out communication
* Pub/Sub architecture

### Flow Diagram

```text
                  ┌──────────────┐
                  │ Notification │
                  └──────────────┘
                          ▲
                          │
Payment Event ──► Event Bus ──► Analytics
                          │
                          ▼
                    Fraud Service
```

---

## E — Account State Change Events

### Why Event Bus?

* Multiple systems react independently
* Future subscribers can be added easily
* Loose coupling between services

### Flow Diagram

```text
                 ┌────────────┐
                 │ Compliance │
                 └────────────┘
                        ▲
                        │
Account Event ─► Event Bus ─► Merchant Portal
                        │
                        ▼
                  Payment Core
```

---

# Final Classification Summary

## Queue Integrations

* A — Settlement command
* C — SMS / Push notifications
* D — Fraud score request
* F — End-of-day reconciliation batch

### Queue Is Best When

* One worker processes one task
* Retry handling is important
* Controlled execution is required
* Task distribution/load balancing is needed

---

## Event Bus Integrations

* B — Payment received broadcast
* E — Account state change events

### Event Bus Is Best When

* Multiple services need same event
* Broadcast/fan-out is required
* Systems should remain loosely coupled
* Pub/Sub communication is preferred

---

# Overall Assignment Summary

This assignment demonstrated how Queue and Event Bus architectures are applied in real-world distributed payment systems.

Queues are ideal for reliable task execution and worker-based processing, while Event Bus architectures are best for scalable event broadcasting across multiple independent services.
