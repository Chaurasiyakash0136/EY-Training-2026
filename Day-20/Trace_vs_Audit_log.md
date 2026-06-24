# Day 20 – Observability & Governance in Production Multi-Agent Systems

## Objective

Modern AI systems generate large volumes of operational and compliance data.

To support debugging, monitoring, security, governance, and regulatory requirements, production systems typically maintain two different records:

1. Trace / Spans
2. Audit Logs

Although both record information about requests, they solve different business problems.

This exercise focuses on identifying which system should be used for different operational and compliance scenarios.

---

# Business Scenario

MeridianPay is a regulated lending platform powered by a multi-agent AI system.

The platform includes:

- Retrieval Agent
- Underwriting Agent
- Guardrail Agent
- Decision Agent

The platform processes millions of lending decisions every day and must satisfy:

- Reliability requirements
- Security requirements
- Compliance requirements
- Regulatory audits
- Cost monitoring requirements

The challenge is deciding whether a request belongs in:

- Trace / Spans
- Audit Logs
- Both Systems

---

# Understanding Trace / Spans

A Trace records how a request executes inside the system.

Example:

User Request

↓

Retrieval Agent

↓

Underwriting Agent

↓

Model Call

↓

Guardrail Agent

↓

Decision Agent

↓

Response

A trace helps engineers understand:

- Execution flow
- Latency
- Failures
- Dependencies
- Agent interactions
- Token usage

### Primary Users

- Developers
- SRE Teams
- Platform Engineers
- FinOps Teams

---

# Understanding Audit Logs

An Audit Log records important business actions.

Example:

```json
{
  "user_id": "12345",
  "action": "Loan Approved",
  "timestamp": "2026-06-24T10:15:00",
  "model_version": "v3.2"
}
```

Audit logs answer:

- What happened?
- Who performed the action?
- When did it happen?
- Can we prove it happened?

### Primary Users

- Compliance Teams
- Security Teams
- Risk Teams
- Auditors
- Legal Teams

---

# Trace vs Audit Log

| Category | Trace / Spans | Audit Log |
|-----------|--------------|------------|
| Purpose | Debugging | Accountability |
| Question Answered | How did it run? | Who did what? |
| Sampling | Usually sampled | Never sampled |
| Retention | Hours to weeks | Months to years |
| Mutability | Can expire | Immutable |
| Primary Users | SRE, Dev, FinOps | Compliance, Security |
| Data Stored | Execution details | Business decisions |
| Technology | OpenTelemetry | Signed Audit Store |

---

# Ticket Resolution

## Ticket 1

### Requirement

Reproduce a failing request in staging and identify exactly where the error occurred.

### Answer

✅ Trace / Spans

### Reason

The request flow, latency, execution tree, and failure location are all stored inside traces.

---

## Ticket 2

### Requirement

Investigate which agent introduced additional latency.

### Answer

✅ Trace / Spans

### Reason

Traces capture timing information for every operation.

---

## Ticket 3

### Requirement

Determine token consumption and average cost per request.

### Answer

✅ Trace / Spans

### Reason

Token usage and cost metrics are operational telemetry and can be collected from sampled traces.

---

## Ticket 4

### Requirement

Show the complete call tree for a failing production request.

### Answer

✅ Trace / Spans

### Reason

A trace contains the complete execution hierarchy.

---

## Ticket 5

### Requirement

Compliance requires proof that a loan approval occurred.

### Answer

✅ Audit Log

### Reason

Audit logs maintain permanent records of business decisions.

---

## Ticket 6

### Requirement

The decision record must remain valid even if a database administrator attempts to alter it years later.

### Answer

✅ Audit Log

### Reason

Audit logs are append-only and tamper-evident.

---

## Ticket 7

### Requirement

Provide evidence showing who approved a loan and when.

### Answer

✅ Audit Log

### Reason

Audit logs provide accountability and historical proof.

---

## Ticket 8

### Requirement

A guardrail blocked a suspicious transaction.

Compliance needs proof it happened.

SRE needs to understand why it triggered.

### Answer

✅ Both

### Reason

Audit Log:

- Permanent compliance evidence

Trace:

- Root cause analysis
- Execution details
- Debugging information

Both are required.

---

# Why Both Systems Exist

A common misconception is that traces and audit logs are interchangeable.

They are not.

### Trace

Focuses on:

- System behavior
- Performance
- Reliability

### Audit Log

Focuses on:

- Governance
- Security
- Accountability

Both serve different stakeholders.

---

# Industry Best Practices

## Trace Best Practices

- Use OpenTelemetry
- Enable distributed tracing
- Capture latency metrics
- Sample high-volume traffic
- Correlate requests with Trace IDs

---

## Audit Log Best Practices

- Store immutable records
- Use append-only storage
- Enable hash chaining
- Maintain long-term retention
- Support regulatory audits

---

# Production Architecture

User Request

↓

Multi-Agent Workflow

↓

Trace Generation (OpenTelemetry)

↓

Observability Platform

↓

Audit Event Generation

↓

Immutable Audit Store

↓

Compliance & Security Review

---

# Key Learning

Trace tells us:

"How did the request behave?"

Audit Log tells us:

"What happened and who is accountable?"

When debugging:

→ Use Trace

When proving compliance:

→ Use Audit Log

When both debugging and compliance are required:

→ Use Both

---

# Interview Answer

In production AI systems, traces and audit logs serve different purposes. Traces record the complete execution flow of a request, including latency, agent interactions, and failures, making them useful for debugging and observability. Audit logs record business actions, decisions, timestamps, and accountability information, making them essential for compliance, governance, and security. If we need to understand how a request behaved, we use traces. If we need evidence of what happened and who performed an action, we use audit logs.