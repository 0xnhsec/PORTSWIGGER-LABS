# Broken Access Control Labs 01-13 — Proof of Concept Writeups

This document contains structured Proof of Concept (PoC) writeups for Broken Access Control (BAC) Labs 01 to 13 from the PortSwigger Web Security Academy.

---

## Lab 01 — Unprotected Admin Functionality

- **Vulnerability Type:** Vertical BAC (robots.txt disclosure)
- **Goal:** Access admin panel and delete user `carlos`.

### Proof of Concept (PoC)
1. Access `/robots.txt` in the root URL.
2. Note the directive:
   ```
   Disallow: /administrator-panel
   ```
3. Navigate to `/administrator-panel` directly.
4. Click "Delete carlos".

### Why It Works
The administrative panel does not enforce session privilege checks. Developers mistakenly relied on `robots.txt` to "hide" the path from users, which is a security-by-obscurity failure.

---

## Lab 02 — Unprotected Admin Functionality with Unpredictable URL

- **Vulnerability Type:** Vertical BAC (Hardcoded path in JavaScript)
- **Goal:** Access admin panel and delete user `carlos`.

### Proof of Concept (PoC)
1. Inspect the homepage source code (or DevTools console).
2. Locate the loaded JavaScript file containing a conditional routing logic:
   ```javascript
   if (isAdmin) {
       // link to '/admin-lmn62t'
   }
   ```
3. Access the unpredictable path `/admin-lmn62t` directly.
4. Delete user `carlos`.

### Why It Works
Client-side JavaScript files are public. Obfuscating the URL within a conditional block on the client side does not protect the resource; the backend failed to perform access authorization on the `/admin-lmn62t` endpoint.

---

## Lab 03 — User Role Controlled by Request Parameter

- **Vulnerability Type:** Vertical BAC (Parameter Tampering - Cookie)
- **Goal:** Access admin panel at `/admin` and delete user `carlos`.

### Proof of Concept (PoC)
1. Log in with standard credentials `wiener:peter`.
2. Observe the request cookies in Burp Suite: `Admin=false; session=...`
3. Modify the cookie to `Admin=true` and navigate to `/admin`.
4. Delete user `carlos`.

### Why It Works
The server trusts client-side cookie values (`Admin=true`) directly to determine administrative privileges, failing to perform server-side checks.

---

## Lab 04 — User Role Can Be Modified in User Profile

- **Vulnerability Type:** Vertical BAC (JSON Parameter Pollution / Mass Assignment)
- **Goal:** Elevate privileges, access admin panel, and delete `carlos`.

### Proof of Concept (PoC)
1. Log in with standard credentials `wiener:peter`.
2. Navigate to user settings, change your email, and intercept the request in Burp.
3. Observe the JSON structure:
   ```json
   {
     "username": "wiener",
     "email": "wiener@normal-user.net"
   }
   ```
4. Inject a role parameter:
   ```json
   {
     "username": "wiener",
     "email": "wiener@normal-user.net",
     "roleid": 2
   }
   ```
5. Submit, navigate to `/admin`, and delete user `carlos`.

### Why It Works
The user profile update API is vulnerable to mass assignment. It binds input fields directly to the user model without filtering out administrative columns like `roleid`.

---

## Lab 05 — User ID Controlled by Request Parameter

- **Vulnerability Type:** Horizontal BAC (IDOR in URL Parameter)
- **Goal:** Retrieve Carlos's API key.

### Proof of Concept (PoC)
1. Log in with credentials `wiener:peter`.
2. Click "My Account" and observe the URL: `/my-account?id=wiener`.
3. Change the `id` parameter to `/my-account?id=carlos`.
4. Retrieve the API key from the page output.

### Why It Works
The backend displays the user account template matching the `id` parameter directly from database queries, without validating whether the active session identifier matches the owner of that user record.

---

## Lab 06 — User ID Controlled by Request Parameter with Unpredictable User IDs

- **Vulnerability Type:** Horizontal BAC (IDOR with Enumerable GUID)
- **Goal:** Find Carlos's GUID, access his account page, and retrieve his API key.

### Proof of Concept (PoC)
1. Navigate to a blog post written by `carlos`.
2. Inspect the author link to retrieve Carlos's GUID from the URL:
   `href="/author?id=85a12d...4a"`
3. Navigate to `/my-account?id=85a12d...4a`.
4. Copy Carlos's API key.

### Why It Works
Even though the application uses unpredictable GUIDs (UUIDs) to secure user objects, the IDOR vulnerability still exists because these GUIDs are exposed publicly in metadata areas like blog post authors.

---

## Lab 07 — User ID Controlled by Request Parameter with Data Leakage in Redirect

- **Vulnerability Type:** Horizontal BAC (Information Leak in 302 Redirect Response)
- **Goal:** Retrieve Carlos's API key.

### Proof of Concept (PoC)
1. Intercept a request to `/my-account?id=carlos` using Burp Suite.
2. Note that the browser receives a `302 Found` redirecting to `/login`.
3. Inspect the response body of the `302 Found` redirect in Burp Suite.
4. Locate Carlos's API key rendered inside the HTML payload.

### Why It Works
The backend checks permissions and generates a redirect, but fails to stop executing the page-building logic. The application generates the full HTML template containing sensitive database results before issuing the redirect header.

---

## Lab 08 — User ID Controlled by Request Parameter with Password Disclosure

- **Vulnerability Type:** Horizontal to Vertical Escalation (Password Disclosure)
- **Goal:** Retrieve the administrator password and delete user `carlos`.

### Proof of Concept (PoC)
1. Log in with credentials `wiener:peter`.
2. Navigate to `/my-account?id=administrator`.
3. Inspect the source code and locate the pre-filled value of the password input field:
   `value="admin-password-here"`
4. Log out and log back in as `administrator`.
5. Access `/admin` and delete `carlos`.

### Why It Works
The profile page populates the password input field dynamically for the requested user profile ID without checking if the requester is the resource owner.

---

## Lab 09 — Insecure Direct Object References

- **Vulnerability Type:** IDOR (Predictable Static Files)
- **Goal:** Retrieve Carlos's password from chat logs.

### Proof of Concept (PoC)
1. Start a live chat session.
2. Click "View transcript" and note the path: `/download-transcript?file=3.txt`.
3. Enumerate the files by requesting `/download-transcript?file=1.txt` or `2.txt`.
4. Locate a transcript where Carlos is told his login credentials by the support bot.
5. Log in as `carlos` and delete `wiener`.

### Why It Works
File system requests are fetched using predictable filenames (`1.txt`, `2.txt`) without access controls, exposing historical session chat transcripts.

---

## Lab 10 — URL-based Access Control Can Be Circumvented

- **Vulnerability Type:** Vertical BAC (Reverse Proxy/WAF Bypass)
- **Goal:** Access admin panel at `/admin` and delete user `carlos`.

### Proof of Concept (PoC)
1. Request `/admin` -> Returns `403 Forbidden` (Front-end proxy blocks `/admin`).
2. Add a custom routing header to access the endpoint through the root:
   ```http
   GET / HTTP/2
   X-Original-URL: /admin/delete?username=carlos
   ```
3. Submit the request.

### Why It Works
The front-end reverse proxy restricts `/admin` but permits `/`. By passing `X-Original-URL`, the request reaches the backend application, which interprets the header to rewrite the internal route, bypassing front-end WAF limits.

---

## Lab 11 — Method-based Access Control Can Be Circumvented

- **Vulnerability Type:** Vertical BAC (HTTP Method Bypass)
- **Goal:** Elevate privileges of user `wiener`.

### Proof of Concept (PoC)
1. Log in as `administrator` and promote a user, intercepting the request:
   `POST /admin-roles` with data `username=carlos&action=upgrade`
2. Log in as `wiener`.
3. Try sending the same request -> Returns 403.
4. Modify the request method to GET or POST with parameter overrides:
   ```http
   GET /admin-roles?username=wiener&action=upgrade HTTP/2
   ```

### Why It Works
The authorization middleware checks permissions strictly on `POST` requests to `/admin-roles`, but the application router maps the handler to both `POST` and `GET` requests without validating authorization on the `GET` route.

---

## Lab 12 — Multi-step Process with No Access Control on One Step

- **Vulnerability Type:** Vertical BAC (Multi-Step Bypass)
- **Goal:** Promote `wiener` to administrator.

### Proof of Concept (PoC)
1. Log in as `administrator`.
2. Promote a user and capture the multi-step flow in Burp history:
   - Step 1: `POST /admin-roles` with `username=carlos&action=upgrade` (Returns page asking for confirmation).
   - Step 2: `POST /admin-roles` with `username=carlos&action=upgrade&confirmed=true`.
3. Log in as `wiener` and submit Step 2 payload directly:
   ```http
   POST /admin-roles HTTP/2
   ...
   username=wiener&action=upgrade&confirmed=true
   ```

### Why It Works
The application validates authorization only on the first step of the promotion request. The final confirmation step (step 2) implicitly trusts the request, assuming step 1 was already validated.

---

## Lab 13 — Referer-based Access Control

- **Vulnerability Type:** Vertical BAC (Referer Header Spoofing)
- **Goal:** Promote `wiener` to administrator.

### Proof of Concept (PoC)
1. Log in as `wiener`.
2. Trigger the promotion request endpoint (e.g. `/admin-roles?username=wiener&action=upgrade`).
3. Intercept the request and inject the Referer header pointing to the admin panel:
   ```http
   GET /admin-roles?username=wiener&action=upgrade HTTP/2
   Referer: https://<lab-id>.web-security-academy.net/admin
   ```

### Why It Works
The server authorization module trusts the `Referer` header to distinguish whether a request is authorized, allowing users to bypass checks by modifying their browser referrer strings in Burp.
