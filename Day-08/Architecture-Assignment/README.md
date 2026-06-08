# Day 08 — Azure Load Balancer vs Application Gateway

# Overview

This assignment focuses on understanding Azure traffic routing architectures and selecting the correct networking component based on real-world infrastructure requirements.

The task was to classify multiple healthcare platform scenarios as either:

* Azure Load Balancer
  or
* Azure Application Gateway

based on routing behavior, traffic type, security requirements, scalability, and application-layer features.

---

# Objective

Analyze each requirement and determine whether Azure Load Balancer or Azure Application Gateway is the best architectural solution.

---

# Core Concepts

# Azure Load Balancer

Azure Load Balancer operates at **Layer 4 (Transport Layer)**.

It distributes:

* TCP traffic
* UDP traffic

without inspecting:

* URLs
* HTTP headers
* Cookies
* Hostnames

## Best Used For

* Internal traffic
* High-performance TCP routing
* Non-HTTP applications
* Low-latency routing
* Simple failover systems

---

# Azure Application Gateway

Azure Application Gateway operates at **Layer 7 (Application Layer)**.

It understands:

* HTTP
* HTTPS
* URLs
* Hostnames
* Headers
* Cookies

## Best Used For

* Public web applications
* APIs
* HTTPS applications
* WAF protection
* URL-based routing
* Hostname-based routing

---

# Architecture Comparison

## Azure Load Balancer

```text id="n7sp1z"
Client Traffic
      │
      ▼
Load Balancer (Layer 4)
   │       │
   ▼       ▼
 VM1      VM2
```

---

## Azure Application Gateway

```text id="upc02n"
User Request
      │
      ▼
Application Gateway (Layer 7)
   │         │
   ▼         ▼
 /api      /admin
Backend1   Backend2
```

---

# Learning Outcomes

By completing this assignment, the following concepts were understood:

* Layer 4 vs Layer 7 routing
* TCP vs HTTP traffic handling
* WAF protection
* SSL termination
* Host-based routing
* URL path routing
* Session persistence
* Internal vs public traffic architecture

---

# Technologies & Concepts

* Microsoft Azure
* Azure Load Balancer
* Azure Application Gateway
* Distributed Systems
* Cloud Networking
* Layer 4 Routing
* Layer 7 Routing
* WAF Security

---

# Conclusion

Azure Load Balancer is best suited for high-performance Layer 4 traffic distribution and internal services, while Azure Application Gateway is ideal for intelligent Layer 7 web traffic management with advanced routing and security features.
