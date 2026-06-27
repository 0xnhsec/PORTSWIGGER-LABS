# Business Logic Vulnerabilities Fundamentals

Business logic vulnerabilities are flaws in the design and implementation of an application that allow attackers to manipulate its behavior to achieve unauthorized goals. These flaws arise because the application's logical rules—often built on top of developers' assumptions about user behavior—contain loopholes.

```
SQLi / XSS      = Exploiting syntax parsing rules (e.g. database, browser)
BAC / IDOR      = Bypassing permission structures to access forbidden resources
Business Logic  = Abusing the legal functionality of the features you are ALLOWED to access
```

---

## Why Automated Scanners Fail

Unlike signature-based vulnerabilities (like XSS or SQLi), business logic flaws do not have standardized detection payloads. Every application enforces a unique set of business rules. Identifying these flaws requires:
- Deep understanding of the application's domain and workflow.
- Identifying what steps, inputs, or combinations are expected versus what can be sent.
- Testing boundaries and out-of-order flows manually.

This makes business logic vulnerabilities highly valued in bug bounty programs, as they are rarely discovered by automated security tools.

---

## Core Vulnerability Categories

### 1. Excessive Trust in Client-Side Inputs
The server implicitly trusts parameters supplied directly by the client browser instead of validating or generating them internally.
- *Examples:*
  - Accepting product price fields from POST request bodies.
  - Relying on hidden input form fields for discount rates.
  - Trusting quantities without checking for negative integers.

### 2. Flawed Assumptions in Workflow Sequences
Developers often assume that users will only interact with the application through the intended visual user interface, following step-by-step processes in order.
- *Examples:*
  - Skipping confirmation step screens in multi-phase checkouts.
  - Registering accounts and skipping the verification screen.
  - Accessing internal administrative routes directly because they are hidden from standard navigation menus.

### 3. Boundary Condition Violations (Numerical Limits)
Developers fail to enforce strict boundary checks on numeric inputs, leading to integer overflows or unexpected state transitions.
- *Examples:*
  - Submitting negative quantities (e.g. `-10` items) to subtract prices from cart totals.
  - Exceeding the maximum integer limit (e.g., `2147483647`) to trigger numeric wrap-around (overflows).

### 4. Parser Discrepancies
Different backend systems (e.g., a reverse proxy, an application server, and an SMTP server) read or decode inputs differently, leading to validation bypasses.
- *Example:* Bypassing email domain filters using RFC 2047 encoding discrepancies (e.g. `=?utf-7?q?...?=`).
