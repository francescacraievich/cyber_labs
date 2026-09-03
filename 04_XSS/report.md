# XSS Lab Report - OWASP Juice Shop

**Course:** [505MI] Cybersecurity Lab A.Y. 2025/2026  
**Author:** Francesca Craievich  
**Target:** OWASP Juice Shop  
**Tools:** Burp Suite Community Edition, Firefox with proxy, Docker  

---

## 1. Introduction

Cross-Site Scripting (XSS) is a web vulnerability (CWE-79) that allows an attacker to inject malicious scripts into web pages viewed by other users. This report documents the exploitation of two XSS challenges on OWASP Juice Shop: **DOM-based XSS** and **Reflected XSS**. These are non-persistent attacks that differ in how user input is processed: in the DOM-based variant the payload never leaves the browser, while in the Reflected variant it travels through the server before being rendered.

The Juice Shop instance was run in Docker with `NODE_ENV=unsafe` to enable all challenges:

```bash
docker run -e "NODE_ENV=unsafe" -p 3000:3000 bkimminich/juice-shop
```

Firefox was configured to proxy all traffic (including localhost) through Burp Suite on port 8080, with `network.proxy.allow_hijacking_localhost` set to `true` in `about:config`.

---

## 2. DOM-based XSS (Challenge 1)

### 2.1 Attack vector

The Juice Shop search functionality at `/#/search?q=...` reads the query parameter directly from the URL fragment and inserts it into the DOM without sanitization. Since the fragment (everything after `#`) is never sent to the server, the entire attack takes place client-side.

### 2.2 Exploitation

The following payload was entered in the search bar:

```
<iframe src="javascript:alert(`xss`)">
```

Resulting URL:

```
http://localhost:3000/#/search?q=<iframe src%3D"javascript:alert(`xss`)">
```

The browser parsed the `<iframe>` tag, executed the `javascript`, and displayed an alert box containing "xss". The green banner confirmed the challenge was solved.

![DOM XSS - alert triggered and challenge solved](img/DOM-xss.png)

### 2.3 Analysis with Burp Suite

Juice Shop is a Single Page Application (SPA) built with Angular: all routing happens client-side via the URL fragment (`#/...`), without full page reloads. When the search is performed, Angular reads the `q` parameter directly from the fragment and renders it into the DOM via `bypassSecurityTrustHtml()` (a `DomSanitizer` method that explicitly disables Angular's built-in XSS protection), without waiting for any server response. This is where the XSS executes.

A separate API call (`GET /rest/products/search?q=...`) is also made to fetch product results, and the payload does appear in that request. However, this is irrelevant to the XSS: the malicious code has already been parsed and executed by the browser during DOM rendering, independently of the API response (which simply returns `"data": []`).

This confirms the DOM-based nature of the vulnerability: the attack is entirely contained within the client-side code that reads the fragment and writes it into the DOM. The server never processes or reflects the payload in a way that contributes to the exploit.

![Burp Suite - DOM XSS: the search API request is visible but irrelevant to the exploit](img/DOM-xss-burp.png)

---

## 3. Reflected XSS (Challenge 2)

### 3.1 Attack vector

The order tracking feature at `/#/track-result?id=...` sends the tracking ID to the server via the REST API endpoint `/rest/track-order/{id}`. The server includes the `id` parameter in its JSON response, and the client-side code renders this value into the page without sanitization.

### 3.2 Exploitation

The payload `<iframe src="javascript:alert(`xss`)">` was placed in the order tracking ID. In Juice Shop the route `/#/track-order` redirects to the homepage, so the direct URL format was used:

```
http://localhost:3000/#/track-result?id=<iframe src="javascript:alert(`xss`)">
```

The payload triggered an alert, confirming the vulnerability.

![Reflected XSS - alert triggered on the order tracking page](img/reflected-xss.png)

### 3.3 Analysis with Burp Suite

Unlike the DOM XSS, Burp Suite's HTTP history clearly shows the payload traveling to and from the server. The request:

```
GET /rest/track-order/%3Ciframe%20src%3D%22javascript:alert(%60xss%60)%22%3E HTTP/1.1
Host: localhost:3000
```

The server response (HTTP 200 OK) reflects the payload in the `orderId` field:

```json
{
  "status": "success",
  "data": [
    {
      "orderId": "<iframe src=\"javascript:alert(`xss`)\">"
    }
  ]
}
```

The server does not build a dynamic HTML page in the traditional reflected XSS sense. Instead, it returns a JSON response that includes the unsanitized tracking ID. The client-side Angular code then takes this `orderId` value and inserts it into the DOM without encoding, which causes the browser to parse and execute the injected `<iframe>`.

![Burp Suite - server response reflecting the XSS payload in the orderId field](img/reflected-xss-burp.png)

---

## 4. DOM vs. Reflected XSS: Key Differences

From the user's perspective, both challenges appear identical: an `<iframe>` payload triggers an `alert()`. However, the underlying mechanisms are fundamentally different.

In the **DOM XSS** challenge, the input never leaves the browser. The URL fragment (`#/search?q=PAYLOAD`) is read by client-side JavaScript, which extracts the value and writes it directly into the page's DOM. The server has no awareness of the payload. The vulnerability lies entirely in the client-side code that uses `bypassSecurityTrustHtml()` to render unsanitized input into the DOM.

In the **Reflected XSS** challenge, the input travels through the server. The tracking ID is sent as a path parameter in an API request (`/rest/track-order/PAYLOAD`). The server processes this input and includes it in its JSON response. The server still "reflects" the attacker-controlled string back to the client. The client-side code then renders this reflected value into the DOM unsafely. 

---

## 5. Conclusions

The two challenges demonstrate how XSS attacks can exploit different parts of the application stack. DOM XSS is entirely client-side and invisible to server-side monitoring, while Reflected XSS involves the server echoing unsanitized input back to the client. 

---

> **Disclosure:** An LLM (Claude) was used to assist with the organization and formatting of this report.
