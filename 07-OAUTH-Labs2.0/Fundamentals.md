# OAuth 2.0 & OIDC Vulnerabilities Fundamentals

OAuth is an authorization framework that enables applications to request limited access to user accounts on other services (the OAuth providers) without exposing credentials. OpenID Connect (OIDC) is an identity layer built on top of OAuth 2.0 to provide single sign-on (SSO).

```
Client Application   = The web app requesting access to user data.
Resource Owner       = The user who owns the data.
OAuth Provider       = The service managing authentication and hosting the user data API.
```

---

## The Authorization Code Flow vs. Implicit Flow

### 1. Authorization Code Flow (Recommended)
1. **Request:** Client redirects the user to the OAuth `/authorization` endpoint.
2. **Consent:** User logs in to the OAuth provider and grants permissions.
3. **Authorization Code:** Provider redirects user back to the client callback URL (e.g. `/callback?code=CODE`).
4. **Token Exchange:** The client sends the `code` along with its `client_secret` directly to the provider backend (server-to-server) to exchange it for an `access_token`.

### 2. Implicit Flow (Legacy/Flawed)
1. **Request:** Client redirects user to `/authorization`.
2. **Consent:** User logs in and grants permissions.
3. **Access Token:** Provider redirects user back via a URL fragment containing the token: `/callback#access_token=TOKEN`.
4. **Usage:** The client UI extracts the token from the fragment and sends it in a POST request to authenticate the user's session.

---

## Core Vulnerability Vectors

### 1. Improper Implementation of the Implicit Flow
In the Implicit flow, the browser receives the `access_token` in the URL fragment and forwards it to the backend server to create a session cookie.
- **Flaw:** If the backend trusts the email/username parameters sent in the body alongside the token without validating the token's signature, attackers can intercept the POST request and swap parameters to log in as any user.

### 2. Forced Profile Linking (CSRF on OAuth Bindings)
Many sites allow users to link social logins (OAuth) to their existing local profiles.
- **Flaw:** If the client application initiates the linking redirect without validating a unique, unpredictable `state` parameter, it is vulnerable to CSRF.
- **Attack:** An attacker intercepts their own OAuth callback link and induces a logged-in victim to visit it. The victim's local account is then linked to the attacker's social profile.

### 3. Open `redirect_uri` Validation
During authorization requests, the client specifies a `redirect_uri` parameter indicating where the provider should send the authorization code or access token.
- **Flaw:** If the OAuth provider fails to validate the `redirect_uri` against a strict allowlist (e.g. accepting wildcards or subdomains), attackers can manipulate the parameter to redirect authentication codes to their own domains.

### 4. Dynamic Client Registration Vulnerabilities
OpenID Connect allows client applications to register dynamically with the OpenID Provider using endpoints like `/register`.
- **Flaw:** Attackers can submit registration requests containing parameters like `logo_uri` pointing to internal resources (e.g. `http://169.254.169.254/latest/meta-data/`). The provider server attempts to fetch the logo, creating a Server-Side Request Forgery (SSRF) vulnerability.

### 5. `postMessage` Access Token Theft
Some applications use child windows or iframes to handle OAuth callbacks and pass access tokens back to the parent page via HTML5 `postMessage`.
- **Flaw:** If the callback script calls `postMessage(token, '*')` without specifying a strict destination origin, any open listening window can capture the token.
