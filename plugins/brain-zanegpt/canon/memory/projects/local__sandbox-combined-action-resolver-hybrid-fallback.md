# local/sandbox-combined-action-resolver-hybrid-fallback — lessons

Project: local/sandbox-combined-action-resolver-hybrid-fallback. Newest first.

---

## E1 — sandbox hybrid resolve fallback hint
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-hybrid-fallback
- Tags: [ui][input][state][gamedev][testing]
- What: Sandbox of a third press policy for the shared action resolver: execute the hinted action if it is still available at press time, otherwise re-resolve, compared with pure execute-time resolve and the frozen hint.
- Why built: The execute-time-resolve versus stale-hint lesson rests on a two-policy choice and one source, so a hybrid was the untested angle that could soften the tradeoff.
- Design: Deterministic, no RNG, 600 ticks. Role B (higher priority) is available for the first 5 of every 15 ticks, role A always. The hint is the priority resolve at tick t and the press lands at t plus lag, lag swept 0/1/2/4. Counted rule-valid presses and presses matching the hint per policy.
- Got right: Hybrid stays rule-valid on 600 of 600 at every lag while matching the hint on 560/520/440 at lag 1/2/4, against 520/440/280 for pure execute-time resolve. Frozen hint matches 600 but is rule-valid on only 560/520/440. All three score 600 and 600 at lag 0.
- Where/why it failed: Hybrid still cannot match the hint on every press above lag 0, since a hint of B that has expired must be replaced; the gap to 600 (40/80/160) equals the frozen policy's invalid executions exactly.
- Fix: Use hint-first with a validity check and a re-resolve fallback at press time, and report both counts, valid and hint-matching, in the lag sweep.
- Why this fix: The hint only conflicts with the rules on presses where it has expired, so keeping it elsewhere recovers every press that the pure re-resolve throws away while keeping full rule validity.
- Rule of thumb: When re-resolve-late and keep-the-hint disagree, try hint-first with a validity fallback; it dominates pure re-resolve on hint fidelity, and its residual mismatch equals the frozen policy's invalid count.
- Provenance: Verified first-hand by running the Python sandbox (sb/p1.py) and observing the counts listed above; a real input pipeline was outside the sandbox.
- Composed: sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint/E1, sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint-window-cycles/E1, dog/E20
- Link: session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-30 · projects/local__sandbox-age-gate-vs-validity-fallback-tradeoff.md#E1 · compatible · no sandbox · session_01AfTzT5iniwzFpQZUQQxJ7F
- Cited-by: 2026-09-30 · projects/local__sandbox-age-gated-fallback-aperiodic-waveform.md#E1 · compatible · no sandbox · session_01AfTzT5iniwzFpQZUQQxJ7F
- Cited-by: 2026-09-30 · projects/local__sandbox-age-plus-validity-combined-policy-cost.md#E1 · compatible · no sandbox · session_01AfTzT5iniwzFpQZUQQxJ7F
- Cited-by: 2026-09-30 · projects/local__sandbox-hybrid-fallback-age-validity-fidelity-ladder.md#E1 · compatible · sandboxes/2026-09-30__hybrid-fallback-age-validity-fidelity-ladder.py · observed RESULT: PASS pure 520/440/280, hybrid 560/520/440, gap=frozen invalid=40*lag, age+validity keeps 0 hints at lag>0 · scheduled brain train pass 4
- Cited-by: 2026-09-30 · projects/local__sandbox-hybrid-fallback-follows-mismatch-curve.md#E1 · compatible · no sandbox · session
- Cited-by: 2026-09-30 · projects/local__sandbox-hybrid-fallback-three-verb-dog-resolver.md#E1 · compatible · no sandbox · session_01AfTzT5iniwzFpQZUQQxJ7F
- Cited-by: 2026-09-30 · projects/local__sandbox-hybrid-residual-identity-across-window-shapes.md#E1 · compatible · no sandbox · session_01AfTzT5iniwzFpQZUQQxJ7F
