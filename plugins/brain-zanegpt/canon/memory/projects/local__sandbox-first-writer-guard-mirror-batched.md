# local/sandbox-first-writer-guard-mirror-batched — lessons

Project: local/sandbox-first-writer-guard-mirror-batched. Newest first.

---

## E1 — first writer guard mirror of no guard batched
- Date: 2026-09-29
- Project: local/sandbox-first-writer-guard-mirror-batched
- Tags: [ui][state][architecture][testing]
- What: Second independent re-check of the priority-guard lessons, with a compact 3-handler model across all 6 registration orders, comparing no guard, first-writer guard and priority guard, each with immediate and batched render.
- Why built: The mirror-image claim between no guard and first-writer guard, and the batching claim, each had one source; a smaller model checks them from a different angle and combines both.
- Design: Deterministic Python, no RNG or timing. Handlers A/B/C with priority 3/2/1; each also fires a side effect. Metrics: orders with wrong final view, wrong frames shown, stray effects from non-winners, plus fixtures where order equals priority and where order is reversed.
- Got right: No guard and first-writer guard both end wrong in 4/6 orders (mirror images, last versus first writer); priority guard is 0/6. Reverse-order fixture: first-writer wrong 1/1, no guard right 1/1. Batching cuts wrong frames 12 to 4 (unguarded) and 6 to 0 (priority guard), but stray effects stay 12 in every mode.
- Where/why it failed: A first-writer guard looks fine in a fixture where handler order equals priority (0/1 wrong) yet fails whenever order differs; batching never touches effects.
- Fix: Make the guard compare priority, or better resolve the winner before dispatch, and sweep all registration orders in the test while asserting effect counts as well as frames.
- Why this fix: Order-invariant arbitration passes every permutation; a single fixture order or a visual check can pass by coincidence.
- Rule of thumb: A guard that passes in one handler order proves nothing; sweep every order and assert effects, since batched rendering only hides flicker.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; all numbers are observed output over 6 permutations.
- Composed: sandbox-combined-action-resolver-waiting-city-priority-consulting-guard/E1, sandbox-combined-action-resolver-waiting-city-batched-render-hides-flicker-not-effects/E1, sandbox-combined-action-resolver/E1
- Link: brain train pass 2 session

