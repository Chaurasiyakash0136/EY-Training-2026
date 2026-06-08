# Azure Load Balancer vs Application Gateway — Final Answers

# Final Classification Table

| # | Requirement             | Classification      | Key Deciding Factor                              |
| - | ----------------------- | ------------------- | ------------------------------------------------ |
| 1 | Patient web portal      | Application Gateway | HTTPS traffic, WAF protection, URL-based routing |
| 2 | Clinical API (internal) | Load Balancer       | Internal TCP traffic, Layer 4 routing            |
| 3 | DICOM image streaming   | Load Balancer       | Large TCP payloads, long-lived connections       |
| 4 | Authentication service  | Application Gateway | Header-based routing, Layer 7 inspection         |
| 5 | Legacy SOAP lab service | Load Balancer       | Internal TCP failover, no content inspection     |
| 6 | Admin dashboard         | Application Gateway | Hostname-based routing, HTTPS traffic            |

---

# Detailed Explanations

# 1. Patient Web Portal → Application Gateway

## Why?

The patient-facing portal uses:

* HTTPS traffic
* URL-based routing
* WAF protection
* Layer 7 features

Application Gateway supports intelligent web traffic management and security inspection.

## Architecture Flow

```text id="vwxns3"
Internet Users
       │
       ▼
Application Gateway
   │           │
   ▼           ▼
 /api        /static
Backend A   Storage
```

---

# 2. Clinical API (Internal) → Load Balancer

## Why?

The API traffic:

* Is entirely internal
* Uses TCP
* Requires fast routing
* Does not need HTTP inspection

Load Balancer is optimized for Layer 4 traffic distribution.

## Architecture Flow

```text id="zhh4r5"
Hospital Systems
        │
        ▼
Load Balancer
    │       │
    ▼       ▼
 API VM1  API VM2
```

---

# 3. DICOM Image Streaming → Load Balancer

## Why?

The system handles:

* Large TCP payloads
* Long-lived sessions
* Non-HTTP traffic
* Session persistence

Load Balancer provides efficient Layer 4 traffic handling.

## Architecture Flow

```text id="rmv3gx"
Radiology Systems
         │
         ▼
Load Balancer
    │         │
    ▼         ▼
 Image VM1  Image VM2
```

---

# 4. Authentication Service → Application Gateway

## Why?

The service requires:

* Header-based routing
* Multi-tenant support
* HTTPS inspection
* TLS handling

These are advanced Layer 7 capabilities.

## Architecture Flow

```text id="z7p0x2"
Login Request
      │
      ▼
Application Gateway
   │         │
   ▼         ▼
Tenant A  Tenant B
Backend   Backend
```

---

# 5. Legacy SOAP Lab Service → Load Balancer

## Why?

The SOAP service:

* Uses raw TCP traffic
* Needs internal failover
* Requires no payload inspection
* Needs simple redundancy

Load Balancer is the correct Layer 4 solution.

## Architecture Flow

```text id="o5z25u"
Lab Systems
     │
     ▼
Load Balancer
   │       │
   ▼       ▼
SOAP VM1 SOAP VM2
```

---

# 6. Admin Dashboard → Application Gateway

## Why?

The dashboard requires:

* Hostname-based routing
* HTTPS support
* Multiple sites on one IP
* Layer 7 routing

Application Gateway supports these advanced web-routing capabilities.

## Architecture Flow

```text id="fjlwmu"
admin.site.com
www.site.com
        │
        ▼
Application Gateway
   │             │
   ▼             ▼
Admin Pool   Public Pool
```

---

# Final Summary

## Use Azure Load Balancer When

* Traffic is TCP/UDP
* Routing is Layer 4
* Internal traffic is used
* Low latency is required
* No HTTP inspection is needed

---

## Use Azure Application Gateway When

* Traffic is HTTP/HTTPS
* URL or hostname routing is required
* WAF security is needed
* SSL termination is required
* Advanced Layer 7 routing is needed

---

# Assignment Outcome

This assignment demonstrated practical understanding of Azure networking architectures and how Layer 4 and Layer 7 routing solutions are selected in real-world enterprise cloud systems.
