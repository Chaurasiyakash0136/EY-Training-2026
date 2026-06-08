# Queue vs Event Bus — Final Answers

| ID | Integration                     | Classification | Justification                                                                                                                                                  |
| -- | ------------------------------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A  | Settlement command              | Queue          | The settlement instruction must be processed exactly once by a single consumer. Retry support is required to avoid message loss or duplication.                |
| B  | Payment received broadcast      | Event Bus      | Multiple independent systems such as Notifications, Analytics, and Fraud services must react to the same event simultaneously using a publish-subscribe model. |
| C  | SMS / Push notifications        | Queue          | Notification tasks must be distributed across worker pools where each message is processed by only one worker to prevent duplicate customer alerts.            |
| D  | Fraud score request             | Queue          | This is a synchronous request/reply workflow involving a dedicated processing service. The task should be handled by a single consumer.                        |
| E  | Account state change events     | Event Bus      | Multiple services must independently react to account status changes, and future subscribers may be added without modifying the producer.                      |
| F  | End-of-day reconciliation batch | Queue          | Reconciliation jobs require worker distribution, retry handling, and guaranteed task processing by one worker only.                                            |

---

# Final Classification Summary

## Queue-Based Integrations

* A — Settlement command
* C — SMS / Push notifications
* D — Fraud score request
* F — End-of-day reconciliation batch

### Why Queue?

These integrations require:

* Single consumer processing
* Retry mechanisms
* Task distribution
* Guaranteed execution
* Worker pool architecture

---

## Event Bus-Based Integrations

* B — Payment received broadcast
* E — Account state change events

### Why Event Bus?

These integrations require:

* Fan-out communication
* Multiple subscribers
* Publish/Subscribe architecture
* Independent service reactions
* Extensible event-driven systems

---

# Key Architectural Decision Rules

## Use Queue When

* Exactly one consumer should process a message
* Retry and dead-letter handling are required
* Task distribution/load balancing is needed
* Guaranteed execution is important
* Worker-based processing is used

---

## Use Event Bus When

* Multiple services must react to the same event
* Broadcast/fan-out communication is needed
* Systems should remain loosely coupled
* New subscribers may be added in future
* Event-driven extensibility is required

---

# Assignment Outcome

This exercise demonstrates practical understanding of distributed messaging patterns and how Queue and Event Bus architectures are applied in real-world payment processing systems.