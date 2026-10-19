# Security notes

Northbridge Bank IT PMO board is a static, single-file demo (`index.html`) for a **fictitious** bank. It has no server and stores nothing. The only outbound call is the optional "New project request" POST to FormSubmit.

## Threat model (STRIDE)

| Threat | Where | Control in this page |
|---|---|---|
| **Spoofing** | Bots or scripts posting fake requests to the PMO inbox via FormSubmit | Honeypot field (fake success, nothing sent); minimum 3 s fill time; 30 s cooldown and max 5 sends per page load; strict email validation |
| **Tampering** | DOM tampering of `<select>` values or oversized inputs flowing into `className`, ARIA labels or emails | `sanitizeProject()` allow-lists stage/priority/RAG/department, clamps numbers/dates, caps lengths, strips control and bidi-override characters |
| **Repudiation** | No user identity or audit trail | Accepted for a demo; nothing persists past a refresh |
| **Information disclosure** | Referrer leakage; PMO address visible in source; credentials sent cross-site | `referrer` meta + `referrerPolicy: 'no-referrer'`; `credentials: 'omit'`; config comment says to use FormSubmit's random-string alias instead of the raw address |
| **Denial of service** | Hanging requests; email flooding | 15 s `AbortController` timeout; cooldown and per-load cap (client-side only, see residual risks) |
| **Elevation (XSS / injection)** | User text rendered into the board; email header injection via `_subject` | DOM built only with `textContent`/`createElement(NS)`; no HTML-string sinks (enforced by CI grep); strict CSP with hashed inline script/style, `default-src 'none'`, `connect-src` limited to formsubmit.co, `form-action 'none'`, `base-uri 'none'`; Trusted Types (`require-trusted-types-for 'script'`, no policies); CR/LF stripped from every single-line field |
| **Clickjacking** | Page framed by another site | `frame-ancestors` is ignored in a meta CSP, so a script overlay blocks the UI when framed |

## Residual risks

- **All abuse controls are client-side.** Anyone can call FormSubmit directly, and a refresh resets the cooldown and cap. Real protection needs FormSubmit's own settings (captcha, domain allow-list) or a server.
- **A meta CSP can't set `frame-ancestors`, `report-uri` or other HTTP-only headers.** GitHub Pages can't add custom headers either. When hosted behind a proxy, add `Content-Security-Policy: frame-ancestors 'none'`, `X-Content-Type-Options: nosniff` and HSTS as HTTP headers.
- **Trusted Types is enforced only in Chromium-based browsers.** Other browsers rely on CSP and the no-sink coding rule.
- **FormSubmit is a third party** and sees all submitted request data. Don't put confidential information in requests.

## Maintenance

- After editing the inline `<script>` or `<style>`, run `python3 scripts/csp-hash.py`. CI fails on a stale hash.
- CI also greps for storage APIs, external resources and HTML-string sinks (`innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval(`, `new Function`), and runs gitleaks.
