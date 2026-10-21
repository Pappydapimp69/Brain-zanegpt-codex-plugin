# local/sandbox-modal-priority-guard-order-permutations — lessons

Project: local/sandbox-modal-priority-guard-order-permutations. Newest first.

---

## E1 — modal priority guard order permutations
- Date: 2026-09-29
- Project: local/sandbox-modal-priority-guard-order-permutations
- Tags: [ui][state][architecture][testing]
- What: Independent re-check of two claims (a priority guard is not retroactive; batched render hides flicker but not side effects) using all 6 registration orders of 3 handlers (prio 3/2/1) instead of one fixed order.
- Why built: Existing lessons were single-source; a different model (exhaustive order permutations, counts over 6 orders) tests whether they hold independent of a particular handler order.
- Design: Deterministic Python, no RNG or timing. Modes: naive, guard on view write only, guard on whole handler, each immediate or batched render, plus resolve-winner-before-dispatch. Metrics: final view correct, frames showing a wrong modal, side effects fired by non-winners.
- Got right: Both claims reproduce. Guard-on-view gives final correct 6/6 but wrong frames 6 and stray effects 12; batching cuts wrong frames to 0 but stray effects stay 12 (whole-handler guard: 5). Resolve-before-dispatch gives 0/0/0 across all orders.
- Where/why it failed: Naive dispatch is order dependent: final view correct only 2/6 orders. A guard fixes the end state but is blind to handlers that already ran earlier in the order.
- Fix: Compute the winning role once before dispatch, then run only the winner's handler and one render.
- Why this fix: Removes order dependence entirely, so no flicker and no stray effects regardless of registration order, unlike guards or batching that only mask one symptom.
- Rule of thumb: Test priority arbitration across every handler registration order and assert effects and frames, not just the final view; arbitrate before dispatch rather than guarding inside handlers.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; numbers above are observed output over 6 permutations.
- Composed: sandbox-combined-action-resolver-waiting-city-batched-render-hides-flicker-not-effects/E1, sandbox-combined-action-resolver-waiting-city-guard-cannot-be-retroactive/E1
- Link: brain train pass 1 session

