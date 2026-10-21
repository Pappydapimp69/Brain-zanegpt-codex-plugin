# local/sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint — lessons

Project: local/sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint. Newest first.

---

## E1 — sandbox combined action resolver execution time resolve vs stale hint
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint
- Tags: [ui][state][architecture][input][testing]
- What: sandbox-combined-action-resolver/E1 says resolve the role again at execution time, and sandbox-combined-action-resolver-dog-stale-hint-press-lag/E1 says the shown hint then disagrees with the press. Composed, they force a choice between rule-correct effects and hint-faithful effects once there is any lag.
- Why built: Each lesson is right alone; the two prescriptions pull in opposite directions and no entry priced the trade.
- Design: Deterministic 600-tick model of one entity with roles A (always available) and B (higher priority, available only in the first of every three 5-tick state blocks). Hint is the priority resolve at tick t; press lands at t plus lag, lag swept 0/1/2/4. Policy X resolves at press time; policy Y executes the frozen hint.
- Got right: At lag 0 both policies score 600 of 600 on both measures, so any divergence is caused by lag alone.
- Where/why it failed: Execution-time resolve stays rule-valid 600 of 600 but matches the shown hint only 520/440/280 at lag 1/2/4. Frozen hint always matches the hint but executes a role no longer available on 40/80/160 presses (rule-valid 560/520/440).
- Fix: Choose per action which invariant is binding: use execution-time resolve when the rules must hold, and when the hint must be honoured, re-validate availability at press and reject rather than execute a role that lapsed.
- Why this fix: The two invariants (effect valid under current rules, effect equals what was promised) coincide only at lag 0, so a design that claims both without a lag bound is unfalsified rather than correct.
- Rule of thumb: When one lesson says re-resolve late and another says keep the UI consistent, sweep the input lag and report both violation counts; do not accept either alone.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session; all counts above are observed output from the run.
- Composed: sandbox-combined-action-resolver/E1, sandbox-combined-action-resolver-dog-stale-hint-press-lag/E1, dog/E20
- Link: session https://claude.ai/code/session_01VDpEDT2ry2U1WXLUnGqdYD
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-execute-vs-hint-cycle-scaling.md#E1 · compatible · no sandbox · scheduled training pass 2, session_01NomGdXQGCMAr6o2dzv6Tp2
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint-window-cycles.md#E1 · compatible · no sandbox · session (scheduled brain train pass 2)
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-hybrid-fallback.md#E1 · compatible · no sandbox · session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-30 · projects/local__sandbox-hybrid-residual-identity-across-window-shapes.md#E1 · compatible · no sandbox · session_01AfTzT5iniwzFpQZUQQxJ7F
- Cited-by: 2026-09-29 · projects/pappydapimp69__brain.md#E62 · compatible · no sandbox · session https://claude.ai/code/session_01CHKxy8KkvpqUvfaWw1qb3v
- Cited-by: 2026-09-30 · projects/pappydapimp69__brainwork.md#E4 · compatible · no sandbox · session https://claude.ai/code/session_01F9aR1eawRNLN9c3sNEJ6Sd
