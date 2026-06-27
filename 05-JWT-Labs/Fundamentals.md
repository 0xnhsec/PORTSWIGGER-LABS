# JSON Web Tokens (JWT) Fundamentals

JSON Web Token (JWT) is a stateless string-based token used by servers to recognize a user's identity without storing session state in a backend database. The token is sent to the client and included in subsequent API requests via the header:
`Authorization: Bearer <token>`

---

## JWT Structure

A JWT consists of three parts separated by periods (`.`):
`Header.Payload.Signature`

1. **Header:** Contains metadata about the token, such as the signing algorithm (`alg`: e.g., RS256, HS256, None) and key identifiers (`kid`).
2. **Payload:** Contains user claims and data (e.g., `"sub": "wiener"`, `"role": "user"`). This part is simply Base64URL-encoded and can be decoded/read by anyone.
3. **Signature:** Created by hashing the encoded Header and Payload using a server-side secret or private key. This ensures the integrity of the token and prevents unauthorized modification.

---

## Attack Surface

JWT attacks generally target verification flaws:
- **Algorithm Manipulation:** Swapping the header algorithm field to `None` (signature check bypass) or changing asymmetric algorithms (RS256) to symmetric (HS256) using public keys.
- **Weak HMAC Secrets:** Brute-forcing weak signing secrets using dictionaries like `rockyou.txt`.
- **Header Injection:** Injecting properties inside the header to alter verification routing:
  - `jwk` (JSON Web Key): Injecting self-signed public keys directly.
  - `jku` (JWK Set URL): Redirecting the server to fetch verifying keys from an attacker-controlled endpoint.
  - `kid` (Key ID): Exploiting path traversals (e.g. `../../../../dev/null`) to force verification against static empty strings or known local files.
