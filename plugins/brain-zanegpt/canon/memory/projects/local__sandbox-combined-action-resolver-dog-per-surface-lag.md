# local/sandbox-combined-action-resolver-dog-per-surface-lag — lessons

Project: local/sandbox-combined-action-resolver-dog-per-surface-lag. Newest first.

---

## E1 — sandbox combined action resolver dog per surface lag
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-dog-per-surface-lag
- Tags: [ui][input][state][gamedev][testing]
- What: Sandbox of one shared action resolver feeding several input surfaces (keyboard, gamepad, touch) that each have their own hint-to-press lag, checking where the hint-fix conversion cost lands.
- Why built: dog#E20 routes every surface through one resolver and dog#E27 warns surfaces are independent listeners; the hint-fix lesson only measured a single lag, so the multi-surface case was untested.
- Design: Deterministic, no RNG: state = (t // 5) % 4 over 600 ticks; surfaces at lag 0/1/2 (keyboard/gamepad/touch); each policy (re-resolve, token-validate, frozen hint) counts its own failures per surface; then two what-ifs: touch lag cut to 0, and every surface forced to the worst lag.
- Got right: Per surface the count is the recorded law (0/120/240 of 600), identical across all three policies, so the single resolver does not hide lag: total 360 failures, all on the laggy surfaces.
- Where/why it failed: A shared, uniform lag is a worse fix than nothing: forcing every surface to the worst lag raises the total from 360 to 720 because the zero-lag keyboard now fails 240 too. Fixing only the worst surface's lag drops the total to 120.
- Fix: Measure lag and failures per surface, then cut the worst surface's lag; do not synchronise surfaces to a common delay and do not rely on the policy choice, which changes nothing in the count.
- Why this fix: Failures are additive over surfaces and linear in each surface's own lag, so the total falls fastest by removing lag where it is largest and rises whenever a fast surface is slowed.
- Rule of thumb: A single-chokepoint resolver gives consistent decisions, not consistent timing; assert the per-surface failure count in a lag sweep and fix the slowest surface first, never equalise upward.
- Provenance (verified/assumed): Verified first-hand by running the sandbox at ~/brainwork/sb/s4.py; the numbers are its observed output. Real device latencies were not measured.
- Composed: dog/E20, dog/E27, sandbox-combined-action-resolver-dog-hint-fix-converts-mismatch/E1
- Link: scheduled training pass 3, session_01NomGdXQGCMAr6o2dzv6Tp2
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-dog-per-surface-lag-aliasing-ranking.md#E1 · compatible · no sandbox · session_01AJo9NVvaQuzD3JbJDk6P3B
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-dog-per-surface-lag-period-sweep.md#E1 · compatible · no sandbox · session (scheduled brain train pass 1)
- Cited-by: 2026-09-29 · projects/local__sandbox-lag-aliasing-ranking-p7-p11.md#E1 · compatible · no sandbox · session_012dXvqZTw6GRKUoDHUaZ6HP
- Cited-by: 2026-09-29 · projects/local__sandbox-sync-to-worst-lag-rule-fails-across-cycle.md#E1 · compatible · no sandbox · session_012dXvqZTw6GRKUoDHUaZ6HP
- Cited-by: 2026-09-29 · projects/pappydapimp69__brain.md#E61 · compatible · no sandbox · session https://claude.ai/code/session_01CHKxy8KkvpqUvfaWw1qb3v
- Cited-by: 2026-09-30 · projects/pappydapimp69__brainwork.md#E5 · compatible · no sandbox · session https://claude.ai/code/session_01F9aR1eawRNLN9c3sNEJ6Sd
