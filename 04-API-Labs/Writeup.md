# API Testing Labs 01-05 — Proof of Concept Writeups

This document contains structured Proof of Concept (PoC) writeups for API Testing Labs 01 to 05 from the PortSwigger Web Security Academy.

---

## Lab 01 — Exploiting an API Endpoint Using Documentation

- **Goal:** Access administrative API endpoints using documentation and delete user `carlos`.
- **Vulnerability:** Exposed API documentation showing sensitive endpoints.

### Proof of Concept (PoC)
1. Map application endpoints. Identify a potential directory `/api`.
2. Access the API documentation endpoints:
   - Try `/api/swagger.json` or `/api/index.html`.
3. Locate the administrative endpoint from the Swagger schema:
   `DELETE /api/users/{username}`
4. Execute the deletion request:
   ```http
   DELETE /api/users/carlos HTTP/2
   ```

### Why It Works
The Swagger JSON file was publicly accessible and documented administrative endpoints. The endpoint itself failed to validate whether the incoming token had administrator privileges before performing database deletions.

---

## Lab 02 — Exploiting Server-Side Parameter Pollution in a Query String

- **Goal:** Access administrator's password reset features.
- **Vulnerability:** Server-Side Parameter Pollution (SSPP) in backend query parameter mapping.

### Proof of Concept (PoC)
1. Navigate to the password reset page.
2. The page sends a password reset request passing username. The internal request looks like:
   `/reset?username=INPUT&field=email`
3. Try polluting parameters by injecting an encoded parameter divider (`%26` / `&`):
   `username=administrator%26field=password`
4. The backend interprets the request as:
   `/reset?username=administrator&field=password&field=email`
5. If the server evaluates parameters sequentially (where the first `field` value overrides subsequent ones), it resets the password instead of email verification.
6. Retrieve the token or change password to access the administrator account.

### Why It Works
The user input is passed directly to the query string of the internal API. Lack of input sanitization allows the introduction of parameter separators (`&`), which override the developer's default configuration parameters on the server side.

---

## Lab 03 — Finding and Exploiting an Unused API Endpoint

- **Goal:** Purchase the leather jacket for a lower price.
- **Vulnerability:** Exposed but unused HTTP methods (`PATCH`) on endpoints.

### Proof of Concept (PoC)
1. Add the jacket to the cart and view product details.
2. Observe the API request returning product details: `GET /api/products/1/price`.
3. Send this request to Burp Repeater and swap the HTTP method to `PATCH`.
4. Change the `Content-Type` header to `application/json`.
5. Supply the JSON parameter body updating price:
   ```json
   {
     "price": 0
   }
   ```
6. Submit the request. If it returns 200 OK, complete checkout.

### Why It Works
The routing rules map the `PATCH` method to a database update function. While the front-end user interface never utilizes the `PATCH` method, the route remains active, exposed, and vulnerable to unauthorized price manipulation.

---

## Lab 04 — Exploiting a Mass Assignment Vulnerability

- **Goal:** Buy the leather jacket using a 100% off coupon.
- **Vulnerability:** Mass assignment during product checkout updates.

### Proof of Concept (PoC)
1. Add the jacket to your cart and checkout.
2. In Burp, observe the GET details response containing product structures:
   ```json
   {
     "id": 1,
     "name": "leather jacket",
     "price": 133700,
     "chosen_discount": {
       "percentage": 0,
       "code": "none"
     }
   }
   ```
3. Send the checkout update `POST` request to Repeater and inject the discount parameter:
   ```json
   {
     "id": 1,
     "chosen_discount": {
       "percentage": 100,
       "code": "ALL_FREE"
     }
   }
   ```
4. Place the order.

### Why It Works
The backend database model binding framework imports all request fields directly. An attacker can append non-exposed fields (such as nested discount arrays) to manipulate model values.

---

## Lab 05 — Exploiting Server-Side Parameter Pollution in a REST URL

- **Goal:** Reset administrator's password.
- **Vulnerability:** Path Traversal injection into REST URL mapping.

### Proof of Concept (PoC)
1. Go to the password reset/change page.
2. The server calls an internal API passing username in the path:
   `/api/users/INPUT/password`
3. Try injecting directory traversal symbols into the username field:
   `username=carlos/../administrator`
4. The internal API translates the target path to:
   `/api/users/carlos/../administrator/password` which resolves to `/api/users/administrator/password`.
5. Submit the password update request to modify the administrator's password.

### Why It Works
The backend uses string formatting to construct REST paths rather than sanitizing input blocks against traversal sequences. This allows path traversal injections to redirect endpoint routing dynamically.
