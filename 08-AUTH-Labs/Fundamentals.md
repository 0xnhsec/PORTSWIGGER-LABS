# Authentication Vulnerabilities Fundamentals

Authentication is the process of verifying the identity of a user or client. Broken or weak authentication mechanisms allow attackers to compromise user accounts and take control of administrative systems.

---

## Authentication vs. Authorization

```
Authentication = "Who are you?" (Verifying identity, e.g., credentials check)
Authorization  = "What are you allowed to do?" (Checking permissions once authenticated)
```

---

## Core Authentication Categories

Authentication is typically validated using three factors:
1. **Knowledge Factor (Something you know):** Passwords, PINs, security questions.
2. **Possession Factor (Something you have):** Smart cards, hardware tokens, phone (SMS/Authenticator apps).
3. **Inherence Factor (Something you are):** Biometrics (fingerprints, facial recognition).

---

## Common Authentication Vulnerabilities

### 1. Username Enumeration
The application behaves differently depending on whether a submitted username is valid or invalid.
- *Indicators:*
  - Different error messages (e.g. "Invalid username" vs "Incorrect password").
  - Different HTTP response codes.
  - Measurable response time differences (timing attacks).
  - Register/signup page saying "Username already taken".

### 2. Vulnerabilities in Multi-Factor Authentication (MFA)
- *2FA Bypass via State Bypasses:* The server prompts the user for 2FA on page 2 after submitting the password on page 1. However, the user is already treated as logged in before verifying the code, allowing attackers to access `/my-account` directly.
- *2FA Code Brute-Forcing:* Codes (typically 4 or 6 digits) are generated without rate-limiting on the submission endpoint, permitting complete brute-force searches in minutes.

### 3. Session Fixation & Cookie Manipulation
- *Insecure Session Lifecycle:* The session ID does not change upon successful login.
- *Predictable Session Tokens:* Session cookies are generated using guessable variables (e.g. MD5 hash of timestamp or username).

---

## Defensive Strategies

- **Generic Error Messages:** Always return the exact same generic error string (e.g., *“Invalid username or password”*) with matching HTTP status codes.
- **Constant Response Time:** Ensure database lookup structures take a constant amount of time regardless of whether a username is valid or invalid to prevent timing attacks.
- **Robust Rate Limiting:** Enforce locks or captcha blocks after multiple failed attempts. Rate limit based on IP ranges, sessions, and usernames to block distributed brute-force attacks.
- **True Multi-Factor Authentication:** Implement MFA utilizing Time-based One-time Password (TOTP) protocols (e.g. Google Authenticator) instead of SMS or email, and validate steps chronologically.
