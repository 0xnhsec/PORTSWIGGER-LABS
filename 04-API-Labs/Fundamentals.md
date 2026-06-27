# API Vulnerabilities Fundamentals

API testing focuses on discovering undocumented entry points (attack surface) and exploiting backend logic vulnerabilities that might not be visible from the primary web user interface. This is critical for modern microservices and API-driven architectures.

---

## 1. API Reconnaissance (Attack Surface Discovery)

Before attempting to exploit an API, you must map out its routes and endpoints:

- **Browsing & Pattern Hunting:** Inspect traffic in Burp Proxy. Look for common URL route patterns such as `/api/v1/`, `/v2/`, `/developer`, or `/swagger`. Analyze loaded JavaScript source files for hardcoded endpoints.
- **Documentation Enumeration:** Look for exposed API documentation paths:
  - `/api/swagger.json`
  - `/swagger/v1/swagger.json`
  - `/api/index.html`
  - `/api/v1/docs`
- **HTTP Method Fuzzing:** Don't limit interactions to the standard `GET` requests. Switch between `OPTIONS`, `POST`, `PUT`, `DELETE`, and `PATCH` in Burp Repeater to analyze server behavior on different endpoints.
- **Content-Type Testing:** Alter `Content-Type` headers (e.g. from `application/json` to `application/xml`) to see if the backend uses different parsers that lack robust input filtering.

---

## 2. Mass Assignment (Parameter Binding)

Mass assignment occurs when client request parameters are directly bound to internal backend database objects without authorization verification or property filtering.

- **Detection:** Compare variables returned in `GET` responses against payload structures accepted in `POST/PUT/PATCH` requests. If a `GET` query returns `"is_admin": false`, try including `"is_admin": true` inside your updating request.
- **Exploitation:** Manually inject administrative properties (e.g., `"role": "admin"`, `"permissions": ["all"]`) into the request body via Burp Suite.

---

## 3. Server-Side Parameter Pollution (SSPP)

Server-Side Parameter Pollution arises when user-controlled inputs are passed from a public-facing API to an internal API without proper sanitization, altering the logic of the internal request.

- **Query String Injection:** Inject query parameter separators such as `&`, `=`, or `#` to introduce new variables.
  - *Example:* Public request `/api/user?username=INPUT` translates internally to `/internal/user?username=INPUT`. Injecting `attacker&status=active` changes the query to `/internal/user?username=attacker&status=active`.
- **Query String Truncation:** Use the URL-encoded hash character `%23` (`#`) to truncate query strings at the backend, ignoring parameters placed after the user's input.
- **REST Path Injection:** Inject directory traversal patterns (`../`) into path variables to redirect public REST API routes to private internal API paths.
