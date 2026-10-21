# Pappydapimp69/Chat — lessons

Project: Pappydapimp69/Chat. Newest first.

---

## E2 — webview must not hijack redirects
- Date: 2026-08-30
- Project: Pappydapimp69/Chat
- Tags: [browser][webview][auth]
- What: An embedded WebView routed every navigation to a non-allowlisted host out to the system browser. Sign-in failed with a bare error page.
- Why built: External links should not trap the user inside a WebView with no address bar or back stack.
- Design: In shouldOverrideUrlLoading, allowlist the app's own hosts plus known identity providers; hand everything else to an ACTION_VIEW intent.
- Got right: The allowlist correctly covered the primary site and the obvious identity providers.
- Where/why it failed: The check did not distinguish a link the user TAPPED from a redirect. A sign-in is a redirect chain, so the first hop through any host not on the list ejected the flow into the system browser, where it completed against a DIFFERENT COOKIE JAR while the WebView sat on a dead page. No allowlist can be complete enough to fix this, because the failure is the interception itself.
- Fix: Externalise only when `request.hasGesture()` and not `request.isRedirect()`. Redirects always stay in the WebView. Separately, handle onCreateWindow so sign-in popups are adopted into the same WebView rather than silently dropped.
- Why this fix: A redirect is a step inside a flow someone else is driving; only a user gesture expresses intent to leave. Gating on gesture is a property of the navigation, so it does not rot as third-party hosts change.
- Rule of thumb: In an embedded browser, only a user-initiated, non-redirect navigation may leave the app. Allowlisting hosts against a redirect chain is unwinnable — and a flow that completes in another cookie jar looks identical to one that failed.
- Provenance (verified/assumed): Verified first-hand: sign-in failed before the change and completed after it on a real device. Assumed: that the redirect ejection was the sole cause, since the popup handler landed in the same change.
- Composed: N/A
- Link: session https://claude.ai/code/session_01BULysvkcqu6CQJYt48xFzn

## E1 — an embedded browser auth block is a security control
- Date: 2026-08-30
- Project: Pappydapimp69/Chat
- Tags: [browser][webview][auth]
- What: A federated identity provider refused sign-in inside an embedded WebView with HTTP 400 disallowed_useragent. The reflex fix is to strip the WebView marker from the user-agent so the app presents as the underlying browser.
- Why built: The app embeds a logged-in site so the user rides an existing subscription instead of a metered API key, which requires signing in inside the WebView.
- Design: Present the underlying browser build in the user-agent for general site compatibility.
- Got right: The user-agent adjustment is legitimate for compatibility — many sites serve degraded content to the embedded marker.
- Where/why it failed: It does not defeat the auth block, and escalating until it did would have been the actual mistake. The block is an anti-phishing control: a host app can read what is typed into its own WebView, so the provider refuses to render a password field there. Treating it as a compatibility bug frames a security boundary as an obstacle.
- Fix: Stop. Use the site's own email/code sign-in inside the WebView, which carries no such restriction, and detect the specific 400 to say so in the UI instead of showing a blank error.
- Why this fix: It reaches the same end state without weakening anyone's account security, and it is stable — an evasion is an arms race that breaks on the provider's schedule, silently, in the field.
- Rule of thumb: When an auth provider refuses an embedded browser, that is a control protecting the user from the app doing the asking, not a compatibility gap. Route around it via an auth method that permits embedding; never escalate impersonation until it passes.
- Provenance (verified/assumed): Verified first-hand: the 400 reproduced on a real device with the user-agent already adjusted, and email sign-in succeeded on the same build.
- Composed: N/A
- Link: session https://claude.ai/code/session_01BULysvkcqu6CQJYt48xFzn

