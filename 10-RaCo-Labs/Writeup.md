# Race Conditions Labs 01-06 — Proof of Concept Writeups

This document contains structured Proof of Concept (PoC) writeups for Race Condition (RaCo) Labs 01 to 06 from the PortSwigger Web Security Academy.

---

## Lab 01 — Limit Overrun Race Conditions

- **Goal:** Buy the leather jacket using a single-use coupon multiple times.
- **Vulnerability:** Time-of-check to time-of-use (TOCTOU) logic in coupon application.

### Proof of Concept (PoC)
1. Add the leather jacket to your cart.
2. Intercept the request to apply the coupon `PROMO_CODE`:
   `POST /cart/coupon` with parameter `csrf=TOKEN&coupon=PROMO_CODE`
3. Send this request to Burp Repeater, duplicate it 20 times, and group them.
4. Select the option to send all requests in parallel (using HTTP/2 single-packet attack).
5. Review responses: multiple requests return 200 OK showing the coupon applied repeatedly. Check out.

### Why It Works
The application verifies if the coupon has been used in previous completed purchases. However, it does not lock the database state during the active checkout thread validation, opening a race window where multiple concurrent threads read the coupon status as "unused" before the database records the update.

---

## Lab 02 — Bypassing Rate Limits via Race Conditions

- **Goal:** Brute-force credentials for user `carlos` bypassing rate limit lockouts.
- **Vulnerability:** Concurrency check gap in rate limit counter updates.

### Proof of Concept (PoC)
1. Intercept a login request to `POST /login`.
2. Send to Turbo Intruder and configure HTTP/2 single-packet multiplexing:
   - Target connections: `concurrentConnections=1`
   - Engine: `Engine.BURP2`
3. Queue 100 candidate passwords grouped under a single gate, then trigger:
   ```python
   engine.openGate('1')
   ```
4. Note that all 100 requests execute concurrently, yielding 200 OK responses instead of WAF block pages, successfully identifying the password.

### Why It Works
The rate limiter tracks login attempts and updates the lock counter in the database. Because the attempts arrive inside a single TCP packet, the login queries execute simultaneously before the counter thread has completed updating the lockout limit.

---

## Lab 03 — Multi-endpoint Race Conditions

- **Goal:** Buy the leather jacket using a cart transaction balance exploit.
- **Vulnerability:** Multi-endpoint state verification discrepancy.

### Proof of Concept (PoC)
1. Add a cheap item to your cart.
2. In Burp, capture the checkout confirmation request `POST /cart/checkout`.
3. In another tab, capture the add-to-cart request `POST /cart` containing the leather jacket.
4. Group both requests in Burp Repeater.
5. Send both requests in parallel (single-packet attack).
6. Verify the checkout request processed first, but the leather jacket was added to the cart before the checkout completed its final validation.

### Why It Works
The application checks if the user has sufficient balance on the checkout endpoint. Once verified, it proceeds to finalize the transaction. By injecting the expensive item during this millisecond window, the order completes containing both items without validating the balance again.

---

## Lab 04 — Single-endpoint Race Conditions

- **Goal:** Modify account email to hijack other users' verification flows.
- **Vulnerability:** Sub-state collisions in single parameter updates.

### Proof of Concept (PoC)
1. Initiate an email change request to update your address to `attacker@evil.com`.
2. Intercept the request. Group it with another identical request to change to a second address.
3. Send requests in parallel.
4. The database records a sub-state mismatch: the email address updates to Carlos's target address, but the verification link token is sent to the attacker's inbox.
5. Use the link to verify the hijack.

### Why It Works
When the server handles email updates, it generates a confirmation token and sends it. Because the database updates are not thread-safe, thread A updates the email address while thread B generates the verification token, sending the confirmation link to the wrong recipient.

---

## Lab 05 — Exploiting Time-sensitive Vulnerabilities

- **Goal:** Retrieve the password reset token for `carlos`.
- **Vulnerability:** Cryptographic token generation is seeded using guessable system timestamps.

### Proof of Concept (PoC)
1. Trigger a password reset for `carlos`.
2. Simultaneously trigger a password reset for your own user account.
3. Send both requests in a synchronized parallel group using HTTP/2.
4. If both requests reach the database at the exact same millisecond, the random number generator generates identical reset tokens.
5. Copy the reset token sent to your email and apply it to Carlos's password reset endpoint.

### Why It Works
The server generates security tokens using a pseudo-random number generator (PRNG) seeded with the system's current time. Forcing two threads to execute at the exact same millisecond initializes the generator with the identical seed, yielding matching tokens.

---

## Lab 06 — Partial Construction Race Conditions

- **Goal:** Hijack an administrative account during registration.
- **Vulnerability:** The server registers the account details before verifying profile attributes or roles.

### Proof of Concept (PoC)
1. Capture the registration `POST /register` request.
2. Capture the account profile update request `GET /my-account` (or API call).
3. Group the registration request and profile query request in Burp.
4. Send the group in parallel.
5. If timed correctly, the profile query executes during the millisecond window where the user record is initialized in the DB but before WAF authorization rules are fully bound, granting default administrative bypasses.

### Why It Works
The application database inserts a new user record in step 1, then binds security parameters or roles in step 2. Querying the account during this sub-state execution exposes the raw record, allowing attackers to access unconfigured fields or override defaults.
