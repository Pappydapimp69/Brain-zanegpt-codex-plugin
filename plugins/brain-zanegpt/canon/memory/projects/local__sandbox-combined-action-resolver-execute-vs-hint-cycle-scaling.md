# local/sandbox-combined-action-resolver-execute-vs-hint-cycle-scaling — lessons

Project: local/sandbox-combined-action-resolver-execute-vs-hint-cycle-scaling. Newest first.

---

## E1 — sandbox combined action resolver execute vs hint cycle scaling
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-execute-vs-hint-cycle-scaling
- Tags: [ui][state][architecture][input][testing]
- What: Independent re-model of the execute-time-resolve versus hint-fidelity tradeoff, built from two boundary kinds per cycle and swept over lag and cycle length.
- Why built: The recorded 520/440/280 and 40/80/160 numbers came from one sandbox; a differently structured model tests whether the tradeoff is real and how it scales.
- Design: Deterministic, no RNG: 600 ticks; kind A boundary (role validity flips) once per cycle, kind B boundary (priority flips, role stays valid) once per cycle; hint is the best context at t, press lands at t+lag; compared execute-time resolve with a frozen hint. Cycles 15 and 20, lags 0/1/2/4.
- Got right: Cycle 15 reproduces the recorded numbers exactly: execute-time stays rule-valid 600/600 while matching the shown hint 600/520/440/280, and the frozen hint executes a lapsed role 0/40/80/160 at lag 0/1/2/4.
- Where/why it failed: The figures are not universal: at cycle 20 the hint match is 600/540/480/360 and lapsed executions are 0/30/60/120, so both violations scale with lag over cycle length.
- Fix: Model hint mismatch as N times 2 times lag over cycle (both boundary kinds count) and lapsed frozen executions as N times lag over cycle (only role-changing boundaries); test at two cycle lengths and count both violation types per lag.
- Why this fix: Execute-time resolve trades hint fidelity for rule validity one for one at every boundary inside the lag window, so the fair metric is the pair of counts, and the only free lever is a shorter lag or a longer cycle.
- Rule of thumb: Never report one of execute-time validity or hint match alone; sweep lag and cycle length, and expect the hint-mismatch rate to be the sum over all boundary kinds while lapsed executions count only the role-changing ones.
- Provenance (verified/assumed): Verified first-hand by running the sandbox at ~/brainwork/sb/s3.py; all figures quoted are its observed output. Real frame timing was not modelled.
- Composed: sandbox-combined-action-resolver-dog-stale-hint-press-lag/E1, sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint/E1, sandbox-combined-action-resolver/E1
- Link: scheduled training pass 2, session_01NomGdXQGCMAr6o2dzv6Tp2
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-age-tag-staleness.md#E1 · compatible · no sandbox · session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-age-vs-validity.md#E1 · compatible · no sandbox · session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-hint-lag-full-cycle-sweep.md#E1 · compatible · no sandbox · session (scheduled brain train pass 5)
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-lapse-periodic.md#E1 · compatible · no sandbox · session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-29 · projects/local__sandbox-execute-resolve-conserves-mismatch.md#E1 · compatible · no sandbox · session_012dXvqZTw6GRKUoDHUaZ6HP
- Cited-by: 2026-09-29 · projects/pappydapimp69__brain.md#E62 · compatible · no sandbox · session https://claude.ai/code/session_01CHKxy8KkvpqUvfaWw1qb3v
- Cited-by: 2026-09-30 · projects/pappydapimp69__brainwork.md#E2 · compatible · no sandbox · session https://claude.ai/code/session_01F9aR1eawRNLN9c3sNEJ6Sd
