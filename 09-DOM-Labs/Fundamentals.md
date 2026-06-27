# DOM-Based Vulnerabilities & DOM Clobbering Fundamentals

Document Object Model (DOM) vulnerabilities arise when an application's client-side JavaScript processes user-controlled data (the **Source**) in an unsafe way, passing it directly to a sensitive execution point (the **Sink**).

---

## The Source-to-Sink Taint Flow

### 1. Sources
A source is a JavaScript property that can be controlled or influenced by an external request or user input.
- *Common Sources:*
  - `location.search` (URL query parameters)
  - `location.hash` (URL fragment)
  - `document.referrer` (HTTP Referer header value)
  - `document.cookie` (Cookie parameters)
  - `window.name` (Cross-domain window name variables)
  - `postMessage` (Web messaging data)

### 2. Sinks
A sink is a built-in browser function or DOM object that executes or renders data passed to it. If untrusted data enters a sink without sanitization, it triggers code execution or logical bypasses.
- *Common Sinks:*
  - **DOM XSS:** `document.write()`, `element.innerHTML`, `eval()`
  - **Open Redirection:** `location.href`, `location.replace()`
  - **Cookie Manipulation:** `document.cookie`
  - **Script Injection:** `script.src`

```
[Unsafe Source: location.hash] ──→ [Data flow without verification] ──→ [Dangerous Sink: document.write]
```

---

## DOM Clobbering

DOM Clobbering is an advanced HTML injection technique where an attacker injects markup to overwrite global JavaScript variables or properties of objects. This is particularly useful when standard XSS is blocked by WAFs, but the application permits HTML inputs with specific attributes like `id` or `name`.

### Overwriting Global Variables
In JavaScript, DOM elements with an `id` or `name` attribute are automatically exposed as properties on the global `window` object.
For example, injecting:
```html
<a id="myVariable"></a>
```
Creates `window.myVariable` pointing to that anchor element.

### Overwriting Object Properties
You can chain elements with identical `id` attributes to form a DOM collection, and use the `name` attribute to map properties:
```html
<a id="someObject"></a>
<a id="someObject" name="url" href="javascript:alert(1)"></a>
```
If JavaScript does:
```javascript
let target = window.someObject || {};
let scriptUrl = target.url; // Resolves to "javascript:alert(1)"
```
The attacker has successfully "clobbered" `someObject.url` to inject their own source path.

### Bypassing Sanitization Filters (e.g. htmlJanitor)
Some client-side sanitizers iterate through an element's `attributes` collection to sanitize parameters:
```javascript
for (let i = 0; i < element.attributes.length; i++) {
    // Sanitize attributes
}
```
If an attacker injects:
```html
<form onclick="alert(1)"><input id="attributes"></form>
```
The `<input>` tag with `id="attributes"` overwrites the form's `attributes` property. Since the properties of the input do not contain a `length` property, the loop terminates immediately, leaving the parent `<form>`'s event handler (`onclick="alert(1)"`) untouched.
