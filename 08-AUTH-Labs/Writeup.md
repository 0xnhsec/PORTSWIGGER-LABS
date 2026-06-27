# Authentication Labs 01-14 — Proof of Concept Writeups

This document contains structured Proof of Concept (PoC) writeups for Authentication (AUTH) Labs 01 to 14 from the PortSwigger Web Security Academy.

---

## Lab 01 — Username Enumeration via Different Responses

- **Goal:** Enumerate valid username, brute-force password, and log in.
- **Vulnerability:** Distinct error messages for invalid usernames and incorrect passwords.

### Proof of Concept (PoC)
1. Run a dictionary attack against the username login field.
2. Observe error differences:
   - Invalid username returns: `Invalid username`
   - Valid username returns: `Incorrect password`
3. Identify the valid user, then run a dictionary attack on the password field for that user to retrieve the credentials.

---

## Lab 02 — 2FA Simple Bypass

- **Goal:** Bypass 2FA verification to log in as `carlos`.
- **Vulnerability:** Missing 2FA validation state enforcement on target pages.

### Proof of Concept (PoC)
1. Log in with standard credentials `wiener:peter`.
2. Observe the page redirects to `/login2` prompting for 2FA.
3. Instead of completing 2FA, directly navigate to the endpoint:
   `GET /my-account`
4. The page loads successfully, bypassing the 2FA prompt.

---

## Lab 03 — Password Reset Broken Logic

- **Goal:** Reset Carlos's password and log in.
- **Vulnerability:** Password reset endpoint trusts user-controlled query string parameters.

### Proof of Concept (PoC)
1. Trigger a password reset for your account and open the email link.
2. In the reset page form submission request, observe parameters:
   `POST /password-reset?temp-token=TOKEN` with body `username=wiener&new-password-1=123&new-password-2=123`
3. Modify the POST body parameter `username=wiener` to `username=carlos`.
4. Submit the request. Carlos's password resets to `123`.

---

## Lab 04 — Username Enumeration via Subtly Different Responses

- **Goal:** Enumerate username, crack password, and log in.
- **Vulnerability:** Subtle differences (e.g. typos, whitespace, or layout elements) in error output.

### Proof of Concept (PoC)
1. Intercept login responses in Burp Intruder.
2. Attack the username field and verify length/content variations.
3. Locate the single response that includes a minor layout difference (e.g., an extra space or period in the error notification banner). This marks the valid username.
4. Brute force the password for that valid user.

---

## Lab 05 — Username Enumeration via Response Timing

- **Goal:** Enumerate username using timing discrepancies.
- **Vulnerability:** The password hashing algorithm is executed only when the username is valid.

### Proof of Concept (PoC)
1. Run `lab5-auth.py` script against the target login page.
2. The script sends requests with very long passwords (`a` * 100).
3. Monitor response latency:
   - Invalid username returns instantly (~100ms) because the server rejects the request immediately.
   - Valid username takes significantly longer (~500ms+) because the server hashes the long password.
4. Identify the valid user and brute-force the password.

---

## Lab 06 — Broken Brute-force Protection, IP Block

- **Goal:** Bypass IP-based rate limiting to brute force credentials.
- **Vulnerability:** IP lockout tracking reset conditions.

### Proof of Concept (PoC)
1. Note that the server blocks the IP after 3 failed login attempts.
2. Alternate requests: Send 2 brute-force attempts for the target user, followed by 1 successful login request for your own attacker account.
3. The successful login resets the failed attempts counter, allowing indefinite brute force.
4. (Alternative: Spoof client IP header fields like `X-Forwarded-For: 1.1.1.X` in Intruder).

---

## Lab 07 — Username Enumeration via Account Lock

- **Goal:** Enumerate usernames using lockout responses.
- **Vulnerability:** Account locking provides distinct error signals.

### Proof of Concept (PoC)
1. Send 5 consecutive failed logins for each candidate username.
2. Observe error message variations:
   - Standard response: `Invalid username or password`
   - Locked user response: `Account locked due to too many attempts`
3. Identify the locked username, wait for the lock to expire, and brute-force the password.

---

## Lab 08 — 2FA Broken Logic

- **Goal:** Bypass 2FA checks to log in as `carlos`.
- **Vulnerability:** The 2FA verify cookie tracks username state independently of the login session.

### Proof of Concept (PoC)
1. Enter credentials for `carlos` (or trigger his login sequence to set target cookies).
2. Intercept the 2FA submission request and change the verification cookie identifier:
   `Cookie: verify=carlos`
3. Brute force the 4-digit MFA code on the `/login2` endpoint using Intruder.
4. Since the check uses the `verify` cookie to associate the code, you will successfully authenticate as Carlos.

---

## Lab 09 — Brute-forcing a Stay-logged-in Cookie

- **Goal:** Hijack Carlos's session using cookies.
- **Vulnerability:** Cookie structure is predictable: `base64(username:md5(password))`.

### Proof of Concept (PoC)
1. Run `labs9-auth.sh` script to convert a wordlist of standard passwords into MD5 hashes, format them as `carlos:hash`, and base64-encode them.
2. Use Burp Intruder to iterate through the generated base64 cookies.
3. The server validates the decoded cookie values directly, executing session login.

---

## Lab 10 — Offline Password Cracking

- **Goal:** Retrieve credentials from compromised data logs.
- **Vulnerability:** Weak hashing algorithms used to store local passwords.

### Proof of Concept (PoC)
1. Identify the hash format (e.g. bcrypt, SHA-256, MD5) from the database dump.
2. Launch an offline cracking utility:
   ```bash
   hashcat -m 1800 hashes.txt /usr/share/dict/rockyou.txt
   ```
3. Copy the cracked plaintext password and log in.

---

## Lab 11 — Password Reset Poisoning via Middleware

- **Goal:** Capture the password reset token of `carlos`.
- **Vulnerability:** Host header injection in password reset links.

### Proof of Concept (PoC)
1. Intercept the password reset request for `carlos`.
2. Add a host redirection header parameter:
   ```http
   POST /password-reset HTTP/2
   Host: target.com
   X-Forwarded-Host: exploit-server.net
   ```
3. The server generates a link using the header variable: `https://exploit-server.net/password-reset?token=TOKEN`
4. The victim clicks the link in their email, forwarding the token to your exploit logs. Use the token to reset the password.

---

## Lab 12 — Password Brute-force via Password Change

- **Goal:** Brute-force Carlos's password.
- **Vulnerability:** The password change form does not enforce rate limiting.

### Proof of Concept (PoC)
1. Navigate to the password change page.
2. Intercept the request:
   `POST /change-password` with `username=carlos&current-password=PASSWORD`
3. Run a dictionary brute force against the `current-password` parameter.
4. The endpoint does not block requests, yielding the valid password.

---

## Lab 13 — Broken Brute-force Protection, Multiple Credentials per Request

- **Goal:** Bypass brute force detection by sending multi-parameter arrays.
- **Vulnerability:** Login API handles password lists sequentially in single requests.

### Proof of Concept (PoC)
1. Intercept the login POST request and convert the parameters to a JSON array structure:
   ```json
   {
     "username": "carlos",
     "password": ["123456", "password", "qwerty", "admin", ...]
   }
   ```
2. The server iterates over the password list. A successful login returns a `302 redirect` or valid token, bypassing brute-force rate-limiting filters.

---

## Lab 14 — 2FA Bypass Using Brute-force Attack

- **Goal:** Brute force the 2FA verification page.
- **Vulnerability:** No rate limiting or lockouts on the `/login2` MFA submission endpoint.

### Proof of Concept (PoC)
1. Log in to the target account with known credentials.
2. Navigate to `/login2` and intercept the MFA code POST request.
3. Run `labs14-session-auth.py` script to multi-thread the brute-force extraction of the 4-digit code (from `0000` to `9999`) without trigger blockouts.
4. Extract the successful session cookie.
