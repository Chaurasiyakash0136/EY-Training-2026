# Day 08 — Queue vs Event Bus Architecture Assignment

## Overview

This assignment focuses on understanding messaging patterns used in distributed systems and microservice architectures. The objective is to identify when to use a Queue-based architecture and when to use an Event Bus architecture in a real-time payment platform.

The scenario is based on a fictional payment processing platform named **PayStream**, which handles millions of payment transactions and requires reliable communication between multiple services.

---

# Objective

Classify each system integration as either:

* **Queue**
  or
* **Event Bus**

based on scalability, delivery guarantees, retry behavior, consumer patterns, and messaging requirements.

---

# Concepts Covered

## Queue Architecture

A Queue is used when:

* A message must be processed by exactly one consumer
* Retry handling is required
* Task distribution/load balancing is needed
* Guaranteed processing is important
* Worker-based processing is used

### Common Use Cases

* Payment processing
* Background jobs
* SMS dispatching
* Batch processing
* Task queues

---

## Event Bus Architecture

An Event Bus is used when:

* Multiple services need the same event
* Pub/Sub communication is required
* Systems must remain loosely coupled
* Future subscribers may be added
* Broadcast/fan-out behavior is needed

### Common Use Cases

* Notifications
* Analytics events
* Activity streams
* State change propagation
* Real-time monitoring systems

---

# Platform Scenario

## PayStream Architecture

The PayStream platform contains multiple services:

* Merchant API
* Payment Core
* Ledger Service
* Fraud Engine
* Notification Hub
* Analytics Pipeline

These services communicate using asynchronous messaging patterns.

---

# Learning Outcomes

By completing this assignment, the following concepts were understood:

* Distributed messaging systems
* Queue-based communication
* Event-driven architecture
* Pub/Sub messaging model
* Retry and durability patterns
* Fan-out event broadcasting
* Worker pool architecture
* Exactly-once processing concepts

---

# Technologies & Architecture Concepts

* Distributed Systems
* Microservices
* Event-Driven Architecture
* Queue Messaging
* Event Bus
* Pub/Sub Model
* Worker Pool Design

---

# Conclusion

This assignment demonstrated how different messaging patterns solve different architectural problems in scalable distributed systems.

Queue architectures are best suited for controlled task execution and guaranteed processing, while Event Bus architectures are ideal for broadcasting events to multiple independent services.