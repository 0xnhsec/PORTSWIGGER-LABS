# XSS Hunting Methodology

A systematic approach to detecting and exploiting Cross-Site Scripting (XSS) in target applications.

---

## Mental Model

```
Console = Test and verify JavaScript behavior in YOUR browser (verification).
XSS     = Force the VICTIM'S browser to execute that JavaScript (exploit).

The browser console is not the end goal; it is a verification tool before crafting the exploit payload.
```

---

## Step 1 — Find Injection Points

Locate all entry points where user input is reflected in the HTTP response:

- Search bars / query parameters
- Comment / input form fields
- URL path segments
- HTTP headers (User-Agent, Referer, X-Forwarded-For)
- JSON body parameters
- URL fragments (`#hash`)
- File uploads (e.g., filename parameters)

**Testing approach:**
Inject a unique alphanumeric marker (e.g., `abcxyz123`) into parameters and inspect the source code of the response to see if and where it lands.

---

## Step 2 — Identify the Context

Once you find the marker in the response source (`Ctrl+F`), determine its HTML context:

| Reflected Context | Example | Action |
|---|---|---|
| **HTML Body** | `<p>abcxyz123</p>` | Inject `<script>` tag directly |
| **HTML Attribute** | `<input value="abcxyz123">` | Break out using double quotes `"` or single quotes `'` |
| **Href Attribute** | `<a href="abcxyz123">` | Use `javascript:` pseudoprotocol |
| **JS Single-Quote String** | `var x = 'abcxyz123'` | Break out using `'` and add operators/commands |
| **JS Double-Quote String** | `var x = "abcxyz123"` | Break out using `"` and add operators/commands |
| **Template Literal** | `` var x = `abcxyz123` `` | Inject `${alert(1)}` directly |
| **JSON Response** | `{"key":"abcxyz123"}` | Break out of the JSON string |

---

## Step 3 — Test the Vulnerability

Identify the source and sink within the JavaScript code. Look for sinks like:
- `element.innerHTML = ...`
- `document.write(...)`
- `eval(...)`
- `$(element).html(...)`

Verify execution manually in the console:
```javascript
// Test if innerHTML handles HTML tags correctly
document.getElementById('result').innerHTML = '<img src=x onerror=alert(1)>';
```

---

## Step 4 — Analyze Sanitization and Filters

Verify if characters are filtered or HTML-encoded:

| Encoded output | Meaning | Bypass strategy |
|---|---|---|
| `<` → `&lt;` | Angle brackets encoded | Use tag attributes/sinks that do not need brackets (e.g., JS context) |
| `"` → `&quot;` | Double quotes encoded | Try single quotes `'` or template literals |
| `'` → `\'` | Single quotes escaped | Check if backslash `\` itself can be escaped (`\\`) |
| Tag stripped | Blacklist filtering | Try alternative tags or obfuscation (e.g., `<scr<script>ipt>`) |
