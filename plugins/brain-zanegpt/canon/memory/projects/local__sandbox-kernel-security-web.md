# local/sandbox-kernel-security-web — lessons

Project: local/sandbox-kernel-security-web. Newest first.

---

## E1 — each output context has one encoder that is safe and intact
- Date: 2026-09-28
- Project: local/sandbox-kernel-security-web
- Tags: [security][web][xss][encoding]
- What: Applied the ideas kernel that XSS defence is output encoding matched to the context the data lands in, with CSP as a backstop. The claim reproduced: every encoder failed in some context, and the safe choice depended on both blocking injection and keeping benign text intact.
- Why built: brain train gap listed the kernel as unapplied, and memory had no XSS entry. The kernel rests on the OWASP cheat sheet and had never been exercised.
- Design: Five output contexts (HTML body, double-quoted attribute, unquoted attribute, single-quoted JS string inside a script element, and an href) and six encoders (none, HTML entity escape, naive JS escape of quotes and backslash, JS hex escape of every non-alphanumeric character, URL component encoding, and HTML escape plus an http/https/relative scheme allow-list). 13 payloads and 4 benign strings. Rendered documents were parsed with Python's html.parser; script bodies were checked for a single intact string literal; hrefs were checked for a javascript: scheme after stripping tabs and newlines. CSP was modelled as script-src 'self' without unsafe-inline.
- Got right: Scoring benign round-trips beside injections. URL encoding blocked every payload in every context and looks perfect until its 0 of 4 intact benign strings show it breaks the output.
- Where/why it failed: HTML escaping blocked all 13 payloads in the body and quoted attribute with 4 of 4 benign intact, but let 6 through in an unquoted attribute (spaces are not escaped), let 3 javascript: URLs through in href, and inside the JS string it blocked everything while keeping only 1 of 4 benign strings intact, because script text is not entity-decoded. Naive JS escaping let `</script><script>` through in the JS string. JS hex escaping was the only encoder that was both safe and intact in the JS string. For href, only HTML escaping plus a scheme allow-list was safe with 4 of 4 intact. No encoder made the unquoted attribute both safe and intact. On unencoded body output, CSP blocked the 3 script-bearing injections and let through 2 markup-only ones, `<form action>` and `<base href>`.
- Fix: Pick the encoder per context: HTML entities for body and quoted attributes, JS hex escapes inside script strings, HTML escaping plus a scheme allow-list for URLs, and always quote attributes. Add CSP on top, and set base-uri and form-action as well as script-src.
- Why this fix: Each context is parsed by different rules, so an encoder can be safe in one and exploitable or destructive in another. CSP's script-src only governs script execution, so markup injection passes it.
- Rule of thumb: XSS encoding must match the landing context and keep benign text intact: HTML escaping is safe in body and quoted attributes but leaks 6 of 13 payloads in an unquoted attribute and 3 javascript: URLs in href, and inside a script string it is safe but corrupts 3 of 4 benign strings (JS hex escaping is the one safe, intact choice there); CSP script-src blocked 3 unencoded body injections and passed the 2 markup-only ones.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b04.py loop 17 in Pappydapimp69/Brain, deterministic. Observed: the injection and benign-intact grid for 6 encoders by 5 contexts, and CSP blocking 3 and passing 2. Assumed: Python's html.parser stands in for a browser's HTML5 parser; the two differ on some malformed markup this corpus does not include.
- Composed: ideas:SECURITY/web/xss/xss-defense-is-context-matched-encoding-csp-is-a-backstop-not-the-fix
- Link: session 2026-09-28, brain train gap batch 4 loop 17
- Sandbox: sandboxes/2026-09-28__train-gap-b04.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

