# JWT Attacks Labs 01-08 — Proof of Concept Writeups

This document contains structured Proof of Concept (PoC) writeups for JSON Web Token (JWT) attack Labs 01 to 08 from the PortSwigger Web Security Academy.

---

## Lab 01 — JWT Authentication Bypass via Unverified Signature

- **Vulnerability:** Unverified signature.
- **Goal:** Access admin panel and delete `carlos`.

### Proof of Concept (PoC)
1. Log in to your account.
2. Intercept a request, send it to Burp Repeater, and check the JWT structure.
3. Decode the payload section and change `"sub": "wiener"` to `"sub": "administrator"`.
4. Leave the signature block exactly as is and submit the request.
5. The server accepts the token without validating the signature. Access `/admin` and delete `carlos`.

### Why It Works
The server decodes and trusts variables inside the JWT payload without verifying if the signature hash matches the header/payload contents.

---

## Lab 02 — JWT Authentication Bypass via Flawed Signature Verification (alg: none)

- **Vulnerability:** Signature verification bypass using the `none` algorithm.
- **Goal:** Access admin panel and delete `carlos`.

### Proof of Concept (PoC)
1. Intercept a request containing your session JWT.
2. Change the header algorithm property to `"alg": "none"`.
3. Change the payload `"sub"` value to `"administrator"`.
4. Delete the signature characters completely, but keep the trailing period (`.`):
   `Header.Payload.`
5. Send the request, open the admin panel, and delete `carlos`.

### Why It Works
The backend parser evaluates the `"alg"` parameter from the header. When it matches `none`, the parser disables signature verification checks, implicitly trusting the payload values.

---

## Lab 03 — JWT Authentication Bypass via Weak Signing Secret

- **Vulnerability:** Weak HMAC secret key.
- **Goal:** Brute force key, sign custom token as admin, and delete `carlos`.

### Proof of Concept (PoC)
1. Capture a valid JWT from the browser session.
2. Run a dictionary brute force tool (like `hashcat` or `jwt_tool.py`) with `rockyou.txt`:
   ```bash
   hashcat -m 16500 jwt.txt /usr/share/dict/rockyou.txt
   ```
3. Locate the verified secret key: `secret1`.
4. Generate a new JWT using `HS256` with payload `"sub": "administrator"`, signed using the key `secret1`.
5. Access `/admin` with the modified cookie and delete `carlos`.

### Why It Works
The server uses a weak, guessable HMAC key. Offline brute-forcing extracts the key, allowing attackers to sign arbitrary payloads.

---

## Lab 04 — JWT Authentication Bypass via jwk Header Injection

- **Vulnerability:** Public key injection via `jwk` header parameter.
- **Goal:** Sign custom token with your key and force the server to verify it.

### Proof of Concept (PoC)
1. Create a custom RSA key pair using Burp's JWT Editor extension.
2. Intercept a request containing the session JWT.
3. Modify the payload `"sub"` value to `"administrator"`.
4. Re-sign the token using the custom RSA key, and check the option to embed the public key inside the `"jwk"` header parameter.
5. Submit the request and delete `carlos`.

### Why It Works
The server trusts the public key embedded in the `"jwk"` header of the request to verify the token signature, rather than matching it against a pre-configured whitelist of authorized keys.

---

## Lab 05 — JWT Authentication Bypass via jku Header Injection

- **Vulnerability:** Key set URL redirection via `jku` header parameter.
- **Goal:** host custom JWKS and trigger verification redirect.

### Proof of Concept (PoC)
1. Generate a custom RSA key pair.
2. Expose the public JWK definition structure as a JSON file on the exploit server (e.g. `/jwks.json`).
3. Intercept your session JWT and change `"sub"` to `"administrator"`.
4. Add the `"jku"` parameter to the header pointing to the exploit server JSON:
   `"jku": "https://exploit-server.net/jwks.json"`
5. Sign the token with your private key and send it. Delete `carlos`.

### Why It Works
The server reads the `"jku"` parameter and fetches verification keys from the specified external URL. The server fails to validate that the host domain of the URL is trusted.

---

## Lab 06 — JWT Authentication Bypass via kid Header Path Traversal

- **Vulnerability:** Path traversal in `kid` parameter to bypass key location checks.
- **Goal:** Direct key checks to static empty files.

### Proof of Concept (PoC)
1. Intercept your session JWT.
2. Change the header parameter `"kid"` to point to `/dev/null` using path traversal:
   `"kid": "../../../../../../../dev/null"`
3. Change the payload `"sub"` to `"administrator"`.
4. Sign the token with a symmetric HMAC secret set to an empty byte string `""` or hex `00` (since `/dev/null` is empty, its content yields `""`).
5. Send the request and delete `carlos`.

### Why It Works
The server reads the `"kid"` (Key ID) parameter to load the signing key from the disk filesystem. Specifying a path traversal to `/dev/null` forces the server to read 0 bytes, matching the signature check against an empty string payload.

---

## Lab 07 — JWT Authentication Bypass via Algorithm Confusion

- **Vulnerability:** Algorithm confusion (asymmetric RS256 to symmetric HS256).
- **Goal:** Extract public key and sign HMAC token.

### Proof of Concept (PoC)
1. Fetch the server's public key (e.g., from `/jwks.json` or certificate files).
2. Format the public key string into a standard PEM format.
3. Change the JWT header to use `"alg": "HS256"`.
4. Modify the payload `"sub"` to `"administrator"`.
5. Sign the token using `HS256` (HMAC), supplying the raw text value of the retrieved public key as the symmetric key secret.
6. Submit the token and delete `carlos`.

### Why It Works
The server is configured to check tokens using the symmetric `HS256` code block if specified in the header. When executing `HS256`, it retrieves its internal verification key (which is the public key used for RS256 verification) and treats it as the HMAC secret key.

---

## Lab 08 — JWT Authentication Bypass via Algorithm Confusion with No Exposed Key

- **Vulnerability:** Algorithm confusion without an exposed public key endpoint.
- **Goal:** Calculate public key modulus from signed tokens and execute HMAC confusion.

### Proof of Concept (PoC)
1. Intercept two different valid JWTs signed by the server.
2. Extract the signatures and calculate the public key modulus $N$ by finding the greatest common divisor of multiple signature values.
3. Reconstruct the public key PEM file using the calculated modulus.
4. Modify the JWT header to `"alg": "HS256"`, change `"sub"` to `"administrator"`, and sign it with the calculated public key using `HS256` (HMAC).
5. Submit the request and delete `carlos`.

### Why It Works
Mathematical properties of RSA signatures permit attackers to compute the modulus $N$ offline if they capture multiple signed tokens. Once $N$ is known, the public key is reconstructed to perform an algorithm confusion bypass.
