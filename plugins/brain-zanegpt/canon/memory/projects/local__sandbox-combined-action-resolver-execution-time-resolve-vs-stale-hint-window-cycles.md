# local/sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint-window-cycles — lessons

Project: local/sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint-window-cycles. Newest first.

---

## E1 — sandbox exec vs hint single window cycles
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint-window-cycles
- Tags: [ui][state][architecture][input][testing]
- What: Re-verified the execute-time-resolve versus hint-fidelity tradeoff for the shared action resolver using a single-window action (valid for W ticks of each cycle) at cycle 9 window 3 and cycle 13 window 6, instead of the earlier multi-role cycles.
- Why built: The tradeoff had one supporting sandbox shape, so the edge to dog's shared resolver was single-source and needed a structurally different check.
- Design: Deterministic, no RNG, 600 ticks. The hint shows the state from lag ticks earlier. A frozen-hint policy executes the hinted action on press and a press is lapsed if the action is no longer valid. The execute-time policy re-resolves at press.
- Got right: Execute-time resolve stayed rule-valid on 600 of 600 presses at every lag. At lag 1/2/4 it matched the hint on 467/334/201 (P9 W3) and 508/416/234 (P13 W6). Frozen-hint lapsed executions were 67/134/201 and 46/92/184.
- Where/why it failed: Neither policy holds both properties above lag 0. Hint mismatch is about twice the lapsed count because it sums rise and fall boundaries; at P9 lag 4 the counts are 399 against 201, so the ratio is not exact.
- Fix: Count both violations in a lag sweep and either re-validate and reject at press or shrink the lag itself, rather than choosing one policy and declaring the mismatch solved.
- Why this fix: The two violations are the same boundary crossings viewed from the hint side and the press side, so a policy can only choose which one becomes visible.
- Rule of thumb: Above zero lag a shared resolver cannot give both a truthful hint and a valid press; sweep lag over more than one cycle shape and report both counts.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; all counts above are observed output. Not checked against a real game loop.
- Composed: local/sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint/E1, dog/E20
- Link: session (scheduled brain train pass 2)
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-hybrid-fallback.md#E1 · compatible · no sandbox · session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-30 · projects/local__sandbox-hybrid-residual-identity-across-window-shapes.md#E1 · compatible · no sandbox · session_01AfTzT5iniwzFpQZUQQxJ7F
- Cited-by: 2026-09-30 · projects/pappydapimp69__brainwork.md#E4 · compatible · no sandbox · session https://claude.ai/code/session_01F9aR1eawRNLN9c3sNEJ6Sd
