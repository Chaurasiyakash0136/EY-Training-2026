# Homework — Facebook Distributed Memcache Load Balancing

# Introduction

Facebook handles billions of requests daily and requires an extremely scalable caching infrastructure. To reduce database load and improve performance, Facebook uses a distributed Memcache architecture.

The system distributes cached data across many cache servers while maintaining high availability, scalability, and fault tolerance.

---

# What Is Memcache?

Memcache is a distributed in-memory caching system used to:

* Reduce database queries
* Improve response time
* Handle massive traffic efficiently

Facebook heavily relies on Memcache for scaling its infrastructure.

---

# Core Load Balancing Concept

Unlike traditional centralized load balancers, Facebook primarily uses:

* Client-side sharding
* Consistent hashing
* Distributed caching

instead of routing all traffic through one central load balancer.

---

# Distributed Memcache Architecture

```text id="axwqrm"
Application Servers
        │
        ▼
Consistent Hashing
   │      │      │
   ▼      ▼      ▼
Cache1 Cache2 Cache3
```

---

# Consistent Hashing

Consistent hashing determines which cache server stores a specific key.

## Example

```text id="73l94s"
User123  → Cache Server 1
User456  → Cache Server 2
User789  → Cache Server 3
```

This distributes traffic evenly across cache nodes.

---

# Advantages of Facebook’s Approach

## Horizontal Scalability

New cache servers can be added easily when traffic increases.

---

## Reduced Bottlenecks

Traffic is distributed across multiple cache nodes instead of relying on one centralized server.

---

## Fault Tolerance

If one cache node fails:

* Requests are redistributed automatically
* System availability remains high

---

## High Performance

Memcache reduces expensive database queries and improves overall application speed.

---

# Key Concepts Learned

* Distributed Caching
* Consistent Hashing
* Client-side Sharding
* Horizontal Scaling
* Fault Tolerance
* Cache Load Distribution

---

# Conclusion

Facebook’s distributed Memcache architecture uses consistent hashing and distributed caching to balance load efficiently across multiple cache servers. This approach enables high scalability, low latency, and fault tolerance for massive-scale applications.
