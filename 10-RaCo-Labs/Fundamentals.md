# Race Conditions (Concurrency Vulnerabilities) Fundamentals

A race condition occurs when a web application processes concurrent requests simultaneously without proper synchronization constraints. When multiple processing threads access and modify the same data record at the same time, it causes collisions and unexpected application behavior.

---

## The Race Window

The race window is the duration of time (often a few milliseconds) between the start of a validation check and the completion of the database update operation.
- **Classic TOCTOU (Time-of-Check to Time-of-Use):** The server verifies user state (check), then performs action (use). If a second request enters the cycle *before* the first request finishes writing the updated state, the check passes again.

```
Request 1: [Check Balance: OK] ───────────────────────→ [Deduct Balance & Deliver]
Request 2:      [Check Balance: OK] ───────────────────→ [Deduct Balance & Deliver]
                                   ^
                              Race Window
```

---

## Overcoming Network Jitter (Single-Packet Attack)

To trigger collisions, concurrent requests must reach the server within the same millisecond. Normal network latency variance (network jitter) usually splits requests.
Modern testing tools (like Burp Suite 2023.9+ or Turbo Intruder) bypass jitter using protocol features:

### 1. HTTP/1.1 Last-Byte Synchronization
The client sends the bulk of multiple requests down separate TCP connections but holds back the final byte of each request. Once all connections are ready, the client transmits the final bytes simultaneously.

### 2. HTTP/2 Single-Packet Attack
HTTP/2 multiplexing allows sending multiple request frames inside a single TCP packet. Since the packet containing the requests is received by the server in one go, network jitter is eliminated, forcing the server to process the request threads concurrently.

---

## Main Race Condition Variants

### 1. Limit Overrun
Violating resource limits (e.g. redeeming a coupon code multiple times, withdrawing more funds than the account balance, or bypassing rate limits on brute force inputs).

### 2. Multi-Endpoint Race Conditions
Exploiting state variables shared across multiple endpoints.
- *Example:* Adding an item to the cart (endpoint A) while the checkout process (endpoint B) is verifying totals. If timed correctly, the order confirms using a state that is updated after checks but before payment.

### 3. Single-Endpoint Race Conditions
Concurrent updates on a single route causing database state collision.
- *Example:* Submitting two email changes concurrently. The database updates the email address but generates a single token, which might map to the wrong session or overwrite active records.

### 4. Time-Sensitive Vulnerabilities
Systems utilizing predictable inputs (such as time-based seeds for generating password reset tokens). Triggering requests at the exact same millisecond can yield identical verification tokens.
