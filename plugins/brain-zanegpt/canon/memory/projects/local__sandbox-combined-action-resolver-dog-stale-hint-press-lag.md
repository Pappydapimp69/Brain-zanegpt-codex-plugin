# local/sandbox-combined-action-resolver-dog-stale-hint-press-lag — lessons

Project: local/sandbox-combined-action-resolver-dog-stale-hint-press-lag. Newest first.

---

## E1 — sandbox combined action resolver dog stale hint press lag
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-dog-stale-hint-press-lag
- Tags: [ui][gamedev][state][input][testing]
- What: A sandbox re-verifying dog#E20's single action-resolver from a new angle: the hint renderer and the press handler both call the SAME resolver, but at different ticks (press lands `lag` ticks after the hint was drawn).
- Why built: dog#E31 claims one resolver cannot desync its two callers; action-resolver#E1 says resolve again at execution time. Both assume the two calls see the same state.
- Design: Deterministic model, no RNG: verbs talk/pet/sit whose availability cycles with period 5 ticks; resolver picks highest priority available verb. 600 ticks, lag swept 0,1,2,4; three press policies: re-resolve at press, execute the token the hint showed, execute the token only if still valid.
- Got right: At lag 0 all policies agree with the hint (0/600 mismatches), so an isolated same-tick resolver test passes.
- Where/why it failed: With any lag, re-resolve at press differs from the shown hint 120/240/480 of 600 (lag 1/2/4, i.e. lag/period); a valid-only token policy no-ops the same share of presses (80/160/320); the token policy executes a now-invalid verb 80/160/320 times.
- Fix: Treat shared-resolver agreement as true only within one tick; pick an explicit stale-hint policy (freeze hint for a min-visible time so state cannot flip under it, or execute token with validity check and visible no-op) and test with nonzero hint-to-press lag.
- Why this fix: Sharing code removes logic drift but not temporal drift; the mismatch rate scales as lag over state-change period, so freezing the hint for longer than the lag drives it to zero.
- Rule of thumb: A single resolver guarantees hint and effect agree only at the same instant; sweep hint-to-press lag in the test, since lag 0 is green while lag/period of presses misfire.
- Provenance (verified/assumed): Verified first-hand by running the sandbox script; numbers above are the observed output of the run. The frozen-hint fix was reasoned from the lag/period rate, not separately run.
- Composed: dog/E20, dog/E31, sandbox-combined-action-resolver/E1
- Link: brain train pass 1, 2026-09-29
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-dog-hint-fix-converts-mismatch.md#E1 · compatible · no sandbox · session https://claude.ai/code/session_01VDpEDT2ry2U1WXLUnGqdYD
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-execute-vs-hint-cycle-scaling.md#E1 · compatible · no sandbox · scheduled training pass 2, session_01NomGdXQGCMAr6o2dzv6Tp2
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint.md#E1 · compatible · no sandbox · session https://claude.ai/code/session_01VDpEDT2ry2U1WXLUnGqdYD
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-hint-lag-period-scaling.md#E1 · compatible · no sandbox · scheduled training pass 1, session_01NomGdXQGCMAr6o2dzv6Tp2
- Cited-by: 2026-09-30 · projects/local__sandbox-hybrid-fallback-three-verb-dog-resolver.md#E1 · compatible · no sandbox · session_01AfTzT5iniwzFpQZUQQxJ7F
- Cited-by: 2026-09-29 · projects/pappydapimp69__brain.md#E62 · compatible · no sandbox · session https://claude.ai/code/session_01CHKxy8KkvpqUvfaWw1qb3v
- Cited-by: 2026-09-30 · projects/pappydapimp69__brainwork.md#E3 · compatible · no sandbox · session https://claude.ai/code/session_01F9aR1eawRNLN9c3sNEJ6Sd
