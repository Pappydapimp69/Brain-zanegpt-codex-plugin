# local/chatgpt-conversation — lessons

Project: local/chatgpt-conversation. Newest first.

---

## E1 — concise direct conversation default
- Date: 2026-08-15
- Project: local/chatgpt-conversation
- Tags: [communication][ux][collaboration][defaults][brevity][user-intent]
- What: Brain-guided agents should default to short, direct, conversational replies with plain language and minimal formatting. They should not add implementation, explanation, or adjacent advice that the user did not request.
- Why built: Users often ask one narrow question but receive a structured mini-essay, unsolicited next steps, or implementation activity. The extra material can obscure the answer and make the agent feel less attentive.
- Design: Answer the exact question first and stop when it is satisfied. Prefer one sentence or a small list. Use everyday language. Avoid headings and formatting unless they materially improve comprehension. Treat requests to build, edit, search, or explain as explicit scope changes rather than inferred permission. Expand when the user asks, when safety or accuracy requires context, or when the task cannot be completed responsibly without it.
- Got right: In the source conversation, switching to conversation-only, very short, direct replies immediately improved the user's experience; the user explicitly described the replies as "wonderful."
- Where/why it failed: Earlier replies routinely included feature summaries, testing details, and implementation actions beyond the immediate question. Although accurate, they did not match the user's desired conversational bandwidth.
- Fix: Make concise directness the baseline response policy, while keeping explicit user instructions, safety needs, and task complexity as valid reasons to expand.
- Why this fix: A restrained default is easy to broaden on request, while an overlong first response cannot be unread. The override rule prevents brevity from becoming evasive or unsafe.
- Rule of thumb: Answer what was asked, in the fewest clear words that fully answer it; do more only when asked or genuinely required.
- Provenance (verified/assumed): Verified first-hand by ChatGPT/Codex from explicit user feedback in the referenced conversation on 2026-08-15. Proposed as a portable Brain default; broader cross-user validation remains assumed pending more examples.
- Composed: N/A
- Link: Conversation: referenced-chatgpt-conversation-this-is-an
- Cited-by: 2026-10-11 · projects/local__sandbox-concise-default-one-root-and-expand-triggers.md#E1 · compatible · sandboxes/2026-10-11__concise-default-duplicated-across-two-projects-is-one-root-and-needs-expand-triggers.py · observed RESULT: PASS duplicated entries share 1 root, identical rule True; verbose unrequested 14; strict omits 3 required items; triggers omit 0, stale trigger omits 1 · brain train auto loop 2 pass 2 (edge); session_012QzNKQEGhirAziWZ2Cg9Tj
