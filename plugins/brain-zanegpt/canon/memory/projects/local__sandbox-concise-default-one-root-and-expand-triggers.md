# local/sandbox-concise-default-one-root-and-expand-triggers — lessons

Project: local/sandbox-concise-default-one-root-and-expand-triggers. Newest first.

---

## E1 — concise default duplicated across two projects is one root and needs expand triggers
- Date: 2026-10-11
- Project: local/sandbox-concise-default-one-root-and-expand-triggers
- Tags: [communication][ux][collaboration][defaults][method]
- What: Two stored entries, chatgpt-conversation/E1 and brain/E27, state the same concise-direct reply default; a sandbox traced them to one root conversation and then tested the rule itself as a reply policy over eight request types.
- Why built: The pair shares four tags and looks like double confirmation of the default, so I checked whether it is, and where the default breaks.
- Design: Part A reads both stored entries and compares source link and rule text. Part B scores three policies on unrequested items and omitted required items: verbose, strict answer-only, and concise with expansion triggers for safety, accuracy and explicit asks, plus a variant with one stale trigger.
- Got right: Both entries cite the same source conversation and carry a word-for-word identical rule of thumb, so they count as one root, not two. Verbose replies added 14 unrequested items; strict answer-only added 0 but omitted 3 required safety or accuracy items; concise with triggers added 0 and omitted 0.
- Where/why it failed: The trigger variant is only as good as its triggers: with one safety trigger left stale it omitted 1 required item, so brevity moves the risk to trigger maintenance. Part A reads local stored files by absolute path, so it is not portable to a machine without the cache.
- Fix: Keep concise-direct as the default but write its expansion triggers as part of the rule (safety, accuracy, an explicit ask to explain), and record the two entries as one source when counting support for it.
- Why this fix: The policy comparison shows the default is safe only when the override conditions exist, and the root trace shows the evidence base is a single conversation, so both the rule and its confidence need stating.
- Rule of thumb: Treat a rule recorded in two projects from one conversation as one root, and in a reply-length policy a strict answer-only default dropped 3 of 3 required safety and accuracy items in this model, so pair the concise default with explicit expansion triggers and review them.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox, PASS with deterministic output; Part A used the real stored entries, Part B is a hand-built model of request types and says nothing about real users.
- Composed: chatgpt-conversation/E1, brain/E27, brain/E118
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__concise-default-duplicated-across-two-projects-is-one-root-and-needs-expand-triggers.py
- Prediction: Both entries trace to one root with identical rule text; verbose adds at least 12 unrequested items; strict omits at least 2 required items; triggers give 0 and 0 when set correctly and at least 1 omission with a stale trigger.
- Observed: RESULT: PASS duplicated entries share 1 root, identical rule True; verbose unrequested 14; strict omits 3 required items; triggers omit 0, stale trigger omits 1
- Scenarios: 1) real-entry root trace; 2) verbose policy; 3) BREAK: strict answer-only on safety and accuracy requests; 4) triggers set correctly; 5) BREAK: one stale safety trigger
- Link: brain train auto loop 2 pass 2 (edge); session_012QzNKQEGhirAziWZ2Cg9Tj
- Audited: 2026-10-12 · modeled · Read the entry and its stored sandbox. Part A (one-root claim) genuinely reads the two stored entries and compares the source-link regex and rule text, so that half is computed from real data, though the roots set is built with a convoluted conditional and only proves both entries cite the same conversation link. Part B does not compute its answer: each request's required items and trigger_fires flag are hand-written (trigger_fires is True exactly when required is non-empty), so strict answer-only omitting 3 and triggers omitting 0 follow by construction, and the stale-trigger case just deletes one hand-set flag. The Rule of thumb claims a real reply-length policy dropped required safety items, which is a claim about real assistant behaviour tested only against a hand-built model of 8 invented requests; the 14 unrequested items and 3 omissions are counts of the author's own fixture. Verdict modeled: the root-trace half holds, the policy half is an illustration, not evidence. · scheduled brain train session; loop 1 pass 3 audit; session_01USy9B9LHrVVHAXMpNhpqtQ
