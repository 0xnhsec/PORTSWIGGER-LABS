# Broken Access Control (BAC) Fundamentals

Access control (authorization) determines whether a user is allowed to perform a requested action or access a specific resource. Broken Access Control (BAC) occurs when these restrictions are bypassed, misconfigured, or missing entirely.

```
Authentication  = "Who are you?"       (Identity validation via credentials/tokens)
Authorization   = "What can you do?"   (Privilege and access controls validation)

BAC occurs when the authorization logic is flawed, bypassed, or missing.
```

---

## 3 Core Categories

### 1. Vertical BAC
A user accesses functionality that requires **higher privileges** than their current account level.
```
Normal user ──→ accesses /admin/panel ──→ Returns 200 OK (Vulnerable)
```
*Example:* Accessing `/admin/deleteUser` under a standard customer session.

### 2. Horizontal BAC (Insecure Direct Object Reference - IDOR)
A user accesses resources belonging to **other users** who have the **same privilege level**.
```
User A (ID 1001) ──→ requests /invoice?id=1002 (User B's invoice) ──→ Returns 200 OK (Vulnerable)
```
*Example:* Accessing `/api/orders/5678` when it belongs to another customer.

### 3. Context-Dependent BAC
A user bypasses the **logical flow or sequence** of steps enforced by the application workflow.
```
Normal flow:   Step 1 (Select Item) ──→ Step 2 (Confirm Order) ──→ Step 3 (Payment Check)
BAC bypass:    Step 1 (Select Item) ─────────────────────────────→ Step 3 (Payment Check - skips Step 2)
```

---

## Vulnerability Patterns

### Pattern 1 — Frontend-Only Privilege Controls (Flawed)
Hiding administrative elements in the UI without server-side validation:
```javascript
// Browser-side Javascript (Insecure)
if (user.role === 'admin') {
    showAdminButton();
}
```
*Vulnerability:* The `/admin` endpoint remains fully accessible via direct HTTP requests.
*Fix:* Always enforce access control rules **on the server side**.

### Pattern 2 — Parameter-Based Role Control
The application accepts role variables directly from client inputs:
```http
POST /login HTTP/1.1
username=user&password=password&role=admin
```
*Vulnerability:* Attacker changes `role=user` to `role=admin` to escalate privileges.

### Pattern 3 — Predictable Resource ID (IDOR)
Incremental or sequential integers used for object identifiers:
```
/invoice/download?id=1001  -> User's invoice
/invoice/download?id=1002  -> Another user's invoice
```
*Fix:* Use UUIDs / GUIDs or validate that the active session matches the owner of the requested object.

### Pattern 4 — Reference Header Reliance
The server verifies access privileges using user-controlled HTTP headers:
```http
GET /admin/panel HTTP/1.1
Referer: https://target.com/admin
```
*Vulnerability:* Attackers manipulate the `Referer` header using interception tools to gain unauthorized access.

---

## Methodology for Hunting BAC

1. **Endpoint Mapping:** Walk through the target application as a low-privileged user, record all endpoints, parameter keys (e.g. `id=`, `userId=`), and headers.
2. **Vertical Privilege Escalation Testing:** Access documented administrative endpoints using a low-privileged session token.
   - Use the **Autorize** extension in Burp Suite to automate vertical privilege checks.
3. **Horizontal Privilege Escalation (IDOR) Testing:** Retrieve User A's resource IDs, swap cookies to User B, and request User A's data. Check parameters across:
   - URL query parameters (`/profile?id=123`)
   - URL path variables (`/users/123/settings`)
   - POST/PUT body keys (`{"userId": "123"}`)
   - Cookies and custom headers
4. **HTTP Method Switching:** Swap methods if restricted (e.g., if `DELETE /api/users/1337` returns 403, try `POST /api/users/1337` with `_method=DELETE` or headers).
